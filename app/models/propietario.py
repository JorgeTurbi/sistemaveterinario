"""
Modelo: Propietario
Representa a los dueños de las mascotas
"""
from app import db
from datetime import datetime


class Propietario(db.Model):
    """Modelo para la tabla de propietarios"""
    
    __tablename__ = 'propietarios'
    
    # Columnas
    id_propietario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), nullable=False, unique=True)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    mascotas = db.relationship('Mascota', backref='propietario', lazy='dynamic',
                               cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Propietario {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_propietario,
            'nombre': self.nombre,
            'documento': self.documento,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M') if self.fecha_registro else None,
            'activo': self.activo,
            'num_mascotas': self.mascotas.filter_by(activo=True).count()
        }
    
    @staticmethod
    def get_activos():
        """Obtiene todos los propietarios activos"""
        return Propietario.query.filter_by(activo=True).order_by(Propietario.nombre).all()
    
    @staticmethod
    def buscar(termino):
        """Busca propietarios por nombre o documento"""
        busqueda = f'%{termino}%'
        return Propietario.query.filter(
            db.and_(
                Propietario.activo == True,
                db.or_(
                    Propietario.nombre.ilike(busqueda),
                    Propietario.documento.ilike(busqueda),
                    Propietario.telefono.ilike(busqueda)
                )
            )
        ).order_by(Propietario.nombre).all()
