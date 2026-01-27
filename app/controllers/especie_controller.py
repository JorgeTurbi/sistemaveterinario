"""
Controlador de Especies
CRUD para el catálogo de especies
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.especie import Especie

especie_bp = Blueprint('especies', __name__)


@especie_bp.route('/')
@login_required
def index():
    """Lista todas las especies"""
    especies = Especie.query.order_by(Especie.nombre).all()
    return render_template('especies/index.html', especies=especies)


@especie_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nueva especie"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not nombre:
            flash('El nombre es requerido.', 'danger')
            return render_template('especies/create.html')
        
        if Especie.query.filter_by(nombre=nombre).first():
            flash('Ya existe una especie con este nombre.', 'danger')
            return render_template('especies/create.html')
        
        especie = Especie(
            nombre=nombre,
            descripcion=descripcion if descripcion else None
        )
        
        try:
            db.session.add(especie)
            db.session.commit()
            flash(f'Especie "{nombre}" creada exitosamente.', 'success')
            return redirect(url_for('especies.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('especies/create.html')


@especie_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar especie"""
    especie = Especie.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not nombre:
            flash('El nombre es requerido.', 'danger')
            return render_template('especies/edit.html', especie=especie)
        
        existente = Especie.query.filter_by(nombre=nombre).first()
        if existente and existente.id_especie != id:
            flash('Ya existe otra especie con este nombre.', 'danger')
            return render_template('especies/edit.html', especie=especie)
        
        especie.nombre = nombre
        especie.descripcion = descripcion if descripcion else None
        
        try:
            db.session.commit()
            flash('Especie actualizada.', 'success')
            return redirect(url_for('especies.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('especies/edit.html', especie=especie)


@especie_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    """Activar/Desactivar especie"""
    especie = Especie.query.get_or_404(id)
    especie.activo = not especie.activo
    db.session.commit()
    
    estado = 'activada' if especie.activo else 'desactivada'
    flash(f'Especie {estado}.', 'success')
    return redirect(url_for('especies.index'))
