from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms import PasswordField, BooleanField 
from wtforms import IntegerField, TimeField, DecimalField
from wtforms import DateField
from flask_wtf.file import FileField, FileAllowed

class SocioForm(FlaskForm):
    nombre_completo = StringField('Nombre Completo', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    
    foto = FileField('Fotografía del Socio', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imágenes (jpg, png)')
    ])
    # Opciones estáticas para Nivel (deben coincidir con tus horarios)
    nivel_id = SelectField('Nivel', coerce=int, validators=[DataRequired()])
    
    # El campo de Membresía se llenará dinámicamente en la vista (Route)
    membresia_id = SelectField('Membresía', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Guardar Socio')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Ingresar')

# --- FORMULARIOS DE ADMINISTRACIÓN ---

class HorarioForm(FlaskForm):
    dia_semana = SelectField('Día', choices=[
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')
    ], validators=[DataRequired()])
    
    hora_inicio = TimeField('Hora Inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora Fin', validators=[DataRequired()])
    
    nivel_id = SelectField('Nivel', coerce=int, validators=[DataRequired()])
    
    capacidad_maxima = IntegerField('Cupo Máximo', default=8, validators=[DataRequired()])
    submit = SubmitField('Guardar Horario')

class TarifaForm(FlaskForm):
    # --- NUEVOS CAMPOS PARA CREACIÓN ---
    membresia_id = SelectField('Membresía', coerce=int, validators=[DataRequired()])
    nivel_id = SelectField('Nivel', coerce=int, validators=[DataRequired()])
    
    # --- CAMPOS DE COSTOS (YA EXISTÍAN) ---
    costo_mensual = DecimalField('Costo Mensual', places=2, validators=[DataRequired()])
    costo_anualidad = DecimalField('Costo Anualidad', places=2, validators=[DataRequired()])
    costo_inscripcion = DecimalField('Costo Inscripción', places=2, validators=[DataRequired()])
    
    submit = SubmitField('Guardar Tarifa')

class MembresiaForm(FlaskForm):
    nombre = StringField('Nombre del Plan', validators=[DataRequired(), Length(max=50)])
    clases_por_semana = IntegerField('Límite de Clases por Semana', 
                                     validators=[DataRequired()],
                                     render_kw={"min": 1, "max": 7}) # Restricción visual HTML5
    submit = SubmitField('Guardar Plan')

class NivelForm(FlaskForm):
    nombre = StringField('Nombre del Nivel', validators=[DataRequired()])
    orden = IntegerField('Orden de visualización', default=1)
    submit = SubmitField('Guardar Nivel')
