"""
Controlador de Autenticación
Maneja login, logout y registro de usuarios
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña.', 'warning')
            return render_template('auth/login.html')
        
        usuario = Usuario.get_by_username(username)
        
        if usuario is None or not usuario.check_password(password):
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('auth/login.html')
        
        if not usuario.activo:
            flash('Esta cuenta está desactivada.', 'warning')
            return render_template('auth/login.html')
        
        # Iniciar sesión
        login_user(usuario, remember=remember)
        usuario.actualizar_acceso()
        
        flash(f'¡Bienvenido, {usuario.nombre_completo}!', 'success')
        
        # Redirigir a la página solicitada o al dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios (solo si no hay usuarios o es admin)"""
    # Verificar si hay usuarios en el sistema
    hay_usuarios = Usuario.query.count() > 0
    
    # Si hay usuarios, solo admins pueden registrar
    if hay_usuarios and (not current_user.is_authenticated or not current_user.es_admin):
        flash('Solo los administradores pueden registrar nuevos usuarios.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        nombre = request.form.get('nombre_completo', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        rol = request.form.get('rol', Usuario.ROL_RECEPCIONISTA)
        
        # Validaciones
        errores = []
        
        if not username or len(username) < 3:
            errores.append('El usuario debe tener al menos 3 caracteres.')
        
        if not email or '@' not in email:
            errores.append('Ingresa un email válido.')
        
        if not nombre:
            errores.append('El nombre completo es requerido.')
        
        if not password or len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        
        if password != password2:
            errores.append('Las contraseñas no coinciden.')
        
        if Usuario.query.filter_by(username=username).first():
            errores.append('Este nombre de usuario ya está en uso.')
        
        if Usuario.query.filter_by(email=email).first():
            errores.append('Este email ya está registrado.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('auth/register.html', roles=Usuario.ROLES)
        
        # Crear usuario
        # El primer usuario siempre es admin
        if not hay_usuarios:
            rol = Usuario.ROL_ADMIN
        
        usuario = Usuario(
            username=username,
            email=email,
            nombre_completo=nombre,
            rol=rol
        )
        usuario.set_password(password)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash(f'Usuario {username} creado exitosamente.', 'success')
            
            if not hay_usuarios:
                flash('¡Eres el primer usuario! Se te ha asignado rol de Administrador.', 'info')
                return redirect(url_for('auth.login'))
            
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')
    
    return render_template('auth/register.html', roles=Usuario.ROLES)


@auth_bp.route('/profile')
@login_required
def profile():
    """Ver perfil del usuario actual"""
    return render_template('auth/profile.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'warning')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Contraseña actualizada correctamente.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')
