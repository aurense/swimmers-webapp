from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models import Socio, Pago, Tarifa
from app.forms import CobroForm
from datetime import datetime
from flask_login import login_required
from sqlalchemy import or_

finanzas_bp = Blueprint('finanzas', __name__, url_prefix='/finanzas')

@finanzas_bp.route('/cobro-rapido')
@login_required
def cobro_rapido():
    return render_template('finanzas/buscar_socio.html')

@finanzas_bp.route('/api/buscar_socio', methods=['POST'])
@login_required
def buscar_socio():
    data = request.get_json()
    search_term = data.get('search_term')
    if not search_term:
        return jsonify([])

    # Buscar socios por nombre o número de socio
    socios = Socio.query.filter(
        or_(
            Socio.nombre_completo.ilike(f'%{search_term}%'),
            Socio.folio.ilike(f'%{search_term}%')
        )
    ).limit(10).all()

    # Formatear la respuesta
    results = [
        {'id': socio.id, 'nombre_completo': socio.nombre_completo}
        for socio in socios
    ]
    return jsonify(results)


# --- API INTERNA (Para que el JavaScript consulte precios) ---
@finanzas_bp.route('/api/consultar_precio', methods=['POST'])
@login_required
def consultar_precio():
    data = request.get_json()
    socio_id = data.get('socio_id')
    concepto = data.get('concepto')

    socio = Socio.query.get(socio_id)
    if not socio:
        return jsonify({'error': 'Socio no encontrado'}), 404

    # Intenta buscar una tarifa específica para el nivel del socio
    tarifa = Tarifa.query.filter_by(
        membresia_id=socio.membresia_id,
        nivel_id=socio.nivel_id
    ).first()

    # Si no hay tarifa específica y el concepto es Inscripción o Anualidad,
    # busca una tarifa general para esa membresía (sin nivel específico)
    if not tarifa and concepto in ['Inscripción', 'Anualidad']:
        tarifa = Tarifa.query.filter_by(
            membresia_id=socio.membresia_id,
            nivel_id=None  # Asumiendo que tarifas generales tienen nivel_id=NULL
        ).first()

    precio = 0.0
    detalle_sugerido = ""

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    fecha_hoy = datetime.now()

    if tarifa:
        if concepto == 'Mensualidad':
            precio = tarifa.costo_mensual
            nombre_mes = meses[fecha_hoy.month]
            detalle_sugerido = f"{nombre_mes} {fecha_hoy.year}"
        elif concepto == 'Anualidad':
            precio = tarifa.costo_anualidad
            detalle_sugerido = f"Anualidad {fecha_hoy.year}"
        elif concepto == 'Inscripción':
            precio = tarifa.costo_inscripcion
            detalle_sugerido = "Inscripción Nuevo Ingreso"

    return jsonify({
        'precio_sugerido': float(precio),
        'detalle_sugerido': detalle_sugerido
    })

# --- RUTA DE INTERFAZ ---
@finanzas_bp.route('/cobrar/<int:socio_id>', methods=['GET', 'POST'])
@login_required
def cobrar(socio_id):
    socio = Socio.query.get_or_404(socio_id)
    form = CobroForm()

    if form.validate_on_submit():
        monto_base = float(form.monto.data)
        descuento = float(form.descuento.data)

        monto_ajuste = -descuento
        total_cobrado = monto_base - descuento

        nuevo_pago = Pago(
            folio_recibo=f"REC-{int(datetime.now().timestamp())}",
            socio_id=socio.id,
            concepto_tipo=form.concepto.data,
            detalle_concepto=form.detalle.data,

            monto_base=monto_base,
            monto_ajuste=monto_ajuste,
            total_cobrado=total_cobrado,

            metodo_pago=form.metodo_pago.data,
            requiere_factura=form.factura.data
        )

        db.session.add(nuevo_pago)
        db.session.commit()

        flash(f'Pago registrado. Total cobrado: ${total_cobrado}', 'success')
        return redirect(url_for('socios.lista'))

    return render_template('finanzas/cobrar.html', socio=socio, form=form)


@finanzas_bp.route('/recibo/<int:id>')
@login_required
def ver_recibo(id):
    pago = Pago.query.get_or_404(id)
    return render_template('finanzas/recibo_print.html', pago=pago)
