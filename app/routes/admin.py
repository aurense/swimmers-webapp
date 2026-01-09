from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Horario, Tarifa, User, Membresia, Nivel
from app.forms import HorarioForm, TarifaForm, MembresiaForm, NivelForm
from app.decorators import admin_required
from collections import defaultdict

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- DASHBOARD ADMIN ---
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/asistencia_recepcion')
@login_required
@admin_required
def asistencia_recepcion():
    return render_template('asistencia/recepcion.html')

# --- GESTIÓN DE HORARIOS ---
@admin_bp.route('/horarios', methods=['GET', 'POST'])
@login_required
@admin_required
def horarios():
    lista_horarios = Horario.query.order_by(Horario.dia_semana, Horario.hora_inicio).all()
    form = HorarioForm()
    niveles_db = Nivel.query.order_by(Nivel.orden).all()
    form.nivel_id.choices = [(n.id, n.nombre) for n in niveles_db]
    
    if form.validate_on_submit():
        h = Horario(
            dia_semana=form.dia_semana.data,
            hora_inicio=form.hora_inicio.data,
            hora_fin=form.hora_fin.data,
            nivel_id=form.nivel_id.data,
            capacidad_maxima=form.capacidad_maxima.data
        )
        db.session.add(h)
        db.session.commit()
        flash('Nuevo horario agregado correctamente.', 'success')
        return redirect(url_for('admin.horarios'))
        
    return render_template('admin/horarios.html', horarios=lista_horarios, form=form)

@admin_bp.route('/horarios/borrar/<int:id>')
@login_required
@admin_required
def borrar_horario(id):
    h = Horario.query.get_or_404(id)
    
    inscritos = h.inscripciones.filter_by(activo=True).count()
    if inscritos > 0:
        flash(f'ERROR: No se puede borrar esta clase. Tiene {inscritos} alumnos inscritos.', 'danger')
    else:
        db.session.delete(h)
        db.session.commit()
        flash('Horario eliminado.', 'info')
        
    return redirect(url_for('admin.horarios'))

# --- GESTIÓN DE PRECIOS (TARIFAS) ---
@admin_bp.route('/tarifas')
@login_required
@admin_required
def lista_tarifas():
    tarifas = Tarifa.query.options(db.joinedload(Tarifa.membresia), db.joinedload(Tarifa.nivel)).order_by(Tarifa.membresia_id, Tarifa.nivel_id).all()
    
    tarifas_por_membresia = defaultdict(list)
    for t in tarifas:
        tarifas_por_membresia[t.membresia].append(t)
        
    return render_template('admin/tarifas_lista.html', tarifas_por_membresia=tarifas_por_membresia)

