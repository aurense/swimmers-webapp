from flask import Blueprint, render_template, redirect, url_for, flash, request
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
    # Obtenemos todas las clases activas del socio
    inscripciones_activas = Inscripcion.query.filter_by(socio_id=socio_id, activo=True).all()
    
    for insc in inscripciones_activas:
        existente = insc.horario
        
        # --- NUEVA LÓGICA ESTRICTA ---
        # Si el día de la nueva clase es igual al día de una clase que ya tiene...
        if existente.dia_semana == nuevo_horario.dia_semana:
            # ... Bloqueamos la inscripción inmediatamente.
            return False, f"El socio ya tiene una clase registrada los {existente.dia_semana} ({existente.hora_inicio.strftime('%H:%M')}). Debe darla de baja primero si desea cambiar el horario."
            
    return True, "OK"

# --- RUTAS ---

@academico_bp.route('/inscribir/<int:socio_id>', methods=['GET', 'POST'])
@login_required
def inscribir(socio_id):
    socio = Socio.query.get_or_404(socio_id)
    
    # --- NUEVA VALIDACIÓN DE ESTATUS ---
    es_activo, mensaje_estatus, _ = socio.get_estatus_financiero()

    # PROCESAR INSCRIPCIÓN (POST)
    if request.method == 'POST':
        # 0. BLOQUEO POR MOROSIDAD
        if not es_activo:
            flash(f'⛔ BLOQUEO: No se puede inscribir. {mensaje_estatus}.', 'danger')
            return redirect(url_for('academico.inscribir', socio_id=socio.id))
        horario_id = request.form.get('horario_id')
        horario = Horario.query.get(horario_id)
        
        # 1. Validar Cupo
        if horario.cupos_disponibles() <= 0:
            flash('Error: La clase seleccionada ya está llena.', 'danger')
            return redirect(url_for('academico.inscribir', socio_id=socio.id))

        # 2. Validar Membresía (Límite de clases)
        clases_actuales = Inscripcion.query.filter_by(socio_id=socio.id, activo=True).count()
        if clases_actuales >= socio.membresia.clases_por_semana:
            flash(f'Error: El plan {socio.membresia.nombre} solo permite {socio.membresia.clases_por_semana} clases.', 'warning')
            return redirect(url_for('academico.inscribir', socio_id=socio.id))

        # 3. Validar Regla de "Una clase por día"
        es_valido, msg = validar_reglas_dia(socio.id, horario) # <--- Usar la nueva función
        
        if not es_valido:
            flash(f'Error: {msg}', 'danger')
            return redirect(url_for('academico.inscribir', socio_id=socio.id))

        # SI PASA TODO -> GUARDAR
        nueva_inscripcion = Inscripcion(socio_id=socio.id, horario_id=horario.id)
        db.session.add(nueva_inscripcion)
        db.session.commit()
        
        flash('Inscripción realizada correctamente.', 'success')
        return redirect(url_for('socios.lista'))

    # MOSTRAR CALENDARIO DE SELECCIÓN (GET)
    # 1. Obtener clases actuales ACTIVAS para mostrarlas arriba
    clases_actuales = Inscripcion.query.filter_by(socio_id=socio.id, activo=True).all()

    # Filtramos: Solo horarios del nivel del socio (Niño vs Adulto)
    horarios_disponibles = Horario.query.filter_by(nivel=socio.nivel).order_by(Horario.hora_inicio).all()
    
    # Agrupar por día (similar al paso 5, pero filtrado)
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    agenda = {dia: [] for dia in orden_dias}
    
    for h in horarios_disponibles:
        if h.dia_semana in agenda:
            agenda[h.dia_semana].append(h)
            
    return render_template('academico/inscribir.html', socio=socio, agenda=agenda, clases_actuales=clases_actuales)

@academico_bp.route('/baja/<int:inscripcion_id>')
@login_required
def baja(inscripcion_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    
    # Marcamos como inactivo (libera cupo inmediatamente gracias a la lógica de modelos)
    inscripcion.activo = False
    db.session.commit()
    
    flash('Clase cancelada. El cupo ha sido liberado.', 'info')
    
    # Redirigir a la pantalla de inscripción del socio dueño de esa clase
    return redirect(url_for('academico.inscribir', socio_id=inscripcion.socio_id))