
import os
from functools import wraps
from datetime import datetime, date
from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    render_template,
    redirect,
    url_for,
    send_file,
    session,
    abort,
)
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session
from jinja2 import TemplateNotFound
from models import Base, Partner, Brand, Store, Connection, ReportEntry, ReceiptImage, User
from export_utils import ExportManager

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "disagua.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["JSON_AS_ASCII"] = False
    app.config["JSON_SORT_KEYS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

    default_frontend_origins = {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    }
    configured_origins = {
        origin.strip()
        for origin in os.environ.get("FRONTEND_ORIGINS", "").split(",")
        if origin.strip()
    }
    allowed_origins = list(default_frontend_origins | configured_origins) or None

    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {"origins": allowed_origins},
            r"/login": {"origins": allowed_origins},
            r"/logout": {"origins": allowed_origins},
        },
    )

    app.secret_key = 'change-me'

    def frontend_build_available():
        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        return os.path.isfile(index_file)

    def render_frontend_or_template(template_name, **context):
        if frontend_build_available():
            return send_from_directory(FRONTEND_DIST_DIR, "index.html")
        try:
            return render_template(template_name, **context)
        except TemplateNotFound:
            messages = []
            if context.get("error"):
                messages.append(str(context["error"]))
            if context.get("success"):
                messages.append(str(context["success"]))
            if not messages:
                messages.append("Interface web indisponível. Compile o frontend React (frontend/dist).")
            return app.response_class("\n".join(messages), mimetype="text/plain")

    if os.path.isdir(FRONTEND_DIST_DIR):
        @app.get("/assets/<path:filename>")
        def frontend_assets(filename):
            if not frontend_build_available():
                return abort(404)
            assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
            return send_from_directory(assets_dir, filename)

        @app.get("/favicon.svg")
        def frontend_favicon():
            if not frontend_build_available():
                return abort(404)
            return send_from_directory(FRONTEND_DIST_DIR, "favicon.svg")

    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    Base.metadata.create_all(engine)

    def ensure_schema(conn_engine):
        with conn_engine.begin() as conn:
            def ensure_column(table, column, ddl):
                existing = {row._mapping["name"] for row in conn.execute(text(f"PRAGMA table_info({table})"))}
                if column not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))

            ensure_column("partners", "dia_pagamento", "INTEGER")
            ensure_column("partners", "banco", "VARCHAR")
            ensure_column("partners", "agencia_conta", "VARCHAR")
            ensure_column("partners", "pix", "VARCHAR")

    ensure_schema(engine)
    Session = scoped_session(sessionmaker(bind=engine, autoflush=False, future=True))

    partner_fields = {
        "cidade", "estado", "parceiro", "distribuidora", "cnpj_cpf", "telefone", "email",
        "dia_pagamento", "banco", "agencia_conta", "pix",
        "cx_copo", "dez_litros", "vinte_litros", "mil_quinhentos_ml", "vasilhame"
    }
    partner_float_fields = {"cx_copo", "dez_litros", "vinte_litros", "mil_quinhentos_ml", "vasilhame"}
    partner_required = {"cidade", "estado", "parceiro", "cnpj_cpf", "telefone"}

    def parse_partner_payload(data):
        payload = {}
        for field in partner_fields:
            if field not in data:
                continue
            value = data[field]
            if isinstance(value, str):
                value = value.strip()
            if field in partner_float_fields:
                if value in (None, ""):
                    payload[field] = 0.0
                else:
                    try:
                        payload[field] = float(value)
                    except (TypeError, ValueError):
                        raise ValueError(f"Campo '{field}' deve ser numérico.")
            elif field == "dia_pagamento":
                if value in (None, ""):
                    payload[field] = None
                else:
                    try:
                        payload[field] = int(value)
                    except (TypeError, ValueError):
                        raise ValueError("Campo 'dia_pagamento' deve ser um número inteiro.")
            else:
                payload[field] = value if value != "" else None
        return payload

    def serialize_partner(record):
        total = sum(
            value or 0
            for value in (
                record.cx_copo,
                record.dez_litros,
                record.vinte_litros,
                record.mil_quinhentos_ml,
                record.vasilhame,
            )
        )
        return {
            "id": record.id,
            "cidade": record.cidade,
            "estado": record.estado,
            "parceiro": record.parceiro,
            "distribuidora": record.distribuidora,
            "cnpj_cpf": record.cnpj_cpf,
            "telefone": record.telefone,
            "email": record.email,
            "dia_pagamento": record.dia_pagamento,
            "banco": record.banco,
            "agencia_conta": record.agencia_conta,
            "pix": record.pix,
            "cx_copo": record.cx_copo,
            "dez_litros": record.dez_litros,
            "vinte_litros": record.vinte_litros,
            "mil_quinhentos_ml": record.mil_quinhentos_ml,
            "vasilhame": record.vasilhame,
            "total": total,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }

    def serialize_brand(record):
        return {
            "id": record.id,
            "marca": record.marca,
            "cod_disagua": record.cod_disagua,
            "store_count": len(record.stores),
        }

    def serialize_store(store, brand):
        return {
            "id": store.id,
            "marca_id": store.marca_id,
            "marca": brand.marca,
            "loja": store.loja,
            "cod_disagua": store.cod_disagua,
            "local_entrega": store.local_entrega,
            "endereco": store.endereco,
            "municipio": store.municipio,
            "uf": store.uf,
            "valor_20l": store.valor_20l,
            "valor_10l": store.valor_10l,
            "valor_1500ml": store.valor_1500ml,
            "valor_cx_copo": store.valor_cx_copo,
            "valor_vasilhame": store.valor_vasilhame,
        }

    store_fields = {
        "marca_id", "loja", "cod_disagua", "local_entrega", "endereco", "municipio", "uf",
        "valor_20l", "valor_10l", "valor_1500ml", "valor_cx_copo", "valor_vasilhame"
    }
    store_float_fields = {"valor_20l", "valor_10l", "valor_1500ml", "valor_cx_copo", "valor_vasilhame"}
    store_required = {"marca_id", "loja", "local_entrega", "municipio", "uf"}

    def parse_store_payload(data):
        payload = {}
        for field in store_fields:
            if field not in data:
                continue
            value = data[field]
            if isinstance(value, str):
                value = value.strip()
            if field == "marca_id":
                try:
                    payload[field] = int(value)
                except (TypeError, ValueError):
                    raise ValueError("Campo 'marca_id' deve ser numérico.")
            elif field in store_float_fields:
                if value in (None, ""):
                    payload[field] = 0.0
                else:
                    try:
                        payload[field] = float(value)
                    except (TypeError, ValueError):
                        raise ValueError(f"Campo '{field}' deve ser numérico.")
            else:
                payload[field] = value if value != "" else None
        return payload

    def normalize_required(payload, required_fields):
        missing = [field for field in required_fields if not payload.get(field) and payload.get(field) not in (0, 0.0)]
        return missing

    def success_response(data=None, *, status=200, meta=None):
        payload = {"data": data}
        if meta is not None:
            payload["meta"] = meta
        response = jsonify(payload)
        response.status_code = status
        return response

    def error_response(message, *, status=400, code=None, details=None):
        payload = {"error": {"message": message}}
        if code is not None:
            payload["error"]["code"] = code
        if details is not None:
            payload["error"]["details"] = details
        response = jsonify(payload)
        response.status_code = status
        return response

    class _LoginUser(UserMixin):
        def __init__(self, db_user):
            self.db_user = db_user
            self.id = str(db_user.id)
            self.username = db_user.username
            self._active = getattr(db_user, "is_active", True)

        @property
        def is_active(self):
            return bool(self._active)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        with Session() as s:
            u = s.get(User, int(user_id))
            return _LoginUser(u) if u else None

    def admin_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.path.startswith("/api/"):
                    return error_response("Não autenticado.", status=401, code="unauthorized")
                from flask import abort
                return abort(401)
            with Session() as s:
                u = s.get(User, int(current_user.id))
                if not u or u.role != 'admin':
                    if request.path.startswith("/api/"):
                        return error_response("Acesso restrito ao administrador.", status=403, code="forbidden")
                    from flask import abort
                    return abort(403)
            return f(*args, **kwargs)
        return wrapper

    def roles_allowed(*roles):
        """Allow only if user role in roles; admin always allowed."""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if not current_user.is_authenticated:
                    if request.path.startswith("/api/"):
                        return error_response("Não autenticado.", status=401, code="unauthorized")
                    from flask import abort
                    return abort(401)
                with Session() as s:
                    u = s.get(User, int(current_user.id))
                    if not u:
                        if request.path.startswith("/api/"):
                            return error_response("Não autenticado.", status=401, code="unauthorized")
                        from flask import abort
                        return abort(401)
                    if u.role != 'admin' and u.role not in roles:
                        if request.path.startswith("/api/"):
                            return error_response("Permissões insuficientes.", status=403, code="forbidden")
                        from flask import abort
                        return abort(403)
                return f(*args, **kwargs)
            return wrapper
        return decorator

    # ---------------------- PAGES ----------------------
    @app.get("/login")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        return render_frontend_or_template("login.html")

    @app.post("/login")
    def do_login():
        from werkzeug.security import check_password_hash, generate_password_hash
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        with Session() as s:
            u = s.query(User).filter(User.username==username).first()
            if not u:
                total = s.query(User).count()
                if total == 0 and username == "admin":
                    u = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
                    s.add(u); s.commit()
            if not u or not check_password_hash(u.password_hash, password):
                return render_frontend_or_template("login.html", error="Usuário ou senha inválidos.")
            login_user(_LoginUser(u))
            return redirect(url_for("home"))

    @app.post("/api/login")
    def api_login():
        from werkzeug.security import check_password_hash, generate_password_hash

        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "")).strip()
        password = data.get("password", "")

        if not username or not password:
            return error_response("Usuário e senha são obrigatórios.", status=400, code="invalid_credentials")

        with Session() as s:
            u = s.query(User).filter(User.username == username).first()
            if not u:
                total = s.query(User).count()
                if total == 0 and username == "admin":
                    u = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
                    s.add(u)
                    s.commit()
                    s.refresh(u)
            if not u or not check_password_hash(u.password_hash, password):
                return error_response("Usuário ou senha inválidos.", status=401, code="invalid_credentials")

            login_user(_LoginUser(u))

            return success_response({
                "user": {"id": u.id, "username": u.username, "role": u.role}
            })

    @app.get("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.post("/api/logout")
    @login_required
    def api_logout():
        logout_user()
        session.clear()
        return success_response({"ok": True})

    @app.get("/")
    @login_required
    def home():
        return render_frontend_or_template("index.html")

    @app.get("/parceiros")
    @login_required
    def page_parceiros():
        return render_frontend_or_template("parceiros.html")

    @app.get("/lojas")
    @login_required
    def page_lojas():
        return render_frontend_or_template("lojas.html")

    @app.get("/conectar")
    @login_required
    def page_conectar():
        return render_frontend_or_template("conectar.html")

    @app.get("/comprovantes")
    @login_required
    def page_comprovantes():
        return render_frontend_or_template("comprovantes.html")

    @app.get("/relatorios")
    @login_required
    def page_relatorios():
        return render_frontend_or_template("relatorios.html")

    @app.get("/account")
    @login_required
    def account():
        return render_frontend_or_template("account.html", username=current_user.username)

    @app.post("/account")
    @login_required
    def account_update():
        from werkzeug.security import check_password_hash, generate_password_hash
        current_pwd = request.form.get("current_password","")
        new_pwd = request.form.get("new_password","")
        confirm_pwd = request.form.get("confirm_password","")
        if len(new_pwd) < 6:
            return render_frontend_or_template(
                "account.html",
                username=current_user.username,
                error="A nova senha deve ter ao menos 6 caracteres.",
            )
        if new_pwd != confirm_pwd:
            return render_frontend_or_template(
                "account.html",
                username=current_user.username,
                error="A confirmação de senha não confere.",
            )
        with Session() as s:
            u = s.get(User, int(current_user.id))
            if not u or not check_password_hash(u.password_hash, current_pwd):
                return render_frontend_or_template(
                    "account.html",
                    username=current_user.username,
                    error="Senha atual incorreta.",
                )
            from werkzeug.security import generate_password_hash
            u.password_hash = generate_password_hash(new_pwd)
            s.commit()
        return render_frontend_or_template(
            "account.html",
            username=current_user.username,
            success="Senha alterada com sucesso.",
        )

    @app.get("/usuarios")
    @login_required
    @admin_required
    def users_page():
        return render_frontend_or_template("users.html")

    app.add_url_rule("/users", view_func=users_page)

    # ---------------------- APIs ----------------------
    @app.get("/api/me")
    @login_required
    def whoami():
        with Session() as s:
            u = s.get(User, int(current_user.id))
            return success_response({"id": u.id, "username": u.username, "role": u.role})

    # Partners
    @app.get("/api/partners")
    @login_required
    def get_partners():
        with Session() as s:
            rows = s.execute(select(Partner)).scalars().all()
            partners = [serialize_partner(r) for r in rows]
            return success_response(partners)

    @app.post("/api/partners")
    @login_required
    @roles_allowed("operator")
    def create_partner():
        data = request.json or {}
        try:
            payload = parse_partner_payload(data)
        except ValueError as exc:
            return error_response(str(exc))

        missing = normalize_required(payload, partner_required)
        if missing:
            return error_response(
                "Campos obrigatórios ausentes.",
                details={"missing": missing},
            )

        for field in partner_float_fields:
            payload.setdefault(field, 0.0)

        with Session() as s:
            p = Partner(**payload)
            s.add(p)
            s.commit()
            s.refresh(p)
            return success_response(serialize_partner(p), status=201)

    @app.put("/api/partners/<int:pid>")
    @login_required
    @roles_allowed("operator")
    def update_partner(pid):
        data = request.json or {}
        try:
            payload = parse_partner_payload(data)
        except ValueError as exc:
            return error_response(str(exc))

        if not payload:
            return error_response("Nenhum campo para atualizar.")

        with Session() as s:
            p = s.get(Partner, pid)
            if not p:
                return error_response("Parceiro não encontrado.", status=404, code="not_found")
            for key, value in payload.items():
                setattr(p, key, value)
            s.commit()
            s.refresh(p)
            return success_response(serialize_partner(p))

    @app.delete("/api/partners/<int:pid>")
    @login_required
    @roles_allowed("operator")
    def delete_partner(pid):
        with Session() as s:
            p = s.get(Partner, pid)
            if not p:
                return error_response("Parceiro não encontrado.", status=404, code="not_found")
            s.delete(p)
            s.commit()
            return success_response({"ok": True})

    # Brands
    @app.get("/api/brands")
    @login_required
    def get_brands():
        with Session() as s:
            rows = s.execute(select(Brand)).scalars().all()
            return success_response([serialize_brand(b) for b in rows])

    @app.post("/api/brands")
    @login_required
    @roles_allowed("operator")
    def create_brand():
        data = request.json or {}
        marca = (data.get("marca") or "").strip()
        cod_disagua = (data.get("cod_disagua") or "").strip() or None
        if not marca:
            return error_response("Campo 'marca' é obrigatório.")
        with Session() as s:
            b = Brand(marca=marca, cod_disagua=cod_disagua)
            s.add(b)
            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                return error_response(
                    "Não foi possível salvar a marca. Verifique se o nome já está cadastrado.",
                )
            s.refresh(b)
            return success_response(serialize_brand(b), status=201)

    @app.put("/api/brands/<int:bid>")
    @login_required
    @roles_allowed("operator")
    def update_brand(bid):
        data = request.json or {}
        if not data:
            return error_response("Nenhum campo para atualizar.")
        with Session() as s:
            b = s.get(Brand, bid)
            if not b:
                return error_response("Marca não encontrada.", status=404, code="not_found")
            if "marca" in data:
                marca = (data.get("marca") or "").strip()
                if not marca:
                    return error_response("Campo 'marca' é obrigatório.")
                b.marca = marca
            if "cod_disagua" in data:
                cod_disagua = data.get("cod_disagua")
                if isinstance(cod_disagua, str):
                    cod_disagua = cod_disagua.strip()
                b.cod_disagua = cod_disagua or None
            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                return error_response(
                    "Não foi possível atualizar a marca. Verifique se o nome já está cadastrado.",
                )
            s.refresh(b)
            return success_response(serialize_brand(b))

    @app.delete("/api/brands/<int:bid>")
    @login_required
    @roles_allowed("operator")
    def delete_brand(bid):
        with Session() as s:
            b = s.get(Brand, bid)
            if not b:
                return error_response("Marca não encontrada.", status=404, code="not_found")
            s.delete(b)
            s.commit()
            return success_response({"ok": True})

    # Stores
    @app.get("/api/stores")
    @login_required
    def get_stores():
        with Session() as s:
            rows = s.execute(select(Store, Brand).join(Brand, Store.marca_id == Brand.id)).all()
            stores = [serialize_store(store, brand) for store, brand in rows]
            return success_response(stores)

    @app.post("/api/stores")
    @login_required
    @roles_allowed("operator")
    def create_store():
        data = request.json or {}
        try:
            payload = parse_store_payload(data)
        except ValueError as exc:
            return error_response(str(exc))

        missing = normalize_required(payload, store_required)
        if missing:
            return error_response(
                "Campos obrigatórios ausentes.",
                details={"missing": missing},
            )

        for field in store_float_fields:
            payload.setdefault(field, 0.0)

        with Session() as s:
            if not s.get(Brand, payload["marca_id"]):
                return error_response("Marca não encontrada.")
            st = Store(**payload)
            s.add(st)
            s.commit()
            s.refresh(st)
            brand = s.get(Brand, st.marca_id)
            return success_response(serialize_store(st, brand), status=201)

    @app.put("/api/stores/<int:sid>")
    @login_required
    @roles_allowed("operator")
    def update_store(sid):
        data = request.json or {}
        try:
            payload = parse_store_payload(data)
        except ValueError as exc:
            return error_response(str(exc))

        if not payload:
            return error_response("Nenhum campo para atualizar.")

        with Session() as s:
            st = s.get(Store, sid)
            if not st:
                return error_response("Loja não encontrada.", status=404, code="not_found")
            if "marca_id" in payload and not s.get(Brand, payload["marca_id"]):
                return error_response("Marca não encontrada.")
            for key, value in payload.items():
                setattr(st, key, value)
            s.commit()
            brand = s.get(Brand, st.marca_id)
            return success_response(serialize_store(st, brand))

    @app.delete("/api/stores/<int:sid>")
    @login_required
    @roles_allowed("operator")
    def delete_store(sid):
        with Session() as s:
            st = s.get(Store, sid)
            if not st:
                return error_response("Loja não encontrada.", status=404, code="not_found")
            s.delete(st)
            s.commit()
            return success_response({"ok": True})

    # Connections
    @app.get("/api/connections")
    @login_required
    def get_connections():
        with Session() as s:
            rows = s.execute(select(Connection)).scalars().all()
            return success_response([
                {"id": c.id, "partner_id": c.partner_id, "store_id": c.store_id}
                for c in rows
            ])

    @app.post("/api/connections")
    @login_required
    @roles_allowed("operator")
    def create_connection():
        data = request.json or {}
        with Session() as s:
            c = Connection(**data)
            s.add(c)
            s.commit()
            return success_response({"id": c.id}, status=201)

    @app.delete("/api/connections/<int:cid>")
    @login_required
    @roles_allowed("operator")
    def delete_connection(cid):
        with Session() as s:
            c = s.get(Connection, cid)
            if not c:
                return error_response("Vínculo não encontrado.", status=404, code="not_found")
            s.delete(c)
            s.commit()
            return success_response({"ok": True})

    # Report entries
    @app.get("/api/report-data")
    @login_required
    def get_report_data():
        start = request.args.get("startDate")
        end = request.args.get("endDate")
        marca = request.args.get("marca")
        with Session() as s:
            q = s.query(ReportEntry)
            if start:
                q = q.filter(ReportEntry.data >= date.fromisoformat(start))
            if end:
                q = q.filter(ReportEntry.data <= date.fromisoformat(end))
            if marca:
                q = q.filter(ReportEntry.marca == marca)
            rows = q.all()
            return success_response([
                {
                    "id": r.id,
                    "marca": r.marca,
                    "loja": r.loja,
                    "data": r.data.isoformat(),
                    "valor_20l": r.valor_20l,
                    "valor_10l": r.valor_10l,
                    "valor_1500ml": r.valor_1500ml,
                    "valor_cx_copo": r.valor_cx_copo,
                    "valor_vasilhame": r.valor_vasilhame,
                }
                for r in rows
            ])

    @app.post("/api/report-data/seed")
    @login_required
    @roles_allowed("operator")
    def seed_report_data():
        n = int(request.args.get("n", 100))
        import random
        with Session() as s:
            brands = s.query(Brand).all()
            stores = s.query(Store).all()
            if not brands or not stores:
                return error_response("Cadastre marcas e lojas antes.")
            today = datetime.utcnow().date()
            for _ in range(n):
                brand = random.choice(brands)
                brand_stores = [st for st in stores if st.marca_id == brand.id]
                if not brand_stores:
                    continue
                store = random.choice(brand_stores)
                d = today.replace(day=max(1, random.randint(1, 28)))
                e = ReportEntry(
                    marca=brand.marca, loja=store.loja, data=d,
                    valor_20l=round(random.random()*100, 2),
                    valor_10l=round(random.random()*80, 2),
                    valor_1500ml=round(random.random()*50, 2),
                    valor_cx_copo=round(random.random()*120, 2),
                    valor_vasilhame=round(random.random()*30, 2),
                )
                s.add(e)
            s.commit()
        return success_response({"ok": True, "seeded": n})

    # Upload images
    @app.post("/api/upload")
    @login_required
    @roles_allowed("operator")
    def upload_images():
        brand_id = request.form.get("brand_id")
        files = request.files.getlist("files")
        if not files:
            return error_response("Selecione ao menos um arquivo.")

        brand_id_value = None
        if brand_id not in (None, ""):
            try:
                brand_id_value = int(brand_id)
            except (TypeError, ValueError):
                return error_response("Identificador de marca inválido.")

        saved = []
        with Session() as s:
            if brand_id_value is not None and not s.get(Brand, brand_id_value):
                return error_response("Marca não encontrada.")
            for f in files:
                filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{os.path.basename(f.filename)}"
                path = os.path.join(UPLOAD_DIR, filename)
                f.save(path)
                size_bytes = os.path.getsize(path)
                rec = ReceiptImage(brand_id=brand_id_value, filename=filename, size_bytes=size_bytes)
                s.add(rec)
                s.flush()
                saved.append({
                    "id": rec.id,
                    "filename": filename,
                    "size_bytes": size_bytes,
                    "brand_id": rec.brand_id
                })
            s.commit()
        return success_response({"saved": saved})

    @app.get("/api/receipts")
    @login_required
    def list_receipts():
        with Session() as s:
            rows = s.execute(
                select(ReceiptImage, Brand)
                .join(Brand, ReceiptImage.brand_id == Brand.id, isouter=True)
                .order_by(ReceiptImage.uploaded_at.desc())
            ).all()
            result = []
            for receipt, brand in rows:
                result.append({
                    "id": receipt.id,
                    "filename": receipt.filename,
                    "brand_id": receipt.brand_id,
                    "brand": brand.marca if brand else None,
                    "size_bytes": receipt.size_bytes,
                    "uploaded_at": receipt.uploaded_at.isoformat() if receipt.uploaded_at else None,
                    "url": url_for("get_upload", filename=receipt.filename)
                })
            return success_response(result)

    @app.put("/api/receipts/<int:rid>")
    @login_required
    @roles_allowed("operator")
    def update_receipt(rid):
        data = request.json or {}
        with Session() as s:
            rec = s.get(ReceiptImage, rid)
            if not rec:
                return error_response("Comprovante não encontrado.", status=404, code="not_found")

            if "brand_id" in data:
                brand_value = data.get("brand_id")
                if brand_value in (None, ""):
                    rec.brand_id = None
                else:
                    try:
                        brand_value = int(brand_value)
                    except (TypeError, ValueError):
                        return error_response("Identificador de marca inválido.")
                    if not s.get(Brand, brand_value):
                        return error_response("Marca não encontrada.")
                    rec.brand_id = brand_value

            if "filename" in data:
                new_name = str(data.get("filename", "")).strip()
                if not new_name:
                    return error_response("Nome de arquivo inválido.")
                new_name = os.path.basename(new_name)
                original_ext = os.path.splitext(rec.filename)[1]
                if not os.path.splitext(new_name)[1] and original_ext:
                    new_name = f"{new_name}{original_ext}"
                if new_name != rec.filename:
                    new_path = os.path.join(app.config["UPLOAD_FOLDER"], new_name)
                    if os.path.exists(new_path):
                        return error_response("Já existe um comprovante com esse nome.")
                    old_path = os.path.join(app.config["UPLOAD_FOLDER"], rec.filename)
                    try:
                        os.rename(old_path, new_path)
                    except OSError:
                        return error_response("Não foi possível renomear o arquivo.", status=500)
                    rec.filename = new_name

            s.commit()
            return success_response({"ok": True})

    # Export
    @app.get("/api/report-data/export")
    @login_required
    def export_report():
        fmt = request.args.get("format", "excel")
        start = request.args.get("startDate")
        end = request.args.get("endDate")
        marca = request.args.get("marca")
        with Session() as s:
            q = s.query(ReportEntry)
            if start: q = q.filter(ReportEntry.data >= date.fromisoformat(start))
            if end: q = q.filter(ReportEntry.data <= date.fromisoformat(end))
            if marca: q = q.filter(ReportEntry.marca == marca)
            rows = q.all()
            data = [{
                "Marca": r.marca,
                "Loja": r.loja,
                "Data": r.data.isoformat(),
                "Valor 20L": r.valor_20l,
                "Valor 10L": r.valor_10l,
                "Valor 1500ML": r.valor_1500ml,
                "Valor CX Copo": r.valor_cx_copo,
                "Valor Vasilhame": r.valor_vasilhame,
                "Total": (r.valor_20l + r.valor_10l + r.valor_1500ml + r.valor_cx_copo + r.valor_vasilhame)
            } for r in rows]

        manager = ExportManager()
        try:
            result = manager.export(data, fmt)
        except ValueError as exc:
            return error_response(str(exc))

        return send_file(
            result.buffer,
            as_attachment=True,
            download_name=result.filename,
            mimetype=result.mimetype,
        )

    # Users API
    @app.get("/api/users")
    @login_required
    @admin_required
    def list_users():
        with Session() as s:
            rows = s.query(User).all()
            return success_response([
                {"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active}
                for u in rows
            ])

    @app.post("/api/users")
    @login_required
    @admin_required
    def create_user():
        from werkzeug.security import generate_password_hash
        data = request.json or {}
        username = data.get("username","").strip()
        password = data.get("password","")
        role = data.get("role","operator")
        is_active = bool(data.get("is_active", True))
        if len(username) < 3 or len(password) < 6:
            return error_response("username ou password inválidos")
        with Session() as s:
            if s.query(User).filter(User.username==username).first():
                return error_response("username já existe")
            u = User(username=username, password_hash=generate_password_hash(password), role=role, is_active=is_active)
            s.add(u)
            s.commit()
            return success_response({"id": u.id}, status=201)

    @app.put("/api/users/<int:uid>")
    @login_required
    @admin_required
    def update_user(uid):
        data = request.json or {}
        with Session() as s:
            u = s.get(User, uid)
            if not u:
                return error_response("Usuário não encontrado.", status=404, code="not_found")
            if "role" in data:
                u.role = data["role"]
            if "is_active" in data:
                u.is_active = bool(data["is_active"])
            s.commit()
            return success_response({"ok": True})

    @app.put("/api/users/<int:uid>/password")
    @login_required
    @admin_required
    def change_user_password(uid):
        from werkzeug.security import generate_password_hash
        data = request.json or {}
        new_pwd = data.get("new_password","")
        if len(new_pwd) < 6:
            return error_response("senha curta")
        with Session() as s:
            u = s.get(User, uid)
            if not u:
                return error_response("Usuário não encontrado.", status=404, code="not_found")
            u.password_hash = generate_password_hash(new_pwd)
            s.commit()
            return success_response({"ok": True})

    @app.delete("/api/users/<int:uid>")
    @login_required
    @admin_required
    def delete_user(uid):
        with Session() as s:
            u = s.get(User, uid)
            if not u:
                return error_response("Usuário não encontrado.", status=404, code="not_found")
            if u.username == "admin":
                return error_response("não é permitido excluir o administrador padrão")
            s.delete(u)
            s.commit()
            return success_response({"ok": True})

    @app.get("/uploads/<path:filename>")
    @login_required
    def get_upload(filename):
        return send_from_directory(UPLOAD_DIR, filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
