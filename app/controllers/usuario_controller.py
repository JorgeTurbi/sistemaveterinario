"""
Controlador de Usuarios
CRUD para la gestion de usuarios del sistema
Solo accesible por administradores
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.usuario import Usuario
from app.models.veterinario import Veterinario

usuario_bp = Blueprint('usuarios', __name__)


def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'Administrador':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@usuario_bp.route('/')
@login_required
@admin_required
def index():
    """Lista todos los usuarios"""
    # Filtros
    rol = request.args.get('rol', '')
    estado = request.args.get('estado', '')
    buscar = request.args.get('buscar', '').strip()

    query = Usuario.query

    if rol:
        query = query.filter_by(rol=rol)

    if estado == 'activo':
        query = query.filter_by(activo=True)
    elif estado == 'inactivo':
        query = query.filter_by(activo=False)

    if buscar:
        query = query.filter(
            db.or_(
                Usuario.username.ilike(f'%{buscar}%'),
                Usuario.nombre_completo.ilike(f'%{buscar}%'),
                Usuario.email.ilike(f'%{buscar}%')
            )
        )

    usuarios = query.order_by(Usuario.nombre_completo).all()

    # Estadisticas
    total_usuarios = Usuario.query.count()
    usuarios_activos = Usuario.query.filter_by(activo=True).count()
    admins = Usuario.query.filter_by(rol='Administrador', activo=True).count()
    veterinarios = Usuario.query.filter_by(rol='Veterinario', activo=True).count()
    recepcionistas = Usuario.query.filter_by(rol='Recepcionista', activo=True).count()

    return render_template('usuarios/index.html',
                         usuarios=usuarios,
                         total_usuarios=total_usuarios,
                         usuarios_activos=usuarios_activos,
                         admins=admins,
                         veterinarios=veterinarios,
                         recepcionistas=recepcionistas,
                         rol_filtro=rol,
                         estado_filtro=estado,
                         buscar=buscar)


@usuario_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Crear nuevo usuario"""
    veterinarios_disponibles = Usuario.get_veterinarios_sin_usuario()

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        nombre_completo = request.form.get('nombre_completo', '').strip()
        email = request.form.get('email', '').strip().lower()
        rol = request.form.get('rol', 'Recepcionista')
        activo = request.form.get('activo') == 'on'
        vincular_veterinario = request.form.get('vincular_veterinario', type=int)

        # Validaciones
        errores = []

        if not username or len(username) < 3:
            errores.append('El nombre de usuario debe tener al menos 3 caracteres.')

        if not password or len(password) < 6:
            errores.append('La contrasena debe tener al menos 6 caracteres.')

        if password != confirm_password:
            errores.append('Las contrasenas no coinciden.')

        if not nombre_completo:
            errores.append('El nombre completo es requerido.')

        if not email or '@' not in email:
            errores.append('El email no es valido.')

        # Verificar duplicados
        if Usuario.query.filter_by(username=username).first():
            errores.append('El nombre de usuario ya existe.')

        if Usuario.query.filter_by(email=email).first():
            errores.append('El email ya esta registrado.')

        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('usuarios/create.html',
                                 veterinarios_disponibles=veterinarios_disponibles,
                                 roles=Usuario.ROLES)

        # Crear usuario
        usuario = Usuario(
            username=username,
            nombre_completo=nombre_completo,
            email=email,
            rol=rol,
            activo=activo
        )
        usuario.set_password(password)

        try:
            db.session.add(usuario)
            db.session.flush()  # Para obtener el ID

            # Vincular con veterinario si se selecciono
            if vincular_veterinario and rol == 'Veterinario':
                veterinario = Veterinario.query.get(vincular_veterinario)
                if veterinario:
                    veterinario.id_usuario = usuario.id_usuario

            db.session.commit()
            flash(f'Usuario "{username}" creado exitosamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')

    return render_template('usuarios/create.html',
                         veterinarios_disponibles=veterinarios_disponibles,
                         roles=Usuario.ROLES)


@usuario_bp.route('/<int:id>')
@login_required
@admin_required
def show(id):
    """Ver detalle de usuario"""
    usuario = Usuario.query.get_or_404(id)
    return render_template('usuarios/show.html', usuario=usuario)


