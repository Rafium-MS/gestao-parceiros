
import os
from datetime import datetime, date
from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Partner, Brand, Store, Connection, ReportEntry, ReceiptImage

DB_PATH = os.path.join(os.path.dirname(__file__), "disagua.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["JSON_AS_ASCII"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
    CORS(app)

    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine, autoflush=False, future=True))

    # ---------------------- PAGES ----------------------
    @app.get("/")
    def home():
        return render_template("index.html")
    @app.get("/parceiros")
    def page_parceiros():
        return render_template("parceiros.html")
    @app.get("/lojas")
    def page_lojas():
        return render_template("lojas.html")
    @app.get("/conectar")
    def page_conectar():
        return render_template("conectar.html")
    @app.get("/comprovantes")
    def page_comprovantes():
        return render_template("comprovantes.html")
    @app.get("/relatorios")
    def page_relatorios():
        return render_template("relatorios.html")

    # ---------------------- APIs ----------------------
    # Partners
    @app.get("/api/partners")
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
    def create_partner():
        data = request.json or {}
        with Session() as s:
            p = Partner(**data)
            s.add(p); s.commit()
            return jsonify({"id": p.id}), 201

    # Brands
    @app.get("/api/brands")
    def get_brands():
        with Session() as s:
            rows = s.execute(select(Brand)).scalars().all()
            return jsonify([{"id": b.id, "marca": b.marca, "cod_disagua": b.cod_disagua} for b in rows])

    @app.post("/api/brands")
    def create_brand():
        data = request.json or {}
        with Session() as s:
            b = Brand(**data)
            s.add(b); s.commit()
            return jsonify({"id": b.id}), 201

    # Stores
    @app.get("/api/stores")
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
    def create_store():
        data = request.json or {}
        with Session() as s:
            st = Store(**data); s.add(st); s.commit()
            return jsonify({"id": st.id}), 201

    # Connections
    @app.get("/api/connections")
    def get_connections():
        with Session() as s:
            rows = s.execute(select(Connection)).scalars().all()
            return jsonify([{"id": c.id, "partner_id": c.partner_id, "store_id": c.store_id} for c in rows])

    @app.post("/api/connections")
    def create_connection():
        data = request.json or {}
        with Session() as s:
            c = Connection(**data); s.add(c); s.commit()
            return jsonify({"id": c.id}), 201

    # Report entries
    @app.get("/api/report-data")
    def get_report_data():
        # Optional filters: startDate, endDate, marca
        start = request.args.get("startDate")
        end = request.args.get("endDate")
        marca = request.args.get("marca")  # brand name
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
    def seed_report_data():
        # Seed sample data similar to current front-end generator
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

    # Upload images (comprovantes)
    @app.post("/api/upload")
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

    @app.get("/uploads/<path:filename>")
    def get_upload(filename):
        return send_from_directory(UPLOAD_DIR, filename)


        # --- Update/Delete Partners ---
        @app.put("/api/partners/<int:pid>")
        def update_partner(pid):
            data = request.json or {}
            with Session() as s:
                obj = s.get(Partner, pid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                for k,v in data.items():
                    if hasattr(obj, k): setattr(obj, k, v)
                s.commit()
                return jsonify({"ok": True})

        @app.delete("/api/partners/<int:pid>")
        def delete_partner(pid):
            with Session() as s:
                obj = s.get(Partner, pid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                s.delete(obj); s.commit()
                return jsonify({"ok": True})

        # --- Update/Delete Brands ---
        @app.put("/api/brands/<int:bid>")
        def update_brand(bid):
            data = request.json or {}
            with Session() as s:
                obj = s.get(Brand, bid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                for k,v in data.items():
                    if hasattr(obj, k): setattr(obj, k, v)
                s.commit()
                return jsonify({"ok": True})

        @app.delete("/api/brands/<int:bid>")
        def delete_brand(bid):
            with Session() as s:
                obj = s.get(Brand, bid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                s.delete(obj); s.commit()
                return jsonify({"ok": True})

        # --- Update/Delete Stores ---
        @app.put("/api/stores/<int:sid>")
        def update_store(sid):
            data = request.json or {}
            with Session() as s:
                obj = s.get(Store, sid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                for k,v in data.items():
                    if hasattr(obj, k): setattr(obj, k, v)
                s.commit()
                return jsonify({"ok": True})

        @app.delete("/api/stores/<int:sid>")
        def delete_store(sid):
            with Session() as s:
                obj = s.get(Store, sid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                s.delete(obj); s.commit()
                return jsonify({"ok": True})

        # --- Delete Connection ---
        @app.delete("/api/connections/<int:cid>")
        def delete_connection(cid):
            with Session() as s:
                obj = s.get(Connection, cid)
                if not obj:
                    return jsonify({"error":"not found"}), 404
                s.delete(obj); s.commit()
                return jsonify({"ok": True})
    

    # --- UPDATE/DELETE PARTNER ---
    @app.put("/api/partners/<int:pid>")
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
    def delete_partner(pid):
        with Session() as s:
            p = s.get(Partner, pid)
            if not p: return jsonify({"error":"not found"}), 404
            s.delete(p); s.commit()
            return jsonify({"ok": True})

    # --- UPDATE/DELETE BRAND ---
    @app.put("/api/brands/<int:bid>")
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
    def delete_brand(bid):
        with Session() as s:
            b = s.get(Brand, bid)
            if not b: return jsonify({"error":"not found"}), 404
            s.delete(b); s.commit()
            return jsonify({"ok": True})

    # --- UPDATE/DELETE STORE ---
    @app.put("/api/stores/<int:sid>")
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
    def delete_store(sid):
        with Session() as s:
            st = s.get(Store, sid)
            if not st: return jsonify({"error":"not found"}), 404
            s.delete(st); s.commit()
            return jsonify({"ok": True})

    # --- DELETE CONNECTION ---
    @app.delete("/api/connections/<int:cid>")
    def delete_connection(cid):
        with Session() as s:
            c = s.get(Connection, cid)
            if not c: return jsonify({"error":"not found"}), 404
            s.delete(c); s.commit()
            return jsonify({"ok": True})
    

    return app

if __name__ == "__main__":
    app = create_app()
    # For dev: use Flask built-in; in production consider waitress/uvicorn.
    app.run(host="127.0.0.1", port=5000, debug=True)
