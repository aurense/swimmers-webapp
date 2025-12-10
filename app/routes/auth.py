from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.forms import LoginForm
from urllib.parse import urlsplit

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, mandarlo al dashboard según su rol
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('reportes.dashboard'))
        if current_user.role == 'instructor':
            return redirect(url_for('asistencia.hoy'))
        return redirect(url_for('socios.lista'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Validar usuario y contraseña
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # Manejo de redirección segura (si venía de otra página)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            if user.role == 'admin':
                next_page = url_for('reportes.dashboard')
            elif user.role == 'instructor':
                next_page = url_for('asistencia.hoy')
            else:
                next_page = url_for('socios.lista')
        return redirect(next_page)
        
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))