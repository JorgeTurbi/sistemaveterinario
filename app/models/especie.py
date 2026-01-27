"""
Modelo: Especie
Representa las especies de mascotas (Perro, Gato, Ave, etc.)
"""
from app import db


class Especie(db.Model):
    """Modelo para la tabla de especies"""
    
    __tablename__ = 'especies'
    
    # Columnas
    id_especie = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    mascotas = db.relationship('Mascota', backref='especie', lazy='dynamic')
    vacunas = db.relationship('Vacuna', backref='especie', lazy='dynamic')
    
    def __repr__(self):
        return f'<Especie {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_especie,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'num_mascotas': self.mascotas.filter_by(activo=True).count()
        }
    
    @staticmethod
    def get_activas():
        """Obtiene todas las especies activas"""
        return Especie.query.filter_by(activo=True).order_by(Especie.nombre).all()
