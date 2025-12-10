from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login  

# --- TABLAS CATÁLOGOS ---

class Membresia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)  # Ej: Plan A
    clases_por_semana = db.Column(db.Integer, nullable=False)
    socios = db.relationship('Socio', backref='membresia', lazy=True)
    tarifas = db.relationship('Tarifa', backref='membresia', lazy=True)

class Tarifa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    membresia_id = db.Column(db.Integer, db.ForeignKey('membresia.id'), nullable=False)
    nivel = db.Column(db.String(20), nullable=False)  # Bebés, Niños, Adultos
    costo_mensual = db.Column(db.Float, nullable=False)
    costo_anualidad = db.Column(db.Float, nullable=False)
    costo_inscripcion = db.Column(db.Float, nullable=False)

class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String(15), nullable=False) # Lunes, Martes...
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    nivel = db.Column(db.String(20), nullable=False)
    capacidad_maxima = db.Column(db.Integer, default=10)
    
    # Relación dinámica para filtros
    inscripciones = db.relationship('Inscripcion', backref='horario', lazy='dynamic')
    asistencias = db.relationship('Asistencia', backref='horario', lazy=True)

    def cupos_disponibles(self):
        # Cuenta solo las inscripciones activas
        ocupados = self.inscripciones.filter_by(activo=True).count()
        return self.capacidad_maxima - ocupados

# --- TABLAS OPERATIVAS ---

class Socio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True, index=True) # SW0001
    nombre_completo = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(200)) # URL o path del archivo
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    nivel = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    membresia_id = db.Column(db.Integer, db.ForeignKey('membresia.id'))
    
    # Relaciones
    inscripciones = db.relationship('Inscripcion', backref='socio', lazy='dynamic')
    asistencias = db.relationship('Asistencia', backref='socio', lazy='dynamic')
    pagos = db.relationship('Pago', backref='socio', lazy='dynamic')

class Inscripcion(db.Model):
    """ Reservaciones Fijas """
    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socio.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.id'), nullable=False)
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socio.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.id'), nullable=False)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(20), default='Presente') # Presente, Falta
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folio_recibo = db.Column(db.String(20))
    socio_id = db.Column(db.Integer, db.ForeignKey('socio.id'), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    
    concepto_tipo = db.Column(db.String(50)) # Mensualidad, Anualidad
    detalle_concepto = db.Column(db.String(100)) # Noviembre 2024
    
    monto_base = db.Column(db.Float)
    monto_ajuste = db.Column(db.Float, default=0.0)
    total_cobrado = db.Column(db.Float)
    
    metodo_pago = db.Column(db.String(50))
    requiere_factura = db.Column(db.Boolean, default=False)

# --- NUEVA CLASE USUARIO ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False) # 'admin', 'recepcion', 'instructor'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- CARGADOR DE USUARIO (Requerido por Flask-Login) ---
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Nivel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    
    # Esto es solo para mantener el orden visual si lo deseas
    orden = db.Column(db.Integer, default=0) 

    def __repr__(self):
        return f'<Nivel {self.nombre}>'