@admin_bp.route('/tarifas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_tarifa(id):
    tarifa = Tarifa.query.get_or_404(id)
    form = TarifaForm(obj=tarifa)
    
    # Populate choices for dropdowns
    form.membresia_id.choices = [(m.id, m.nombre) for m in Membresia.query.all()]
    form.nivel_id.choices = [(0, 'General (Sin Nivel)')] + [(n.id, n.nombre) for n in Nivel.query.all()]

    if form.validate_on_submit():
        # The 'membresia_id' and 'nivel_id' are not meant to be changed on edit,
        # so we only update the cost fields.
        tarifa.costo_mensual = form.costo_mensual.data
        tarifa.costo_anualidad = form.costo_anualidad.data
        tarifa.costo_inscripcion = form.costo_inscripcion.data
        
        db.session.commit()
        flash('Precios actualizados.', 'success')
        return redirect(url_for('admin.lista_tarifas'))
        
    # Set the initial values for the form fields
    form.costo_mensual.data = tarifa.costo_mensual
    form.costo_anualidad.data = tarifa.costo_anualidad
    form.costo_inscripcion.data = tarifa.costo_inscripcion
    
    return render_template('admin/tarifa_editar.html', form=form, tarifa=tarifa)

@admin_bp.route('/tarifas/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_tarifa():
    form = TarifaForm()
    
    # Llenar Selects
    membresias = Membresia.query.order_by(Membresia.nombre).all()
    niveles = Nivel.query.order_by(Nivel.orden).all()
    form.membresia_id.choices = [(m.id, m.nombre) for m in membresias]
    # Opción para tarifa general (sin nivel)
    form.nivel_id.choices = [(0, 'General (Para todos los niveles)')] + [(n.id, n.nombre) for n in niveles]
    
    if form.validate_on_submit():
        nivel_id_seleccionado = form.nivel_id.data
        
        # Convertir "0" a None para la BD
        id_para_db = None if nivel_id_seleccionado == 0 else nivel_id_seleccionado

        # Validar si ya existe la combinación
        existe = Tarifa.query.filter_by(
            membresia_id=form.membresia_id.data,
            nivel_id=id_para_db
        ).first()

        if existe:
            flash('Error: Ya existe una tarifa para esa combinación de Membresía y Nivel.', 'danger')
        else:
            nueva = Tarifa(
                membresia_id=form.membresia_id.data,
                nivel_id=id_para_db,
                costo_mensual=form.costo_mensual.data,
                costo_anualidad=form.costo_anualidad.data,
                costo_inscripcion=form.costo_inscripcion.data
            )
            db.session.add(nueva)
            db.session.commit()
            flash('Nueva tarifa registrada correctamente.', 'success')
            return redirect(url_for('admin.lista_tarifas'))
            
    return render_template('admin/tarifa_crear.html', form=form)

# --- GESTIÓN DE MEMBRESÍAS ---

@admin_bp.route('/membresias')
@login_required
@admin_required
def membresias():
    lista = Membresia.query.order_by(Membresia.clases_por_semana).all()
    return render_template('admin/membresias_lista.html', membresias=lista)

@admin_bp.route('/membresias/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_membresia():
    form = MembresiaForm()
    if form.validate_on_submit():
        nueva = Membresia(
            nombre=form.nombre.data,
            clases_por_semana=form.clases_por_semana.data
        )
        db.session.add(nueva)
        db.session.commit()
        flash('Nuevo plan creado. Recuerda asignarle Tarifas.', 'success')
        return redirect(url_for('admin.membresias'))
        
    return render_template('admin/membresia_form.html', form=form, titulo="Crear Membresía")

@admin_bp.route('/membresias/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_membresia(id):
    plan = Membresia.query.get_or_404(id)
    form = MembresiaForm(obj=plan)
    
    if form.validate_on_submit():
        form.populate_obj(plan)
        db.session.commit()
        flash('Plan actualizado correctamente.', 'success')
        return redirect(url_for('admin.membresias'))
        
    return render_template('admin/membresia_form.html', form=form, titulo="Editar Membresía")

# --- GESTIÓN DE NIVELES ---

@admin_bp.route('/niveles')
@login_required
@admin_required
def niveles():
    lista = Nivel.query.order_by(Nivel.orden).all()
    return render_template('admin/niveles_lista.html', niveles=lista)

@admin_bp.route('/niveles/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_nivel():
    form = NivelForm()
    if form.validate_on_submit():
        existe = Nivel.query.filter_by(nombre=form.nombre.data).first()
        if existe:
            flash('Error: Ya existe un nivel con ese nombre.', 'danger')
        else:
            nuevo = Nivel(nombre=form.nombre.data, orden=form.orden.data)
            db.session.add(nuevo)
            db.session.commit()
            flash('Nivel creado correctamente.', 'success')
            return redirect(url_for('admin.niveles'))
    return render_template('admin/nivel_form.html', form=form, titulo="Nuevo Nivel")

@admin_bp.route('/niveles/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_nivel(id):
    nivel_obj = Nivel.query.get_or_404(id)
    form = NivelForm(obj=nivel_obj)
    
    if form.validate_on_submit():
        form.populate_obj(nivel_obj)
        db.session.commit()
        flash(f'Nivel "{nivel_obj.nombre}" actualizado correctamente.', 'success')
        return redirect(url_for('admin.niveles'))
        
    return render_template('admin/nivel_form.html', form=form, titulo="Editar Nivel")
