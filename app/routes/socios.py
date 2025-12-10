
from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime, timedelta
from app import db
from app.models import Socio, Membresia, Pago, Asistencia, Nivel
from app.forms import SocioForm
from flask_login import login_required


# Definir el "Blueprint" (agrupador de rutas)
socios_bp = Blueprint('socios', __name__, url_prefix='/socios')

@socios_bp.route('/')
@login_required
def lista():
    # Obtener todos los socios ordenados por ID reciente
    socios = Socio.query.order_by(Socio.id.desc()).all()
    return render_template('socios/lista.html', socios=socios)

@socios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def crear():
    form = SocioForm()

    # --- CARGA DINÁMICA DE NIVELES ---
    niveles_db = Nivel.query.order_by(Nivel.orden).all()
    form.nivel.choices = [(n.nombre, n.nombre) for n in niveles_db]
    # ---------------------------------
    
    # Llenar el select de membresías dinámicamente desde la BD
    form.membresia_id.choices = [(m.id, m.nombre) for m in Membresia.query.all()]

    if form.validate_on_submit():
        # --- LÓGICA DE FOLIO CONSECUTIVO ---
        ultimo_socio = Socio.query.order_by(Socio.id.desc()).first()
        if ultimo_socio:
            # Extraer el número del último folio (SW0005 -> 5) y sumar 1
            # O usar el ID directamente si confías en el autoincrement
            nuevo_id = ultimo_socio.id + 1
        else:
            nuevo_id = 1
            
        # Generar string SW0001
        folio_generado = f"SW{nuevo_id:04d}" 

        # Crear objeto
        nuevo_socio = Socio(
            folio=folio_generado,
            nombre_completo=form.nombre_completo.data,
            email=form.email.data,
            telefono=form.telefono.data,
            nivel=form.nivel.data,
            membresia_id=form.membresia_id.data
        )

        try:
            db.session.add(nuevo_socio)
            db.session.commit()
            flash(f'Socio registrado con éxito. Folio: {folio_generado}', 'success')
            return redirect(url_for('socios.lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')

    return render_template('socios/crear.html', form=form)

@socios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    socio = Socio.query.get_or_404(id)
    form = SocioForm(obj=socio) # Pre-llenar formulario con datos existentes
    
    # --- CARGA DINÁMICA DE NIVELES ---
    niveles_db = Nivel.query.order_by(Nivel.orden).all()
    form.nivel.choices = [(n.nombre, n.nombre) for n in niveles_db]
    # ---------------------------------
    
    # Llenar el select de membresías dinámicamente desde la BD
    form.membresia_id.choices = [(m.id, m.nombre) for m in Membresia.query.all()]

    if form.validate_on_submit():
        form.populate_obj(socio) # Actualizar objeto con datos del form
        db.session.commit()
        flash('Socio actualizado', 'success')
        return redirect(url_for('socios.lista'))
        
    return render_template('socios/crear.html', form=form, titulo="Editar Socio")

@socios_bp.route('/perfil/<int:id>')
@login_required
def perfil(id):
    socio = Socio.query.get_or_404(id)
    
    # 1. Obtener Historial de Pagos (Más recientes primero)
    pagos = socio.pagos.order_by(Pago.fecha_pago.desc()).all()
    
    # 2. Obtener Historial de Asistencia (Últimos 50 registros)
    asistencias = socio.asistencias.order_by(Asistencia.fecha.desc()).limit(50).all()
    
    # 3. CÁLCULO DE ESTATUS (Lógica de Negocio)
    # Buscamos el último pago de mensualidad
    ultimo_pago_mes = Pago.query.filter_by(socio_id=socio.id, concepto_tipo='Mensualidad')\
        .order_by(Pago.fecha_pago.desc()).first()
    
    estatus = "Nuevo / Sin Pagos"
    color_estatus = "secondary"
    
    if ultimo_pago_mes:
        # Calculamos días desde el último pago
        dias_transcurridos = (datetime.now() - ultimo_pago_mes.fecha_pago).days
        
        if dias_transcurridos <= 31:
            estatus = "Al Corriente"
            color_estatus = "success"
        elif dias_transcurridos <= 45:
            estatus = f"Pago Pendiente ({dias_transcurridos} días)"
            color_estatus = "warning"
        else:
            estatus = "MOROSO"
            color_estatus = "danger"

    return render_template('socios/perfil.html', 
                           socio=socio, 
                           pagos=pagos, 
                           asistencias=asistencias,
                           estatus=estatus,
                           color_estatus=color_estatus)