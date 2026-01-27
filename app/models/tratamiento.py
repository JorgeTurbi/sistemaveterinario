"""
Modelo: Tratamiento
Representa los tratamientos aplicados en las consultas
"""
from app import db
from datetime import datetime


class Tratamiento(db.Model):
    """Modelo para la tabla de tratamientos"""
    
    __tablename__ = 'tratamientos'
    
    # Columnas
    id_tratamiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id_consulta'), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    medicamento = db.Column(db.String(100))
    dosis = db.Column(db.String(100))
    duracion_dias = db.Column(db.Integer)
    indicaciones = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    fecha_inicio = db.Column(db.Date, default=datetime.utcnow)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.String(20), default='Activo')  # Activo, Completado, Suspendido
    
    def __repr__(self):
        return f'<Tratamiento {self.id_tratamiento} - {self.descripcion[:30]}>'
    
    @property
    def estado_color(self):
        """Retorna el color según el estado"""
        colores = {
            'Activo': 'success',
            'Completado': 'secondary',
            'Suspendido': 'warning'
        }
        return colores.get(self.estado, 'info')
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_tratamiento,
            'consulta_id': self.id_consulta,
            'descripcion': self.descripcion,
            'medicamento': self.medicamento,
            'dosis': self.dosis,
            'duracion_dias': self.duracion_dias,
            'indicaciones': self.indicaciones,
            'costo': float(self.costo) if self.costo else None,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else None,
            'estado': self.estado,
            'estado_color': self.estado_color
        }
    
    @staticmethod
    def get_by_consulta(id_consulta):
        """Obtiene tratamientos de una consulta"""
        return Tratamiento.query.filter_by(id_consulta=id_consulta).all()
    
    @staticmethod
    def get_activos():
        """Obtiene tratamientos activos"""
        return Tratamiento.query.filter_by(estado='Activo').all()
    
    @staticmethod
    def get_frecuentes(limit=10):
        """Obtiene los tratamientos más frecuentes"""
        return db.session.query(
            Tratamiento.descripcion,
            db.func.count(Tratamiento.id_tratamiento).label('total')
        ).group_by(Tratamiento.descripcion)\
         .order_by(db.desc('total'))\
         .limit(limit).all()
