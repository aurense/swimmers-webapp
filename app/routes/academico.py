from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models import Socio, Horario, Inscripcion
from flask_login import login_required

academico_bp = Blueprint('academico', __name__, url_prefix='/academico')

# --- FUNCIONES DE AYUDA (VALIDACIONES) ---

def validar_reglas_dia(socio_id, nuevo_horario):
    """
    Valida que el socio no tenga YA una clase ese mismo día.
    Retorna: (True, "OK") o (False, "Mensaje de Error")
    """
    inscripciones_activas = Inscripcion.query.filter_by(socio_id=socio_id, activo=True).all()
    
    for insc in inscripciones_activas:
        existente = insc.horario
        if existente.dia_semana == nuevo_horario.dia_semana:
            return False, f"El socio ya tiene una clase registrada los {existente.dia_semana} ({existente.hora_inicio.strftime('%H:%M')}). Debe darla de baja primero si desea cambiar el horario."
            
    return True, "OK"

def _validar_inscripcion(socio, horario):
    """Función auxiliar para validar todas las reglas de negocio."""
    es_activo, mensaje_estatus, _ = socio.get_estatus_financiero()
    if not es_activo:
        return False, f'⛔ BLOQUEO: No se puede inscribir. {mensaje_estatus}.'

    if horario.cupos_disponibles() <= 0:
        return False, 'La clase seleccionada ya está llena.'

    clases_actuales = Inscripcion.query.filter_by(socio_id=socio.id, activo=True).count()
    if clases_actuales >= socio.membresia.clases_por_semana:
        return False, f'El plan {socio.membresia.nombre} solo permite {socio.membresia.clases_por_semana} clases.'

    es_valido, msg = validar_reglas_dia(socio.id, horario)
    if not es_valido:
        return False, msg

    return True, "OK"

# --- RUTAS ---

@academico_bp.route('/inscribir/<int:socio_id>')
@login_required
def inscribir(socio_id):
    socio = Socio.query.get_or_404(socio_id)
    clases_actuales = Inscripcion.query.filter_by(socio_id=socio.id, activo=True).all()
    horarios_disponibles = Horario.query.filter_by(nivel=socio.nivel).order_by(Horario.hora_inicio).all()
    
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    agenda = {dia: [] for dia in orden_dias}
    
    for h in horarios_disponibles:
        if h.dia_semana in agenda:
            agenda[h.dia_semana].append(h)
            
    return render_template('academico/inscribir.html', socio=socio, agenda=agenda, clases_actuales=clases_actuales)

@academico_bp.route('/inscribir-ajax', methods=['POST'])
@login_required
def inscribir_ajax():
    socio_id = request.form.get('socio_id')
    horario_id = request.form.get('horario_id')

    socio = Socio.query.get(socio_id)
    horario = Horario.query.get(horario_id)

    if not socio or not horario:
        return jsonify({'status': 'error', 'message': 'Socio u horario no encontrado.'}), 404

    es_valido, mensaje = _validar_inscripcion(socio, horario)
    
    if not es_valido:
        return jsonify({'status': 'error', 'message': mensaje})

    try:
        nueva_inscripcion = Inscripcion(socio_id=socio.id, horario_id=horario.id)
        db.session.add(nueva_inscripcion)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '¡Inscripción realizada con éxito!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error en la base de datos: {str(e)}'}), 500

@academico_bp.route('/baja/<int:inscripcion_id>')
@login_required
def baja(inscripcion_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    
    inscripcion.activo = False
    db.session.commit()
    
    flash('Clase cancelada. El cupo ha sido liberado.', 'info')
    
    return redirect(url_for('academico.inscribir', socio_id=inscripcion.socio_id))