from flask import Blueprint, render_template
from app.models import Horario, Inscripcion
from flask_login import login_required

# Definir el Blueprint
horarios_bp = Blueprint('horarios', __name__, url_prefix='/horarios')

@horarios_bp.route('/')
@login_required
def calendario():
    # 1. Obtener todos los horarios de la base de datos
    todos_horarios = Horario.query.all()
    
    # 2. Estructura para ordenar los días cronológicamente
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # 3. Agrupar horarios por día
    agenda_semanal = {dia: [] for dia in orden_dias}
    
    for h in todos_horarios:
        if h.dia_semana in agenda_semanal:
            # Calculamos esto aquí para enviarlo listo a la vista
            datos_horario = {
                'objeto': h,
                'disponibles': h.cupos_disponibles(),
                'porcentaje_ocupacion': ((h.capacidad_maxima - h.cupos_disponibles()) / h.capacidad_maxima) * 100
            }
            agenda_semanal[h.dia_semana].append(datos_horario)
    
    # 4. Ordenar las horas dentro de cada día
    for dia in agenda_semanal:
        agenda_semanal[dia].sort(key=lambda x: x['objeto'].hora_inicio)

    return render_template('horarios/calendario.html', agenda=agenda_semanal)

@horarios_bp.route('/detalle/<int:id>')
def detalle_clase(id):
    # 1. Obtener la clase (horario)
    horario = Horario.query.get_or_404(id)
    
    # 2. Obtener los alumnos inscritos (Solo los ACTIVOS)
    # Usamos la relación 'inscripciones' definida en el modelo Horario
    inscritos = horario.inscripciones.filter_by(activo=True).all()
    
    return render_template('horarios/detalle.html', horario=horario, alumnos=inscritos)