@usuario_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Editar usuario"""
    usuario = Usuario.query.get_or_404(id)
    veterinarios_disponibles = Usuario.get_veterinarios_sin_usuario()

    # Agregar el veterinario actual si existe
    if usuario.veterinario:
        veterinarios_disponibles.insert(0, usuario.veterinario)

    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo', '').strip()
        email = request.form.get('email', '').strip().lower()
        rol = request.form.get('rol', 'Recepcionista')
        activo = request.form.get('activo') == 'on'
        nueva_password = request.form.get('nueva_password', '')
        vincular_veterinario = request.form.get('vincular_veterinario', type=int)

        # Validaciones
        errores = []

        if not nombre_completo:
            errores.append('El nombre completo es requerido.')

        if not email or '@' not in email:
            errores.append('El email no es valido.')

        # Verificar email duplicado (excluyendo el actual)
        email_existente = Usuario.query.filter(
            Usuario.email == email,
            Usuario.id_usuario != id
        ).first()
        if email_existente:
            errores.append('El email ya esta registrado por otro usuario.')

        # No permitir desactivar el ultimo admin
        if usuario.rol == 'Administrador' and (rol != 'Administrador' or not activo):
            admins_activos = Usuario.query.filter(
                Usuario.rol == 'Administrador',
                Usuario.activo == True,
                Usuario.id_usuario != id
            ).count()
            if admins_activos == 0:
                errores.append('No se puede desactivar o cambiar el rol del unico administrador activo.')

        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('usuarios/edit.html',
                                 usuario=usuario,
                                 veterinarios_disponibles=veterinarios_disponibles,
                                 roles=Usuario.ROLES)

        # Actualizar datos
        usuario.nombre_completo = nombre_completo
        usuario.email = email
        usuario.rol = rol
        usuario.activo = activo

        # Actualizar password si se proporciono
        if nueva_password and len(nueva_password) >= 6:
            usuario.set_password(nueva_password)

        # Gestionar vinculacion con veterinario
        # Primero desvincular el anterior si existe
        if usuario.veterinario:
            usuario.veterinario.id_usuario = None

        # Vincular nuevo si se selecciono
        if vincular_veterinario and rol == 'Veterinario':
            veterinario = Veterinario.query.get(vincular_veterinario)
            if veterinario:
                veterinario.id_usuario = usuario.id_usuario

        try:
            db.session.commit()
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    return render_template('usuarios/edit.html',
                         usuario=usuario,
                         veterinarios_disponibles=veterinarios_disponibles,
                         roles=Usuario.ROLES)


@usuario_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_activo(id):
    """Activar/Desactivar usuario"""
    usuario = Usuario.query.get_or_404(id)

    # No permitir desactivarse a si mismo
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes desactivar tu propia cuenta.', 'warning')
        return redirect(url_for('usuarios.index'))

    # No permitir desactivar el ultimo admin
    if usuario.rol == 'Administrador' and usuario.activo:
        admins_activos = Usuario.query.filter(
            Usuario.rol == 'Administrador',
            Usuario.activo == True,
            Usuario.id_usuario != id
        ).count()
        if admins_activos == 0:
            flash('No se puede desactivar al unico administrador activo.', 'danger')
            return redirect(url_for('usuarios.index'))

    usuario.activo = not usuario.activo
    estado = 'activado' if usuario.activo else 'desactivado'

    try:
        db.session.commit()
        flash(f'Usuario {estado} exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('usuarios.index'))


@usuario_bp.route('/<int:id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(id):
    """Resetear contrasena de usuario"""
    usuario = Usuario.query.get_or_404(id)

    # Generar contrasena temporal (el username + "123")
    nueva_password = usuario.username + '123'
    usuario.set_password(nueva_password)

    try:
        db.session.commit()
        flash(f'Contrasena reseteada. Nueva contrasena temporal: {nueva_password}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('usuarios.edit', id=id))


@usuario_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Eliminar usuario (soft delete - solo desactiva)"""
    usuario = Usuario.query.get_or_404(id)

    # No permitir eliminarse a si mismo
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes eliminar tu propia cuenta.', 'warning')
        return redirect(url_for('usuarios.index'))

    # No permitir eliminar el ultimo admin
    if usuario.rol == 'Administrador':
        admins = Usuario.query.filter(
            Usuario.rol == 'Administrador',
            Usuario.id_usuario != id
        ).count()
        if admins == 0:
            flash('No se puede eliminar al unico administrador.', 'danger')
            return redirect(url_for('usuarios.index'))

    # Soft delete
    usuario.activo = False

    try:
        db.session.commit()
        flash(f'Usuario "{usuario.username}" eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('usuarios.index'))
