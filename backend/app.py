import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure the database
# Get the absolute path of the directory where the script is running
basedir = os.path.abspath(os.path.dirname(__file__))
# Set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gestao_parceiros.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import db from extensions
from backend.extensions import db
# Import models
from backend.models import Role, User

# Initialize the database with the app
db.init_app(app)

def add_initial_data():
    # Inserir roles padrão se não existirem
    if Role.query.count() == 0:
        roles = [
            Role(nome="Admin"),
            Role(nome="Operador"),
            Role(nome="Financeiro"),
            Role(nome="Visualizador")
        ]
        db.session.bulk_save_objects(roles)
        db.session.commit()

    # Criar usuário administrador padrão se não existir
    if User.query.count() == 0:
        admin_role = Role.query.filter_by(nome="Admin").first()
        if admin_role:
            # In a real app, use a hashed password
            admin_user = User(username="admin", password="admin", role_id=admin_role.id)
            db.session.add(admin_user)
            db.session.commit()

@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables and initial data."""
    with app.app_context():
        db.create_all()
        add_initial_data()
    print("Initialized the database.")

# Register Blueprints
from backend.api.parceiros import parceiros_bp
from backend.api.lojas import lojas_bp
from backend.api.comprovantes import comprovantes_bp
from backend.api.associacoes import associacoes_bp

app.register_blueprint(parceiros_bp)
app.register_blueprint(lojas_bp)
app.register_blueprint(comprovantes_bp)
app.register_blueprint(associacoes_bp)


@app.route('/')
def index():
    return "Backend is running!"

if __name__ == '__main__':
    app.run(debug=True)
