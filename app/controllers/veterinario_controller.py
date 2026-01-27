"""
Controlador de Veterinarios
CRUD para la gestión de veterinarios
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.veterinario import Veterinario

veterinario_bp = Blueprint('veterinarios', __name__)


@veterinario_bp.route('/')
@login_required
def index():
    """Lista todos los veterinarios"""
    busqueda = request.args.get('q', '')
    
    if busqueda:
        veterinarios = Veterinario.buscar(busqueda)
    else:
        veterinarios = Veterinario.query.order_by(Veterinario.nombre).all()
    
    return render_template('veterinarios/index.html', 
                         veterinarios=veterinarios,
                         busqueda=busqueda)


@veterinario_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nuevo veterinario"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        colegiatura = request.form.get('colegiatura', '').strip()
        especialidad = request.form.get('especialidad', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido.')
        
        if not colegiatura:
            errores.append('El número de colegiatura es requerido.')
        elif Veterinario.query.filter_by(colegiatura=colegiatura).first():
            errores.append('Ya existe un veterinario con este número de colegiatura.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('veterinarios/create.html')
        
        veterinario = Veterinario(
            nombre=nombre,
            colegiatura=colegiatura,
            especialidad=especialidad if especialidad else None,
            telefono=telefono if telefono else None,
            email=email if email else None
        )
        
        try:
            db.session.add(veterinario)
            db.session.commit()
            flash(f'Veterinario "{nombre}" creado exitosamente.', 'success')
            return redirect(url_for('veterinarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('veterinarios/create.html')


@veterinario_bp.route('/<int:id>')
@login_required
def show(id):
    """Ver detalle del veterinario"""
    veterinario = Veterinario.query.get_or_404(id)
    consultas = veterinario.consultas.order_by(db.desc('fecha_hora')).limit(20).all()
    
    return render_template('veterinarios/show.html', 
                         veterinario=veterinario,
                         consultas=consultas)


@veterinario_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar veterinario"""
    veterinario = Veterinario.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        colegiatura = request.form.get('colegiatura', '').strip()
        especialidad = request.form.get('especialidad', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        if not nombre or not colegiatura:
            flash('Nombre y colegiatura son requeridos.', 'danger')
            return render_template('veterinarios/edit.html', veterinario=veterinario)
        
        existente = Veterinario.query.filter_by(colegiatura=colegiatura).first()
        if existente and existente.id_veterinario != id:
            flash('Ya existe otro veterinario con esta colegiatura.', 'danger')
            return render_template('veterinarios/edit.html', veterinario=veterinario)
        
        veterinario.nombre = nombre
        veterinario.colegiatura = colegiatura
        veterinario.especialidad = especialidad if especialidad else None
        veterinario.telefono = telefono if telefono else None
        veterinario.email = email if email else None
        
        try:
            db.session.commit()
            flash('Veterinario actualizado.', 'success')
            return redirect(url_for('veterinarios.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('veterinarios/edit.html', veterinario=veterinario)


@veterinario_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    """Activar/Desactivar veterinario"""
    veterinario = Veterinario.query.get_or_404(id)
    veterinario.activo = not veterinario.activo
    db.session.commit()
    
    estado = 'activado' if veterinario.activo else 'desactivado'
    flash(f'Veterinario {estado}.', 'success')
    return redirect(url_for('veterinarios.index'))


@veterinario_bp.route('/api/activos')
@login_required
def api_activos():
    """API: Obtener veterinarios activos"""
    veterinarios = Veterinario.get_activos()
    return jsonify([v.to_dict() for v in veterinarios])
