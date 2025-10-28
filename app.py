
import os
from functools import wraps
from datetime import datetime, date
from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, send_file, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Partner, Brand, Store, Connection, ReportEntry, ReceiptImage, User

DB_PATH = os.path.join(os.path.dirname(__file__), "disagua.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["JSON_AS_ASCII"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
    CORS(app)
    app.secret_key = 'change-me'

    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine, autoflush=False, future=True))

    class _LoginUser(UserMixin):
        def __init__(self, db_user):
            self.db_user = db_user
            self.id = str(db_user.id)
            self.username = db_user.username
            self.is_active = db_user.is_active

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
                from flask import abort
                return abort(401)
            with Session() as s:
                u = s.get(User, int(current_user.id))
                if not u or u.role != 'admin':
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
                    from flask import abort
                    return abort(401)
                with Session() as s:
                    u = s.get(User, int(current_user.id))
                    if not u:
                        from flask import abort
                        return abort(401)
                    if u.role != 'admin' and u.role not in roles:
                        from flask import abort
                        return abort(403)
                return f(*args, **kwargs)
            return wrapper
        return decorator

    # ---------------------- PAGES ----------------------
    @app.get("/login")
    def login():
        return render_template("login.html")

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
                return render_template("login.html", error="Usuário ou senha inválidos.")
            login_user(_LoginUser(u))
            return redirect(url_for("home"))

    @app.get("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.get("/")
    @login_required
    def home():
        return render_template("index.html")

    @app.get("/parceiros")
    @login_required
    def page_parceiros():
        return render_template("parceiros.html")

    @app.get("/lojas")
    @login_required
    def page_lojas():
        return render_template("lojas.html")

    @app.get("/conectar")
    @login_required
    def page_conectar():
        return render_template("conectar.html")

    @app.get("/comprovantes")
    @login_required
    def page_comprovantes():
        return render_template("comprovantes.html")

    @app.get("/relatorios")
    @login_required
    def page_relatorios():
        return render_template("relatorios.html")

    @app.get("/account")
    @login_required
    def account():
        return render_template("account.html", username=current_user.username)

    @app.post("/account")
    @login_required
    def account_update():
        from werkzeug.security import check_password_hash, generate_password_hash
        current_pwd = request.form.get("current_password","")
        new_pwd = request.form.get("new_password","")
        confirm_pwd = request.form.get("confirm_password","")
        if len(new_pwd) < 6:
            return render_template("account.html", username=current_user.username, error="A nova senha deve ter ao menos 6 caracteres.")
        if new_pwd != confirm_pwd:
            return render_template("account.html", username=current_user.username, error="A confirmação de senha não confere.")
        with Session() as s:
            u = s.get(User, int(current_user.id))
            if not u or not check_password_hash(u.password_hash, current_pwd):
                return render_template("account.html", username=current_user.username, error="Senha atual incorreta.")
            from werkzeug.security import generate_password_hash
            u.password_hash = generate_password_hash(new_pwd)
            s.commit()
        return render_template("account.html", username=current_user.username, success="Senha alterada com sucesso.")

    @app.get("/users")
    @login_required
    @admin_required
    def users_page():
        return render_template("users.html")

    # ---------------------- APIs ----------------------
    @app.get("/api/me")
    @login_required
    def whoami():
        with Session() as s:
            u = s.get(User, int(current_user.id))
            return jsonify({"id": u.id, "username": u.username, "role": u.role})

    # Partners
    @app.get("/api/partners")
    @login_required
    def get_partners():
        with Session() as s:
            rows = s.execute(select(Partner)).scalars().all()
            return jsonify([{
                "id": r.id, "cidade": r.cidade, "estado": r.estado, "parceiro": r.parceiro,
                "distribuidora": r.distribuidora, "cnpj_cpf": r.cnpj_cpf, "telefone": r.telefone,
                "email": r.email, "cx_copo": r.cx_copo, "dez_litros": r.dez_litros,
                "vinte_litros": r.vinte_litros, "mil_quinhentos_ml": r.mil_quinhentos_ml,
                "vasilhame": r.vasilhame
            } for r in rows])

    @app.post("/api/partners")
    @login_required
    @roles_allowed("operator")
    def create_partner():
        data = request.json or {}
        with Session() as s:
            p = Partner(**data)
            s.add(p); s.commit()
            return jsonify({"id": p.id}), 201

    @app.put("/api/partners/<int:pid>")
    @login_required
    @roles_allowed("operator")
    def update_partner(pid):
        data = request.json or {}
        with Session() as s:
            p = s.get(Partner, pid)
            if not p: return jsonify({"error":"not found"}), 404
            for k,v in data.items():
                if hasattr(p, k): setattr(p, k, v)
            s.commit()
            return jsonify({"ok": True})

    @app.delete("/api/partners/<int:pid>")
    @login_required
    @roles_allowed("operator")
    def delete_partner(pid):
        with Session() as s:
            p = s.get(Partner, pid)
            if not p: return jsonify({"error":"not found"}), 404
            s.delete(p); s.commit()
            return jsonify({"ok": True})

    # Brands
    @app.get("/api/brands")
    @login_required
    def get_brands():
        with Session() as s:
            rows = s.execute(select(Brand)).scalars().all()
            return jsonify([{"id": b.id, "marca": b.marca, "cod_disagua": b.cod_disagua} for b in rows])

    @app.post("/api/brands")
    @login_required
    @roles_allowed("operator")
    def create_brand():
        data = request.json or {}
        with Session() as s:
            b = Brand(**data)
            s.add(b); s.commit()
            return jsonify({"id": b.id}), 201

    @app.put("/api/brands/<int:bid>")
    @login_required
    @roles_allowed("operator")
    def update_brand(bid):
        data = request.json or {}
        with Session() as s:
            b = s.get(Brand, bid)
            if not b: return jsonify({"error":"not found"}), 404
            for k,v in data.items():
                if hasattr(b, k): setattr(b, k, v)
            s.commit()
            return jsonify({"ok": True})

    @app.delete("/api/brands/<int:bid>")
    @login_required
    @roles_allowed("operator")
    def delete_brand(bid):
        with Session() as s:
            b = s.get(Brand, bid)
            if not b: return jsonify({"error":"not found"}), 404
            s.delete(b); s.commit()
            return jsonify({"ok": True})

    # Stores
    @app.get("/api/stores")
    @login_required
    def get_stores():
        with Session() as s:
            rows = s.execute(select(Store)).scalars().all()
            return jsonify([{
                "id": st.id, "marca_id": st.marca_id, "loja": st.loja, "cod_disagua": st.cod_disagua,
                "local_entrega": st.local_entrega, "endereco": st.endereco,
                "municipio": st.municipio, "uf": st.uf,
                "valor_20l": st.valor_20l, "valor_10l": st.valor_10l,
                "valor_1500ml": st.valor_1500ml, "valor_cx_copo": st.valor_cx_copo,
                "valor_vasilhame": st.valor_vasilhame
            } for st in rows])

    @app.post("/api/stores")
    @login_required
    @roles_allowed("operator")
    def create_store():
        data = request.json or {}
        with Session() as s:
            st = Store(**data); s.add(st); s.commit()
            return jsonify({"id": st.id}), 201

    @app.put("/api/stores/<int:sid>")
    @login_required
    @roles_allowed("operator")
    def update_store(sid):
        data = request.json or {}
        with Session() as s:
            st = s.get(Store, sid)
            if not st: return jsonify({"error":"not found"}), 404
            for k,v in data.items():
                if hasattr(st, k): setattr(st, k, v)
            s.commit()
            return jsonify({"ok": True})

    @app.delete("/api/stores/<int:sid>")
    @login_required
    @roles_allowed("operator")
    def delete_store(sid):
        with Session() as s:
            st = s.get(Store, sid)
            if not st: return jsonify({"error":"not found"}), 404
            s.delete(st); s.commit()
            return jsonify({"ok": True})

    # Connections
    @app.get("/api/connections")
    @login_required
    def get_connections():
        with Session() as s:
            rows = s.execute(select(Connection)).scalars().all()
            return jsonify([{"id": c.id, "partner_id": c.partner_id, "store_id": c.store_id} for c in rows])

    @app.post("/api/connections")
    @login_required
    @roles_allowed("operator")
    def create_connection():
        data = request.json or {}
        with Session() as s:
            c = Connection(**data); s.add(c); s.commit()
            return jsonify({"id": c.id}), 201

    @app.delete("/api/connections/<int:cid>")
    @login_required
    @roles_allowed("operator")
    def delete_connection(cid):
        with Session() as s:
            c = s.get(Connection, cid)
            if not c: return jsonify({"error":"not found"}), 404
            s.delete(c); s.commit()
            return jsonify({"ok": True})

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
            return jsonify([{
                "id": r.id, "marca": r.marca, "loja": r.loja, "data": r.data.isoformat(),
                "valor_20l": r.valor_20l, "valor_10l": r.valor_10l, "valor_1500ml": r.valor_1500ml,
                "valor_cx_copo": r.valor_cx_copo, "valor_vasilhame": r.valor_vasilhame
            } for r in rows])

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
                return jsonify({"error": "Cadastre marcas e lojas antes."}), 400
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
        return jsonify({"ok": True, "seeded": n})

    # Upload images
    @app.post("/api/upload")
    @login_required
    @roles_allowed("operator")
    def upload_images():
        brand_id = request.form.get("brand_id")
        files = request.files.getlist("files")
        saved = []
        with Session() as s:
            for f in files:
                filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{f.filename}"
                path = os.path.join(UPLOAD_DIR, filename)
                f.save(path)
                size_bytes = os.path.getsize(path)
                rec = ReceiptImage(brand_id=int(brand_id) if brand_id else None, filename=filename, size_bytes=size_bytes)
                s.add(rec); s.flush()
                saved.append({"id": rec.id, "filename": filename, "size_bytes": size_bytes})
            s.commit()
        return jsonify({"saved": saved})

    # Export
    @app.get("/api/report-data/export")
    @login_required
    def export_report():
        import io
        import pandas as pd
        fmt = request.args.get("format","excel")
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
        if fmt == "excel":
            df = pd.DataFrame(data)
            bio = io.BytesIO()
            with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Relatório")
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name="relatorio.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            bio = io.BytesIO()
            doc = SimpleDocTemplate(bio, pagesize=A4)
            styles = getSampleStyleSheet()
            elems = [Paragraph("Relatório de Marcas e Lojas", styles['Title']), Spacer(1, 12)]
            if data:
                headers = list(data[0].keys())
                rows_tbl = [headers] + [[str(r[h]) for h in headers] for r in data]
            else:
                rows_tbl = [["Sem dados"]]
            t = Table(rows_tbl, repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.lightgrey),
                                   ('GRID',(0,0),(-1,-1), 0.25, colors.grey),
                                   ('FONT',(0,0),(-1,0),'Helvetica-Bold'),
                                   ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, colors.whitesmoke])]))
            elems.append(t)
            doc.build(elems)
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name="relatorio.pdf", mimetype="application/pdf")

    # Users API
    @app.get("/api/users")
    @login_required
    @admin_required
    def list_users():
        with Session() as s:
            rows = s.query(User).all()
            return jsonify([{"id":u.id, "username":u.username, "role":u.role, "is_active":u.is_active} for u in rows])

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
        if len(username)<3 or len(password)<6:
            return jsonify({"error":"username ou password inválidos"}), 400
        with Session() as s:
            if s.query(User).filter(User.username==username).first():
                return jsonify({"error":"username já existe"}), 400
            u = User(username=username, password_hash=generate_password_hash(password), role=role, is_active=is_active)
            s.add(u); s.commit()
            return jsonify({"id":u.id}), 201

    @app.put("/api/users/<int:uid>")
    @login_required
    @admin_required
    def update_user(uid):
        data = request.json or {}
        with Session() as s:
            u = s.get(User, uid)
            if not u: return jsonify({"error":"not found"}), 404
            if "role" in data: u.role = data["role"]
            if "is_active" in data: u.is_active = bool(data["is_active"])
            s.commit()
            return jsonify({"ok":True})

    @app.put("/api/users/<int:uid>/password")
    @login_required
    @admin_required
    def change_user_password(uid):
        from werkzeug.security import generate_password_hash
        data = request.json or {}
        new_pwd = data.get("new_password","")
        if len(new_pwd) < 6:
            return jsonify({"error":"senha curta"}), 400
        with Session() as s:
            u = s.get(User, uid)
            if not u: return jsonify({"error":"not found"}), 404
            u.password_hash = generate_password_hash(new_pwd)
            s.commit()
            return jsonify({"ok":True})

    @app.delete("/api/users/<int:uid>")
    @login_required
    @admin_required
    def delete_user(uid):
        with Session() as s:
            u = s.get(User, uid)
            if not u: return jsonify({"error":"not found"}), 404
            if u.username == "admin":
                return jsonify({"error":"não é permitido excluir o administrador padrão"}), 400
            s.delete(u); s.commit()
            return jsonify({"ok":True})

    @app.get("/uploads/<path:filename>")
    @login_required
    def get_upload(filename):
        return send_from_directory(UPLOAD_DIR, filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
