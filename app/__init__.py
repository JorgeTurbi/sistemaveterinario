"""
VetCare Pro - Inicialización de la Aplicación Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """
    Factory function para crear la aplicación Flask
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    
    # ============================================
    # REGISTRAR BLUEPRINTS (Controladores)
    # ============================================
    
    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.propietario_controller import propietario_bp
    from app.controllers.mascota_controller import mascota_bp
    from app.controllers.especie_controller import especie_bp
    from app.controllers.veterinario_controller import veterinario_bp
    from app.controllers.consulta_controller import consulta_bp
    from app.controllers.tratamiento_controller import tratamiento_bp
    from app.controllers.vacunacion_controller import vacunacion_bp
    from app.controllers.reportes_controller import reportes_bp
    from app.controllers.servicio_controller import servicio_bp
    from app.controllers.facturacion_controller import facturacion_bp
    from app.controllers.usuario_controller import usuario_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(propietario_bp, url_prefix='/propietarios')
    app.register_blueprint(mascota_bp, url_prefix='/mascotas')
    app.register_blueprint(especie_bp, url_prefix='/especies')
    app.register_blueprint(veterinario_bp, url_prefix='/veterinarios')
    app.register_blueprint(consulta_bp, url_prefix='/consultas')
    app.register_blueprint(tratamiento_bp, url_prefix='/tratamientos')
    app.register_blueprint(vacunacion_bp, url_prefix='/vacunacion')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(servicio_bp, url_prefix='/servicios')
    app.register_blueprint(facturacion_bp, url_prefix='/facturacion')
    app.register_blueprint(usuario_bp, url_prefix='/usuarios')

    # ============================================
    # CONTEXT PROCESSORS (Variables globales para templates)
    # ============================================
    
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'VetCare Pro',
            'app_version': '1.0.0'
        }
    
    # ============================================
    # ERROR HANDLERS
    # ============================================
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app


# Importar para evitar errores de importación circular
from flask import render_template
