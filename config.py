"""
Configuración del Sistema VetCare Pro
"""
import os
from urllib.parse import quote_plus


class Config:
    """Configuración base de la aplicación"""
    
    # Clave secreta para sesiones y CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vetcare-clave-secreta-desarrollo-2024'
    
    # ============================================
    # CONFIGURACIÓN DE SQL SERVER
    # ============================================
    # Modifica estos valores según tu instalación
    
    SQL_SERVER = os.environ.get('SQL_SERVER') or 'localhost'  # o 'localhost\\SQLEXPRESS'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'VetCareDB'
    SQL_DRIVER = 'ODBC Driver 17 for SQL Server'  # o 'ODBC Driver 18 for SQL Server'
    
    # ============================================
    # OPCIÓN 1: Windows Authentication (Recomendado)
    # ============================================
    params = quote_plus(
        f'DRIVER={{{SQL_DRIVER}}};'
        f'SERVER={SQL_SERVER};'
        f'DATABASE={SQL_DATABASE};'
        f'Trusted_Connection=yes;'
        f'TrustServerCertificate=yes;'
    )
    
    # ============================================
    # OPCIÓN 2: SQL Server Authentication
    # Descomenta las siguientes líneas si usas usuario y contraseña
    # ============================================
    # SQL_USERNAME = 'tu_usuario'
    # SQL_PASSWORD = 'tu_contraseña'
    # params = quote_plus(
    #     f'DRIVER={{{SQL_DRIVER}}};'
    #     f'SERVER={SQL_SERVER};'
    #     f'DATABASE={SQL_DATABASE};'
    #     f'UID={SQL_USERNAME};'
    #     f'PWD={SQL_PASSWORD};'
    #     f'TrustServerCertificate=yes;'
    # )
    
    # Cadena de conexión final para SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc:///?odbc_connect={params}'
    
    # Desactivar el seguimiento de modificaciones (mejora rendimiento)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mostrar consultas SQL en consola (solo para desarrollo)
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Muestra las consultas SQL


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
