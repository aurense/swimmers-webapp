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
    
    # 1. Obtener datos de la petición
    socio_id = data.get('socio_id')
    concepto = data.get('concepto')
    
    # 2. Validar Socio
    socio = Socio.query.get(socio_id)
    if not socio:
        return jsonify({'error': 'Socio no encontrado'}), 404

    # 3. Buscar la Tarifa (Cruce de Membresía + Nivel)
    tarifa = Tarifa.query.filter_by(
        membresia_id=socio.membresia_id, 
        nivel_id=socio.nivel_id
    ).first()

    # Valores por defecto
    precio = 0.0
    detalle_sugerido = ""
    
    # Helper para meses en español
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    fecha_hoy = datetime.now()

    # 4. Lógica de Precios
    if tarifa:
        if concepto == 'Mensualidad':
            precio = tarifa.costo_mensual
            # Generar "Diciembre 2025"
            nombre_mes = meses[fecha_hoy.month]
            detalle_sugerido = f"{nombre_mes} {fecha_hoy.year}"
            
        elif concepto == 'Anualidad':
            precio = tarifa.costo_anualidad
            detalle_sugerido = f"Anualidad {fecha_hoy.year}"
            
        elif concepto == 'Inscripción':
            precio = tarifa.costo_inscripcion
            detalle_sugerido = "Inscripción Nuevo Ingreso"
            
    # Nota: Si concepto es 'Producto', precio se queda en 0.0 para llenado manual

    return jsonify({
        'precio_sugerido': float(precio), # Aseguramos formato numérico
        'detalle_sugerido': detalle_sugerido
    })

# --- RUTA DE INTERFAZ ---
@finanzas_bp.route('/cobrar/<int:socio_id>', methods=['GET', 'POST'])
@login_required
def cobrar(socio_id):
    socio = Socio.query.get_or_404(socio_id)
    
    if request.method == 'POST':
        monto_base = float(request.form.get('monto') or 0)
        descuento = float(request.form.get('descuento') or 0)
        
        # El ajuste es negativo si es descuento
        monto_ajuste = -descuento 
        
        # El total es Base - Descuento
        total_cobrado = monto_base - descuento
        
        nuevo_pago = Pago(
            folio_recibo=f"REC-{int(datetime.now().timestamp())}",
            socio_id=socio.id,
            concepto_tipo=request.form.get('concepto'),
            detalle_concepto=request.form.get('detalle'),
            
            monto_base=monto_base,
            monto_ajuste=monto_ajuste, # Guardamos -50.00
            total_cobrado=total_cobrado, # Guardamos 750.00
            
            metodo_pago=request.form.get('metodo_pago'),
            requiere_factura=(request.form.get('factura') == 'on')
        )
        
        db.session.add(nuevo_pago)
        db.session.commit()
        
        flash(f'Pago registrado. Total cobrado: ${total_cobrado}', 'success')
        return redirect(url_for('socios.lista'))

    return render_template('finanzas/cobrar.html', socio=socio)


@finanzas_bp.route('/recibo/<int:id>')
@login_required
def ver_recibo(id):
    pago = Pago.query.get_or_404(id)
    # Renderizamos una plantilla dedicada EXCLUSIVA para impresión
    return render_template('finanzas/recibo_print.html', pago=pago)
