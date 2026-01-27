"""
Controlador de Consultas
CRUD para la gestión de consultas médicas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.consulta import Consulta
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from datetime import datetime

consulta_bp = Blueprint('consultas', __name__)


@consulta_bp.route('/')
@login_required
def index():
    """Lista todas las consultas"""
    estado = request.args.get('estado', '')
    fecha = request.args.get('fecha', '')
    
    query = Consulta.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(db.func.cast(Consulta.fecha_hora, db.Date) == fecha_dt)
        except ValueError:
            pass
    
    consultas = query.order_by(Consulta.fecha_hora.desc()).limit(100).all()
    
    return render_template('consultas/index.html', 
                         consultas=consultas,
                         estados=Consulta.ESTADOS,
                         estado_filtro=estado,
                         fecha_filtro=fecha)


@consulta_bp.route('/hoy')
@login_required
def hoy():
    """Consultas del día"""
    consultas = Consulta.get_hoy()
    return render_template('consultas/hoy.html', consultas=consultas)


@consulta_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Programar nueva consulta"""
    if request.method == 'POST':
        id_mascota = request.form.get('id_mascota', type=int)
        id_veterinario = request.form.get('id_veterinario', type=int)
        fecha = request.form.get('fecha', '')
        hora = request.form.get('hora', '')
        motivo = request.form.get('motivo', '').strip()
        
        errores = []
        
        if not id_mascota:
            errores.append('Debe seleccionar una mascota.')
        
        if not id_veterinario:
            errores.append('Debe seleccionar un veterinario.')
        
        if not fecha or not hora:
            errores.append('La fecha y hora son requeridas.')
        
        if not motivo:
            errores.append('El motivo es requerido.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            mascotas = Mascota.get_activas()
            veterinarios = Veterinario.get_activos()
            return render_template('consultas/create.html', 
                                 mascotas=mascotas,
                                 veterinarios=veterinarios)
        
        # Combinar fecha y hora
        try:
            fecha_hora = datetime.strptime(f'{fecha} {hora}', '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Formato de fecha/hora inválido.', 'danger')
            mascotas = Mascota.get_activas()
            veterinarios = Veterinario.get_activos()
            return render_template('consultas/create.html', 
                                 mascotas=mascotas,
                                 veterinarios=veterinarios)
        
        consulta = Consulta(
            id_mascota=id_mascota,
            id_veterinario=id_veterinario,
            fecha_hora=fecha_hora,
            motivo=motivo,
            estado=Consulta.ESTADO_PROGRAMADA
        )
        
        try:
            db.session.add(consulta)
            db.session.commit()
            flash('Consulta programada exitosamente.', 'success')
            return redirect(url_for('consultas.show', id=consulta.id_consulta))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    mascotas = Mascota.get_activas()
    veterinarios = Veterinario.get_activos()
    mascota_id = request.args.get('mascota', type=int)
    
    return render_template('consultas/create.html', 
                         mascotas=mascotas,
                         veterinarios=veterinarios,
                         mascota_id=mascota_id)


@consulta_bp.route('/<int:id>')
@login_required
def show(id):
    """Ver detalle de una consulta"""
    consulta = Consulta.query.get_or_404(id)
    tratamientos = consulta.tratamientos.all()
    
    return render_template('consultas/show.html', 
                         consulta=consulta,
                         tratamientos=tratamientos)


@consulta_bp.route('/<int:id>/atender', methods=['GET', 'POST'])
@login_required
def atender(id):
    """Atender consulta (registrar diagnóstico)"""
    consulta = Consulta.query.get_or_404(id)
    
    if request.method == 'POST':
        diagnostico = request.form.get('diagnostico', '').strip()
        peso_actual = request.form.get('peso_actual', '')
        temperatura = request.form.get('temperatura', '')
        observaciones = request.form.get('observaciones', '').strip()
        costo = request.form.get('costo', '')
        estado = request.form.get('estado', Consulta.ESTADO_COMPLETADA)
        
        consulta.diagnostico = diagnostico if diagnostico else None
        consulta.observaciones = observaciones if observaciones else None
        consulta.estado = estado
        
        if peso_actual:
            try:
                consulta.peso_actual = float(peso_actual)
                # Actualizar peso de la mascota
                consulta.mascota.peso = float(peso_actual)
            except ValueError:
                pass
        
        if temperatura:
            try:
                consulta.temperatura = float(temperatura)
            except ValueError:
                pass
        
        if costo:
            try:
                consulta.costo = float(costo)
            except ValueError:
                pass
        
        try:
            db.session.commit()
            flash('Consulta actualizada.', 'success')
            return redirect(url_for('consultas.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('consultas/atender.html', 
                         consulta=consulta,
                         estados=Consulta.ESTADOS)


@consulta_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancelar consulta"""
    consulta = Consulta.query.get_or_404(id)
    consulta.estado = Consulta.ESTADO_CANCELADA
    db.session.commit()
    flash('Consulta cancelada.', 'info')
    return redirect(url_for('consultas.index'))


@consulta_bp.route('/api/by-mascota/<int:id>')
@login_required
def api_by_mascota(id):
    """API: Obtener historial de una mascota"""
    consultas = Consulta.get_by_mascota(id)
    return jsonify([c.to_dict() for c in consultas])
