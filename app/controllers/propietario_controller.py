"""
Controlador de Propietarios
CRUD completo para la gestión de propietarios
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.propietario import Propietario

propietario_bp = Blueprint('propietarios', __name__)


@propietario_bp.route('/')
@login_required
def index():
    """Lista todos los propietarios"""
    busqueda = request.args.get('q', '')
    
    if busqueda:
        propietarios = Propietario.buscar(busqueda)
    else:
        propietarios = Propietario.get_activos()
    
    return render_template('propietarios/index.html', 
                         propietarios=propietarios,
                         busqueda=busqueda)


@propietario_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nuevo propietario"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        
        # Validaciones
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido.')
        
        if not documento:
            errores.append('El documento es requerido.')
        elif Propietario.query.filter_by(documento=documento).first():
            errores.append('Ya existe un propietario con este documento.')
        
        if not telefono:
            errores.append('El teléfono es requerido.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('propietarios/create.html')
        
        # Crear propietario
        propietario = Propietario(
            nombre=nombre,
            documento=documento,
            telefono=telefono,
            email=email if email else None,
            direccion=direccion if direccion else None
        )
        
        try:
            db.session.add(propietario)
            db.session.commit()
            flash(f'Propietario "{nombre}" creado exitosamente.', 'success')
            return redirect(url_for('propietarios.show', id=propietario.id_propietario))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear propietario: {str(e)}', 'danger')
    
    return render_template('propietarios/create.html')


@propietario_bp.route('/<int:id>')
@login_required
def show(id):
    """Ver detalle de un propietario"""
    propietario = Propietario.query.get_or_404(id)
    mascotas = propietario.mascotas.filter_by(activo=True).all()
    
    return render_template('propietarios/show.html', 
                         propietario=propietario,
                         mascotas=mascotas)


@propietario_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar propietario"""
    propietario = Propietario.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        
        # Validaciones
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido.')
        
        if not documento:
            errores.append('El documento es requerido.')
        else:
            existente = Propietario.query.filter_by(documento=documento).first()
            if existente and existente.id_propietario != id:
                errores.append('Ya existe otro propietario con este documento.')
        
        if not telefono:
            errores.append('El teléfono es requerido.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('propietarios/edit.html', propietario=propietario)
        
        # Actualizar
        propietario.nombre = nombre
        propietario.documento = documento
        propietario.telefono = telefono
        propietario.email = email if email else None
        propietario.direccion = direccion if direccion else None
        
        try:
            db.session.commit()
            flash('Propietario actualizado exitosamente.', 'success')
            return redirect(url_for('propietarios.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
    
    return render_template('propietarios/edit.html', propietario=propietario)


@propietario_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar propietario (eliminación lógica)"""
    propietario = Propietario.query.get_or_404(id)
    
    try:
        # Eliminación lógica
        propietario.activo = False
        # También desactivar sus mascotas
        for mascota in propietario.mascotas:
            mascota.activo = False
        
        db.session.commit()
        flash(f'Propietario "{propietario.nombre}" eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('propietarios.index'))


# API JSON para AJAX
@propietario_bp.route('/api/search')
@login_required
def api_search():
    """API para búsqueda (AJAX)"""
    from flask import jsonify
    
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    
    propietarios = Propietario.buscar(q)[:10]
    return jsonify([p.to_dict() for p in propietarios])
