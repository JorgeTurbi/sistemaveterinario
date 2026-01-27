"""
Controlador de Reportes
Generación de reportes y estadísticas
"""
from flask import Blueprint, render_template, request
from flask_login import login_required
from app import db
from app.models.consulta import Consulta
from app.models.mascota import Mascota
from app.models.especie import Especie
from app.models.tratamiento import Tratamiento
from app.models.veterinario import Veterinario
from app.models.calendario_vacunacion import CalendarioVacunacion
from datetime import datetime, date, timedelta
from sqlalchemy import func

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/')
@login_required
def index():
    """Dashboard de reportes"""
    return render_template('reportes/index.html')


@reportes_bp.route('/consultas-periodo')
@login_required
def consultas_periodo():
    """Reporte de consultas por período"""
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    # Por defecto, último mes
    if not fecha_inicio:
        fecha_inicio = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = date.today().strftime('%Y-%m-%d')
    
    try:
        f_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        f_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        f_inicio = datetime.now() - timedelta(days=30)
        f_fin = datetime.now()
    
    consultas = Consulta.query.filter(
        Consulta.fecha_hora >= f_inicio,
        Consulta.fecha_hora < f_fin
    ).order_by(Consulta.fecha_hora.desc()).all()
    
    # Estadísticas
    total = len(consultas)
    completadas = sum(1 for c in consultas if c.estado == 'Completada')
    canceladas = sum(1 for c in consultas if c.estado == 'Cancelada')
    ingresos = sum(float(c.costo or 0) for c in consultas if c.estado == 'Completada')
    
    # Por día
    consultas_por_dia = db.session.query(
        func.cast(Consulta.fecha_hora, db.Date).label('fecha'),
        func.count(Consulta.id_consulta).label('total')
    ).filter(
        Consulta.fecha_hora >= f_inicio,
        Consulta.fecha_hora < f_fin
    ).group_by(func.cast(Consulta.fecha_hora, db.Date)).all()
    
    return render_template('reportes/consultas_periodo.html',
                         consultas=consultas,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         total=total,
                         completadas=completadas,
                         canceladas=canceladas,
                         ingresos=ingresos,
                         consultas_por_dia=consultas_por_dia)


@reportes_bp.route('/especies-atendidas')
@login_required
def especies_atendidas():
    """Reporte de especies más atendidas"""
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    # Por defecto, último año
    if not fecha_inicio:
        fecha_inicio = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = date.today().strftime('%Y-%m-%d')
    
    try:
        f_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        f_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        f_inicio = datetime.now() - timedelta(days=365)
        f_fin = datetime.now()
    
    # Consultas por especie
    resultado = db.session.query(
        Especie.nombre,
        func.count(Consulta.id_consulta).label('total_consultas')
    ).join(Mascota, Mascota.id_especie == Especie.id_especie)\
     .join(Consulta, Consulta.id_mascota == Mascota.id_mascota)\
     .filter(
        Consulta.fecha_hora >= f_inicio,
        Consulta.fecha_hora < f_fin
    ).group_by(Especie.nombre)\
     .order_by(func.count(Consulta.id_consulta).desc()).all()
    
    # Total de mascotas por especie
    mascotas_por_especie = db.session.query(
        Especie.nombre,
        func.count(Mascota.id_mascota).label('total')
    ).join(Mascota, Mascota.id_especie == Especie.id_especie)\
     .filter(Mascota.activo == True)\
     .group_by(Especie.nombre)\
     .order_by(func.count(Mascota.id_mascota).desc()).all()
    
    return render_template('reportes/especies_atendidas.html',
                         resultado=resultado,
                         mascotas_por_especie=mascotas_por_especie,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin)


@reportes_bp.route('/tratamientos-frecuentes')
@login_required
def tratamientos_frecuentes():
    """Reporte de tratamientos más frecuentes"""
    # Por descripción
    por_descripcion = db.session.query(
        Tratamiento.descripcion,
        func.count(Tratamiento.id_tratamiento).label('total')
    ).group_by(Tratamiento.descripcion)\
     .order_by(func.count(Tratamiento.id_tratamiento).desc())\
     .limit(20).all()
    
    # Por medicamento
    por_medicamento = db.session.query(
        Tratamiento.medicamento,
        func.count(Tratamiento.id_tratamiento).label('total')
    ).filter(Tratamiento.medicamento != None)\
     .group_by(Tratamiento.medicamento)\
     .order_by(func.count(Tratamiento.id_tratamiento).desc())\
     .limit(20).all()
    
    return render_template('reportes/tratamientos_frecuentes.html',
                         por_descripcion=por_descripcion,
                         por_medicamento=por_medicamento)


@reportes_bp.route('/productividad-veterinarios')
@login_required
def productividad_veterinarios():
    """Reporte de productividad por veterinario"""
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    # Por defecto, último mes
    if not fecha_inicio:
        fecha_inicio = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = date.today().strftime('%Y-%m-%d')
    
    try:
        f_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        f_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        f_inicio = datetime.now() - timedelta(days=30)
        f_fin = datetime.now()
    
    # Consultas por veterinario
    resultado = db.session.query(
        Veterinario.nombre,
        func.count(Consulta.id_consulta).label('total_consultas'),
        func.sum(Consulta.costo).label('total_ingresos')
    ).join(Consulta, Consulta.id_veterinario == Veterinario.id_veterinario)\
     .filter(
        Consulta.fecha_hora >= f_inicio,
        Consulta.fecha_hora < f_fin,
        Consulta.estado == 'Completada'
    ).group_by(Veterinario.nombre)\
     .order_by(func.count(Consulta.id_consulta).desc()).all()
    
    return render_template('reportes/productividad_veterinarios.html',
                         resultado=resultado,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin)


@reportes_bp.route('/vacunacion')
@login_required
def vacunacion():
    """Reporte de vacunación"""
    # Próximas vacunas (7 días)
    proximas = CalendarioVacunacion.get_proximas(7)
    
    # Vencidas
    vencidas = CalendarioVacunacion.get_vencidas()
    
    # Estadísticas del mes
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)
    
    aplicadas_mes = CalendarioVacunacion.query.filter(
        CalendarioVacunacion.fecha_aplicacion >= inicio_mes,
        CalendarioVacunacion.estado == 'Aplicada'
    ).count()
    
    # Por vacuna
    por_vacuna = db.session.query(
        Vacuna.nombre,
        func.count(CalendarioVacunacion.id_calendario).label('total')
    ).join(CalendarioVacunacion)\
     .filter(CalendarioVacunacion.estado == 'Aplicada')\
     .group_by(Vacuna.nombre)\
     .order_by(func.count(CalendarioVacunacion.id_calendario).desc()).all()
    
    return render_template('reportes/vacunacion.html',
                         proximas=proximas,
                         vencidas=vencidas,
                         aplicadas_mes=aplicadas_mes,
                         por_vacuna=por_vacuna)
