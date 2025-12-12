
import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Socio, Membresia, Pago, Asistencia, Nivel
from app.forms import SocioForm
from flask_login import login_required
from werkzeug.utils import secure_filename

def guardar_foto(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn

socios_bp = Blueprint('socios', __name__, url_prefix='/socios')

@socios_bp.route('/')
@login_required
def lista():
    socios = Socio.query.order_by(Socio.id.desc()).all()
    return render_template('socios/lista.html', socios=socios)

@socios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def crear():
    form = SocioForm()
    niveles_db = Nivel.query.order_by(Nivel.orden).all()
    form.nivel.choices = [(n.nombre, n.nombre) for n in niveles_db]
    form.membresia_id.choices = [(m.id, m.nombre) for m in Membresia.query.all()]

    if form.validate_on_submit():
        nombre_archivo_foto = 'default.png'
        if form.foto.data:
            nombre_archivo_foto = guardar_foto(form.foto.data)

        ultimo_socio = Socio.query.order_by(Socio.id.desc()).first()
        nuevo_id = ultimo_socio.id + 1 if ultimo_socio else 1
        folio_generado = f"SW{nuevo_id:04d}"

        nivel_obj = Nivel.query.filter_by(nombre=form.nivel.data).first()
        if not nivel_obj:
            flash(f"Nivel '{form.nivel.data}' no encontrado.", "danger")
            return render_template('socios/crear.html', form=form)

        nuevo_socio = Socio(
            folio=folio_generado,
            nombre_completo=form.nombre_completo.data,
            email=form.email.data,
            telefono=form.telefono.data,
            nivel=nivel_obj, 
            membresia_id=form.membresia_id.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            foto=nombre_archivo_foto
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
    form = SocioForm(obj=socio)
    form.membresia_id.choices = [(m.id, m.nombre) for m in Membresia.query.all()]
    niveles_db = Nivel.query.order_by(Nivel.orden).all()
    form.nivel.choices = [(n.nombre, n.nombre) for n in niveles_db]

    if form.validate_on_submit():
        socio.nombre_completo = form.nombre_completo.data
        socio.email = form.email.data
        socio.telefono = form.telefono.data

        nivel_obj = Nivel.query.filter_by(nombre=form.nivel.data).first()
        if nivel_obj:
            socio.nivel = nivel_obj
        else:
            flash(f"Nivel '{form.nivel.data}' no encontrado.", "danger")
            return redirect(url_for('socios.editar', id=id))

        socio.membresia_id = form.membresia_id.data
        socio.fecha_nacimiento = form.fecha_nacimiento.data

        if form.foto.data and hasattr(form.foto.data, 'filename'):
            nombre_archivo = guardar_foto(form.foto.data)
            socio.foto = nombre_archivo

        db.session.commit()
        flash('Información del socio actualizada correctamente.', 'success')
        return redirect(url_for('socios.lista'))
    elif request.method == 'GET':
        if socio.nivel:
            form.nivel.data = socio.nivel.nombre

    return render_template('socios/crear.html', form=form, titulo="Editar Socio")

@socios_bp.route('/perfil/<int:id>')
@login_required
def perfil(id):
    socio = Socio.query.get_or_404(id)
    pagos = socio.pagos.order_by(Pago.fecha_pago.desc()).all()
    asistencias = socio.asistencias.order_by(Asistencia.fecha.desc()).limit(50).all()
    ultimo_pago_mes = Pago.query.filter_by(socio_id=socio.id, concepto_tipo='Mensualidad').order_by(Pago.fecha_pago.desc()).first()

    estatus = "Nuevo / Sin Pagos"
    color_estatus = "secondary"

    if ultimo_pago_mes:
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

    return render_template('socios/perfil.html', socio=socio, pagos=pagos, asistencias=asistencias, estatus=estatus, color_estatus=color_estatus)

@socios_bp.route('/api/buscar', methods=['GET'])
@login_required
def buscar_api():
    query = request.args.get('q', '').strip()
    if len(query) < 3:
        return jsonify([])

    # Buscar por Nombre o Folio
    socios = Socio.query.filter(
        (Socio.nombre_completo.ilike(f'%{query}%')) | 
        (Socio.folio.ilike(f'%{query}%'))
    ).limit(5).all()
    
    resultados = []
    for s in socios:
        es_activo, msg, color = s.get_estatus_financiero()
        resultados.append({
            'id': s.id,
            'nombre': s.nombre_completo,
            'folio': s.folio,
            'foto': s.foto or 'default.png',
            'es_activo': es_activo,
            'msg_estatus': msg
        })
        
    return jsonify(resultados)
