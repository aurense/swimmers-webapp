from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Horario, Asistencia, Inscripcion, Socio
from datetime import datetime
from flask_login import login_required

asistencia_bp = Blueprint('asistencia', __name__, url_prefix='/asistencia')

def obtener_dia_actual_espanol():
    """Traduce el día de Python (Monday) al de nuestra BD (Lunes)"""
    mapa_dias = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }
    return mapa_dias[datetime.now().weekday()]

# --- VISTA 1: DASHBOARD (Clases del día) ---
@asistencia_bp.route('/')
@login_required
def hoy():
    dia_hoy = obtener_dia_actual_espanol()
    
    # Buscar solo clases de hoy ordenadas por hora
    clases_hoy = Horario.query.filter_by(dia_semana=dia_hoy)\
        .order_by(Horario.hora_inicio).all()
        
    return render_template('asistencia/dashboard.html', 
                           clases=clases_hoy, 
                           dia=dia_hoy)

# --- VISTA 2: LISTA DE ALUMNOS (Para marcar) ---
@asistencia_bp.route('/clase/<int:horario_id>')
@login_required
def tomar_lista(horario_id):
    horario = Horario.query.get_or_404(horario_id)
    
    # 1. Obtener alumnos inscritos activos
    inscripciones = horario.inscripciones.filter_by(activo=True).all()
    
    # 2. Saber quién ya tiene asistencia HOY (Para deshabilitar el botón)
    fecha_hoy = datetime.now().date()
    asistencias_hoy = Asistencia.query.filter_by(
        horario_id=horario.id, 
        fecha=fecha_hoy
    ).all()
    
    # Crear un set de IDs de socios que ya vinieron
    socios_presentes_ids = {a.socio_id for a in asistencias_hoy}
    
    return render_template('asistencia/tomar_lista.html', 
                           horario=horario, 
                           inscripciones=inscripciones,
                           presentes=socios_presentes_ids,
                           asistencias_hoy=asistencias_hoy)

# --- API: PROCESAR EL CLIC (AJAX) ---
@asistencia_bp.route('/api/marcar', methods=['POST'])
@login_required
def marcar_asistencia():
    data = request.get_json()
    socio_id = data.get('socio_id')
    horario_id = data.get('horario_id')

    # 1. Obtener socio
    socio = Socio.query.get(socio_id)
    
    # 2. VALIDAR ESTATUS FINANCIERO
    es_activo, mensaje_estatus, _ = socio.get_estatus_financiero()
    
    if not es_activo:
        # Retornamos error 403 (Forbidden) con el mensaje
        return jsonify({'status': 'error', 'msg': f'⛔ DEUDOR: {mensaje_estatus}'}), 403
    
    # Recibimos el estado (si no viene, asumimos Presente)
    nuevo_estado = data.get('estado', 'Presente')

    fecha_hoy = datetime.now().date()

    # 1. Buscar si ya existe registro hoy
    asistencia = Asistencia.query.filter_by(
        socio_id=socio_id, 
        horario_id=horario_id, 
        fecha=fecha_hoy
    ).first()
    
    if asistencia:
        # SI YA EXISTE: Actualizamos el estado (Corregir error)
        asistencia.estado = nuevo_estado
        msg = 'Actualizado'
    else:
        # SI NO EXISTE: Creamos uno nuevo
        asistencia = Asistencia(
            socio_id=socio_id,
            horario_id=horario_id,
            fecha=fecha_hoy,
            estado=nuevo_estado
        )
        db.session.add(asistencia)
        msg = 'Registrado'
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': msg, 'estado': nuevo_estado}), 200