from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from config import Config

# Configuraciones
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager() 
csrf = CSRFProtect()
login.login_view = 'auth.login'
login.login_message = "Por favor inicia sesión para acceder a esta página."

def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    # Conectar extensiones a la app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    # Importar modelos para que Flask sepa que existen
    from app import models
    from app.models import User

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
        return dict(current_year=datetime.now().year)

    with app.app_context():
        db.create_all()
        if config_name == 'testing':
            if not User.query.filter_by(username='testadmin').first():
                admin = User(username='testadmin', role='admin')
                admin.set_password('test')
                db.session.add(admin)
                db.session.commit()

    return app
