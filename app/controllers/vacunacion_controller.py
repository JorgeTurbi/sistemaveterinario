"""
Controlador de Vacunación
Gestión del calendario de vacunación
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.calendario_vacunacion import CalendarioVacunacion
from app.models.vacuna import Vacuna
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from datetime import datetime, date, timedelta

vacunacion_bp = Blueprint('vacunacion', __name__)


@vacunacion_bp.route('/')
@login_required
def index():
    """Dashboard de vacunación"""
    proximas = CalendarioVacunacion.get_proximas(7)
    vencidas = CalendarioVacunacion.get_vencidas()
    pendientes = CalendarioVacunacion.get_pendientes()[:20]
    
    return render_template('vacunacion/index.html',
                         proximas=proximas,
                         vencidas=vencidas,
                         pendientes=pendientes)


@vacunacion_bp.route('/calendario')
@login_required
def calendario():
    """Vista de calendario"""
    mes = request.args.get('mes', type=int, default=datetime.now().month)
    año = request.args.get('año', type=int, default=datetime.now().year)
    
    # Obtener vacunaciones del mes
    fecha_inicio = date(año, mes, 1)
    if mes == 12:
        fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
    
    vacunaciones = CalendarioVacunacion.query.filter(
        CalendarioVacunacion.fecha_programada >= fecha_inicio,
        CalendarioVacunacion.fecha_programada <= fecha_fin
    ).all()
    
    return render_template('vacunacion/calendario.html',
                         vacunaciones=vacunaciones,
                         mes=mes,
                         año=año)


@vacunacion_bp.route('/programar', methods=['GET', 'POST'])
@login_required
def programar():
    """Programar vacunación"""
    if request.method == 'POST':
        id_mascota = request.form.get('id_mascota', type=int)
        id_vacuna = request.form.get('id_vacuna', type=int)
        fecha = request.form.get('fecha_programada', '')
        observaciones = request.form.get('observaciones', '').strip()
        
        errores = []
        
        if not id_mascota:
            errores.append('Debe seleccionar una mascota.')
        
        if not id_vacuna:
            errores.append('Debe seleccionar una vacuna.')
        
        if not fecha:
            errores.append('La fecha es requerida.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            mascotas = Mascota.get_activas()
            vacunas = Vacuna.get_activas()
            return render_template('vacunacion/programar.html',
                                 mascotas=mascotas,
                                 vacunas=vacunas)
        
        try:
            fecha_programada = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            mascotas = Mascota.get_activas()
            vacunas = Vacuna.get_activas()
            return render_template('vacunacion/programar.html',
                                 mascotas=mascotas,
                                 vacunas=vacunas)
        
        calendario = CalendarioVacunacion(
            id_mascota=id_mascota,
            id_vacuna=id_vacuna,
            fecha_programada=fecha_programada,
            observaciones=observaciones if observaciones else None,
            estado=CalendarioVacunacion.ESTADO_PENDIENTE
        )
        
        try:
            db.session.add(calendario)
            db.session.commit()
            flash('Vacunación programada exitosamente.', 'success')
            return redirect(url_for('vacunacion.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    mascotas = Mascota.get_activas()
    vacunas = Vacuna.get_activas()
    mascota_id = request.args.get('mascota', type=int)
    
    return render_template('vacunacion/programar.html',
                         mascotas=mascotas,
                         vacunas=vacunas,
                         mascota_id=mascota_id)


@vacunacion_bp.route('/<int:id>/aplicar', methods=['GET', 'POST'])
@login_required
def aplicar(id):
    """Registrar aplicación de vacuna"""
    calendario = CalendarioVacunacion.query.get_or_404(id)
    
    if request.method == 'POST':
        lote = request.form.get('lote_vacuna', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        id_veterinario = request.form.get('id_veterinario', type=int)
        programar_siguiente = request.form.get('programar_siguiente', type=bool)
        
        calendario.aplicar(
            id_veterinario=id_veterinario,
            lote=lote if lote else None,
            observaciones=observaciones if observaciones else None
        )
        
        try:
            db.session.commit()
            
            # Programar siguiente dosis si aplica
            if programar_siguiente and calendario.fecha_proxima:
                nueva = CalendarioVacunacion(
                    id_mascota=calendario.id_mascota,
                    id_vacuna=calendario.id_vacuna,
                    fecha_programada=calendario.fecha_proxima,
                    dosis_numero=calendario.dosis_numero + 1,
                    estado=CalendarioVacunacion.ESTADO_PENDIENTE
                )
                db.session.add(nueva)
                db.session.commit()
                flash('Siguiente dosis programada automáticamente.', 'info')
            
            flash('Vacuna aplicada exitosamente.', 'success')
            return redirect(url_for('vacunacion.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    veterinarios = Veterinario.get_activos()
    return render_template('vacunacion/aplicar.html',
                         calendario=calendario,
                         veterinarios=veterinarios)


@vacunacion_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancelar vacunación programada"""
    calendario = CalendarioVacunacion.query.get_or_404(id)
    calendario.estado = CalendarioVacunacion.ESTADO_CANCELADA
    db.session.commit()
    flash('Vacunación cancelada.', 'info')
    return redirect(url_for('vacunacion.index'))


@vacunacion_bp.route('/historial/<int:mascota_id>')
@login_required
def historial(mascota_id):
    """Historial de vacunación de una mascota"""
    mascota = Mascota.query.get_or_404(mascota_id)
    vacunaciones = CalendarioVacunacion.get_by_mascota(mascota_id)
    
    return render_template('vacunacion/historial.html',
                         mascota=mascota,
                         vacunaciones=vacunaciones)


# === Gestión de Vacunas (Catálogo) ===

@vacunacion_bp.route('/vacunas')
@login_required
def vacunas():
    """Lista de vacunas (catálogo)"""
    todas = Vacuna.query.order_by(Vacuna.nombre).all()
    return render_template('vacunacion/vacunas.html', vacunas=todas)


@vacunacion_bp.route('/vacunas/create', methods=['GET', 'POST'])
@login_required
def vacuna_create():
    """Crear nueva vacuna"""
    from app.models.especie import Especie
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        intervalo_dias = request.form.get('intervalo_dias', type=int, default=365)
        id_especie = request.form.get('id_especie', type=int)
        
        if not nombre:
            flash('El nombre es requerido.', 'danger')
            especies = Especie.get_activas()
            return render_template('vacunacion/vacuna_create.html', especies=especies)
        
        vacuna = Vacuna(
            nombre=nombre,
            descripcion=descripcion if descripcion else None,
            intervalo_dias=intervalo_dias,
            id_especie=id_especie if id_especie else None
        )
        
        try:
            db.session.add(vacuna)
            db.session.commit()
            flash('Vacuna creada exitosamente.', 'success')
            return redirect(url_for('vacunacion.vacunas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    especies = Especie.get_activas()
    return render_template('vacunacion/vacuna_create.html', especies=especies)


@vacunacion_bp.route('/api/proximas')
@login_required
def api_proximas():
    """API: Vacunaciones próximas"""
    dias = request.args.get('dias', type=int, default=7)
    vacunaciones = CalendarioVacunacion.get_proximas(dias)
    return jsonify([v.to_dict() for v in vacunaciones])
