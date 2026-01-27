"""
Controlador de Mascotas
CRUD completo para la gestión de mascotas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.mascota import Mascota
from app.models.propietario import Propietario
from app.models.especie import Especie
from datetime import datetime

mascota_bp = Blueprint('mascotas', __name__)


@mascota_bp.route('/')
@login_required
def index():
    """Lista todas las mascotas"""
    busqueda = request.args.get('q', '')
    especie_id = request.args.get('especie', type=int)
    
    query = Mascota.query.filter_by(activo=True)
    
    if busqueda:
        query = query.filter(Mascota.nombre.ilike(f'%{busqueda}%'))
    
    if especie_id:
        query = query.filter_by(id_especie=especie_id)
    
    mascotas = query.order_by(Mascota.nombre).all()
    especies = Especie.get_activas()
    
    return render_template('mascotas/index.html', 
                         mascotas=mascotas,
                         especies=especies,
                         busqueda=busqueda,
                         especie_id=especie_id)


@mascota_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nueva mascota"""
    if request.method == 'POST':
        id_propietario = request.form.get('id_propietario', type=int)
        id_especie = request.form.get('id_especie', type=int)
        nombre = request.form.get('nombre', '').strip()
        raza = request.form.get('raza', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '')
        sexo = request.form.get('sexo', '')
        peso = request.form.get('peso', '')
        color = request.form.get('color', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        
        # Validaciones
        errores = []
        
        if not id_propietario:
            errores.append('Debe seleccionar un propietario.')
        
        if not id_especie:
            errores.append('Debe seleccionar una especie.')
        
        if not nombre:
            errores.append('El nombre es requerido.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            propietarios = Propietario.get_activos()
            especies = Especie.get_activas()
            return render_template('mascotas/create.html', 
                                 propietarios=propietarios,
                                 especies=especies)
        
        # Crear mascota
        mascota = Mascota(
            id_propietario=id_propietario,
            id_especie=id_especie,
            nombre=nombre,
            raza=raza if raza else None,
            sexo=sexo if sexo else None,
            color=color if color else None,
            observaciones=observaciones if observaciones else None
        )
        
        # Procesar fecha
        if fecha_nacimiento:
            try:
                mascota.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Procesar peso
        if peso:
            try:
                mascota.peso = float(peso)
            except ValueError:
                pass
        
        try:
            db.session.add(mascota)
            db.session.commit()
            flash(f'Mascota "{nombre}" registrada exitosamente.', 'success')
            return redirect(url_for('mascotas.show', id=mascota.id_mascota))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear mascota: {str(e)}', 'danger')
    
    propietarios = Propietario.get_activos()
    especies = Especie.get_activas()
    propietario_id = request.args.get('propietario', type=int)
    
    return render_template('mascotas/create.html', 
                         propietarios=propietarios,
                         especies=especies,
                         propietario_id=propietario_id)


@mascota_bp.route('/<int:id>')
@login_required
def show(id):
    """Ver detalle de una mascota"""
    mascota = Mascota.query.get_or_404(id)
    consultas = mascota.consultas.order_by(db.desc('fecha_hora')).limit(10).all()
    vacunaciones = mascota.vacunaciones.order_by(db.desc('fecha_programada')).limit(10).all()
    
    return render_template('mascotas/show.html', 
                         mascota=mascota,
                         consultas=consultas,
                         vacunaciones=vacunaciones)


@mascota_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar mascota"""
    mascota = Mascota.query.get_or_404(id)
    
    if request.method == 'POST':
        id_propietario = request.form.get('id_propietario', type=int)
        id_especie = request.form.get('id_especie', type=int)
        nombre = request.form.get('nombre', '').strip()
        raza = request.form.get('raza', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '')
        sexo = request.form.get('sexo', '')
        peso = request.form.get('peso', '')
        color = request.form.get('color', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        
        # Validaciones básicas
        if not nombre:
            flash('El nombre es requerido.', 'danger')
            propietarios = Propietario.get_activos()
            especies = Especie.get_activas()
            return render_template('mascotas/edit.html', 
                                 mascota=mascota,
                                 propietarios=propietarios,
                                 especies=especies)
        
        # Actualizar
        mascota.id_propietario = id_propietario
        mascota.id_especie = id_especie
        mascota.nombre = nombre
        mascota.raza = raza if raza else None
        mascota.sexo = sexo if sexo else None
        mascota.color = color if color else None
        mascota.observaciones = observaciones if observaciones else None
        
        # Procesar fecha
        if fecha_nacimiento:
            try:
                mascota.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            except ValueError:
                mascota.fecha_nacimiento = None
        else:
            mascota.fecha_nacimiento = None
        
        # Procesar peso
        if peso:
            try:
                mascota.peso = float(peso)
            except ValueError:
                mascota.peso = None
        else:
            mascota.peso = None
        
        try:
            db.session.commit()
            flash('Mascota actualizada exitosamente.', 'success')
            return redirect(url_for('mascotas.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
    
    propietarios = Propietario.get_activos()
    especies = Especie.get_activas()
    
    return render_template('mascotas/edit.html', 
                         mascota=mascota,
                         propietarios=propietarios,
                         especies=especies)


@mascota_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar mascota (eliminación lógica)"""
    mascota = Mascota.query.get_or_404(id)
    propietario_id = mascota.id_propietario
    
    try:
        mascota.activo = False
        db.session.commit()
        flash(f'Mascota "{mascota.nombre}" eliminada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('propietarios.show', id=propietario_id))


# API JSON
@mascota_bp.route('/api/by-propietario/<int:id>')
@login_required
def api_by_propietario(id):
    """Obtener mascotas de un propietario (AJAX)"""
    mascotas = Mascota.get_by_propietario(id)
    return jsonify([m.to_dict() for m in mascotas])


@mascota_bp.route('/api/search')
@login_required
def api_search():
    """Buscar mascotas (AJAX)"""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    
    mascotas = Mascota.buscar(q)[:10]
    return jsonify([m.to_dict() for m in mascotas])
