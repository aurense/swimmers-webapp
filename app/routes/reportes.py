from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models import Pago, Asistencia, Socio, Horario
from sqlalchemy import func, case
from datetime import date, datetime, timedelta

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/dashboard')
@login_required
def dashboard():
    hoy = date.today()
    
    # 1. KPIs PRINCIPALES (Tarjetas Superiores)
    
    # A. Ingresos de HOY
    ingresos_hoy = db.session.query(func.sum(Pago.total_cobrado))\
        .filter(func.date(Pago.fecha_pago) == hoy).scalar() or 0
        
    # B. Asistencias de HOY
    asistencias_hoy = Asistencia.query.filter_by(fecha=hoy).count()
    
    # C. Alumnos Activos (Total)
    total_alumnos = Socio.query.count() # O filtra por estatus si implementaste soft delete

    # 2. GRÁFICA DE INGRESOS (Últimos 7 días)
    fecha_inicio_semana = hoy - timedelta(days=6)
    
    # Consulta agrupada por fecha
    datos_semana = db.session.query(
        func.date(Pago.fecha_pago), func.sum(Pago.total_cobrado)
    ).filter(func.date(Pago.fecha_pago) >= fecha_inicio_semana)\
     .group_by(func.date(Pago.fecha_pago)).all()
     
    # Formatear para Chart.js ([Labels], [Data])
    # Rellenar con 0 los días que no hubo ventas es ideal, pero simplificaremos:
    # chart_labels = [d[0].strftime('%d/%m') for d in datos_semana]
    chart_labels = [datetime.strptime(d[0], '%Y-%m-%d').strftime('%d/%m') for d in datos_semana]
    chart_values = [float(d[1]) for d in datos_semana]

    # 3. PRÓXIMAS CLASES (Del día de hoy)
    # Traducir día
    dias_map = {0:"Lunes", 1:"Martes", 2:"Miércoles", 3:"Jueves", 4:"Viernes", 5:"Sábado", 6:"Domingo"}
    dia_nombre = dias_map[hoy.weekday()]
    
    clases_hoy = Horario.query.filter_by(dia_semana=dia_nombre)\
        .order_by(Horario.hora_inicio).all()

    # 4. ÚLTIMOS 5 PAGOS (Tabla rápida)
    ultimos_pagos = Pago.query.order_by(Pago.fecha_pago.desc()).limit(5).all()

    return render_template('reportes/dashboard.html',
                           ingresos_hoy=ingresos_hoy,
                           asistencias_hoy=asistencias_hoy,
                           total_alumnos=total_alumnos,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           clases_hoy=clases_hoy,
                           ultimos_pagos=ultimos_pagos,
                           dia_actual=dia_nombre)