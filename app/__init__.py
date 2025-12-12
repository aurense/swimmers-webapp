from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from config import Config

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager() # <--- INICIALIZAR
csrf = CSRFProtect()
login.login_view = 'auth.login' # <--- Redirigir aquí si no está logueado
login.login_message = "Por favor inicia sesión para acceder a esta página."

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Conectar extensiones a la app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    # Importar modelos para que Flask sepa que existen
    from app import models

    # Registrar Blueprints
    from app.routes.socios import socios_bp
    app.register_blueprint(socios_bp)

    from app.routes.horarios import horarios_bp
    app.register_blueprint(horarios_bp)

    from app.routes.academico import academico_bp
    app.register_blueprint(academico_bp)
    
    from app.routes.finanzas import finanzas_bp
    app.register_blueprint(finanzas_bp)

    from app.routes.asistencia import asistencia_bp
    app.register_blueprint(asistencia_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.reportes import reportes_bp
    app.register_blueprint(reportes_bp)


    # Ruta raíz temporal para que no dé error 404 al entrar a localhost:5000
    @app.route('/')
    def index():
        return redirect('/auth/login')

    @app.context_processor
    def inject_context():
        """
        Esta función hace que la variable 'current_year' 
        esté disponible en TODOS los archivos HTML.
        """
        return dict(current_year=datetime.now().year)

    return app