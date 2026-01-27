"""
Controlador de Tratamientos
CRUD para la gestión de tratamientos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.tratamiento import Tratamiento
from app.models.consulta import Consulta
from datetime import datetime, timedelta

tratamiento_bp = Blueprint('tratamientos', __name__)


@tratamiento_bp.route('/')
@login_required
def index():
    """Lista todos los tratamientos"""
    estado = request.args.get('estado', '')
    
    query = Tratamiento.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    tratamientos = query.order_by(Tratamiento.id_tratamiento.desc()).limit(100).all()
    
    return render_template('tratamientos/index.html', 
                         tratamientos=tratamientos,
                         estado_filtro=estado)


@tratamiento_bp.route('/create/<int:consulta_id>', methods=['GET', 'POST'])
@login_required
def create(consulta_id):
    """Crear tratamiento para una consulta"""
    consulta = Consulta.query.get_or_404(consulta_id)
    
    if request.method == 'POST':
        descripcion = request.form.get('descripcion', '').strip()
        medicamento = request.form.get('medicamento', '').strip()
        dosis = request.form.get('dosis', '').strip()
        duracion_dias = request.form.get('duracion_dias', type=int)
        indicaciones = request.form.get('indicaciones', '').strip()
        costo = request.form.get('costo', '')
        
        if not descripcion:
            flash('La descripción es requerida.', 'danger')
            return render_template('tratamientos/create.html', consulta=consulta)
        
        tratamiento = Tratamiento(
            id_consulta=consulta_id,
            descripcion=descripcion,
            medicamento=medicamento if medicamento else None,
            dosis=dosis if dosis else None,
            duracion_dias=duracion_dias,
            indicaciones=indicaciones if indicaciones else None,
            fecha_inicio=datetime.now().date()
        )
        
        if duracion_dias:
            tratamiento.fecha_fin = tratamiento.fecha_inicio + timedelta(days=duracion_dias)
        
        if costo:
            try:
                tratamiento.costo = float(costo)
            except ValueError:
                pass
        
        try:
            db.session.add(tratamiento)
            db.session.commit()
            flash('Tratamiento registrado.', 'success')
            return redirect(url_for('consultas.show', id=consulta_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('tratamientos/create.html', consulta=consulta)


@tratamiento_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar tratamiento"""
    tratamiento = Tratamiento.query.get_or_404(id)
    
    if request.method == 'POST':
        tratamiento.descripcion = request.form.get('descripcion', '').strip()
        tratamiento.medicamento = request.form.get('medicamento', '').strip() or None
        tratamiento.dosis = request.form.get('dosis', '').strip() or None
        tratamiento.duracion_dias = request.form.get('duracion_dias', type=int)
        tratamiento.indicaciones = request.form.get('indicaciones', '').strip() or None
        tratamiento.estado = request.form.get('estado', 'Activo')
        
        costo = request.form.get('costo', '')
        if costo:
            try:
                tratamiento.costo = float(costo)
            except ValueError:
                pass
        
        try:
            db.session.commit()
            flash('Tratamiento actualizado.', 'success')
            return redirect(url_for('consultas.show', id=tratamiento.id_consulta))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('tratamientos/edit.html', tratamiento=tratamiento)


@tratamiento_bp.route('/<int:id>/completar', methods=['POST'])
@login_required
def completar(id):
    """Marcar tratamiento como completado"""
    tratamiento = Tratamiento.query.get_or_404(id)
    tratamiento.estado = 'Completado'
    tratamiento.fecha_fin = datetime.now().date()
    db.session.commit()
    flash('Tratamiento completado.', 'success')
    return redirect(url_for('consultas.show', id=tratamiento.id_consulta))


@tratamiento_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar tratamiento"""
    tratamiento = Tratamiento.query.get_or_404(id)
    consulta_id = tratamiento.id_consulta
    
    try:
        db.session.delete(tratamiento)
        db.session.commit()
        flash('Tratamiento eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('consultas.show', id=consulta_id))
