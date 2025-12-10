@admin_bp.route('/horarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_horario():
    form = HorarioForm() # Crear form con Hora Inicio, Fin, Día, Cupo
    if form.validate_on_submit():
        h = Horario(
            dia_semana=form.dia.data,
            hora_inicio=form.inicio.data,
            # ... resto de campos
        )
        db.session.add(h)
        db.session.commit()
        return redirect(url_for('horarios.calendario'))
    return render_template('admin/form_horario.html', form=form)

@admin_bp.route('/horarios/borrar/<int:id>')
@admin_required
def borrar_horario(id):
    h = Horario.query.get_or_404(id)
    # Validar que no tenga alumnos inscritos antes de borrar
    if h.inscripciones.filter_by(activo=True).count() > 0:
        flash("No se puede borrar una clase con alumnos activos.", "warning")
    else:
        db.session.delete(h)
        db.session.commit()
    return redirect(url_for('horarios.calendario'))