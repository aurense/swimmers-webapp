from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Horario, Asistencia, Inscripcion
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
                           presentes=socios_presentes_ids)

# --- API: PROCESAR EL CLIC (AJAX) ---
@asistencia_bp.route('/api/marcar', methods=['POST'])
@login_required
def marcar_asistencia():
    data = request.get_json()
    socio_id = data.get('socio_id')
    horario_id = data.get('horario_id')
    
    fecha_hoy = datetime.now().date()
    
    # Verificar si ya existe para evitar duplicados
    existe = Asistencia.query.filter_by(
        socio_id=socio_id, 
        horario_id=horario_id, 
        fecha=fecha_hoy
    ).first()
    
    if existe:
        return jsonify({'status': 'duplicated', 'msg': 'Ya registrado'}), 200
        
    # Crear registro
    nueva_asistencia = Asistencia(
        socio_id=socio_id,
        horario_id=horario_id,
        fecha=fecha_hoy,
        estado='Presente'
    )
    
    db.session.add(nueva_asistencia)
    db.session.commit()
    
    return jsonify({'status': 'success'}), 200