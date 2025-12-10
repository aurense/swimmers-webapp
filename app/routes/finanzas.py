from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models import Socio, Pago, Tarifa
from datetime import datetime
from flask_login import login_required

finanzas_bp = Blueprint('finanzas', __name__, url_prefix='/finanzas')

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

    # Buscar la tarifa correspondiente a su membresía y nivel
    tarifa = Tarifa.query.filter_by(
        membresia_id=socio.membresia_id, 
        nivel=socio.nivel
    ).first()

    precio = 0
    detalle_sugerido = ""

    if tarifa:
        if concepto == 'Mensualidad':
            precio = tarifa.costo_mensual
            # Sugerir mes actual: "Diciembre 2025"
            detalle_sugerido = datetime.now().strftime("%B %Y")
        elif concepto == 'Anualidad':
            precio = tarifa.costo_anualidad
            detalle_sugerido = f"Anualidad {datetime.now().year}"
        elif concepto == 'Inscripción':
            precio = tarifa.costo_inscripcion
            detalle_sugerido = "Inscripción Nuevo Ingreso"

    return jsonify({
        'precio_sugerido': precio,
        'detalle_sugerido': detalle_sugerido
    })

# --- RUTA DE INTERFAZ ---
@finanzas_bp.route('/cobrar/<int:socio_id>', methods=['GET', 'POST'])
@login_required
def cobrar(socio_id):
    socio = Socio.query.get_or_404(socio_id)
    
    if request.method == 'POST':
        # Recibir datos del formulario
        nuevo_pago = Pago(
            folio_recibo=f"REC-{int(datetime.now().timestamp())}", # Generar folio simple basado en tiempo
            socio_id=socio.id,
            concepto_tipo=request.form.get('concepto'),
            detalle_concepto=request.form.get('detalle'),
            monto_base=float(request.form.get('monto')),
            total_cobrado=float(request.form.get('monto')), # Aquí podrías restar descuentos si agregas el campo
            metodo_pago=request.form.get('metodo_pago'),
            requiere_factura=(request.form.get('factura') == 'on')
        )
        
        db.session.add(nuevo_pago)
        db.session.commit()
        
        flash('Pago registrado correctamente.', 'success')
        return redirect(url_for('socios.lista'))

    return render_template('finanzas/cobrar.html', socio=socio)