"""
Controlador Principal
Maneja las rutas principales del sistema
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Consulta, CalendarioVacunacion, Mascota, Propietario

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página de inicio / Dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con estadísticas"""
    # Estadísticas generales
    stats = {
        'total_mascotas': Mascota.query.filter_by(activo=True).count(),
        'total_propietarios': Propietario.query.filter_by(activo=True).count(),
        'consultas_hoy': len(Consulta.get_hoy()),
        'vacunas_pendientes': len(CalendarioVacunacion.get_proximas(7))
    }
    
    # Consultas de hoy
    consultas_hoy = Consulta.get_hoy()
    
    # Próximas vacunaciones (7 días)
    proximas_vacunas = CalendarioVacunacion.get_proximas(7)
    
    # Vacunaciones vencidas
    vacunas_vencidas = CalendarioVacunacion.get_vencidas()
    
    return render_template('dashboard.html',
                         stats=stats,
                         consultas_hoy=consultas_hoy,
                         proximas_vacunas=proximas_vacunas,
                         vacunas_vencidas=vacunas_vencidas)


@main_bp.route('/about')
def about():
    """Página Acerca de"""
    return render_template('about.html')
