"""
VetCare Pro - Modelos de Base de Datos
Este archivo exporta todos los modelos SQLAlchemy
"""
from app import db

# Importar todos los modelos
from app.models.especie import Especie
from app.models.propietario import Propietario
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from app.models.consulta import Consulta
from app.models.tratamiento import Tratamiento
from app.models.vacuna import Vacuna
from app.models.calendario_vacunacion import CalendarioVacunacion
from app.models.usuario import Usuario
from app.models.servicio import Servicio
from app.models.factura import Factura, DetalleFactura

# Exportar todos los modelos
__all__ = [
    'db',
    'Especie',
    'Propietario',
    'Mascota',
    'Veterinario',
    'Consulta',
    'Tratamiento',
    'Vacuna',
    'CalendarioVacunacion',
    'Usuario',
    'Servicio',
    'Factura',
    'DetalleFactura'
]
