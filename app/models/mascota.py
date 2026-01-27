"""
Modelo: Mascota
Representa a las mascotas registradas en el sistema
"""
from app import db
from datetime import date


class Mascota(db.Model):
    """Modelo para la tabla de mascotas"""
    
    __tablename__ = 'mascotas'
    
    # Columnas
    id_mascota = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_propietario = db.Column(db.Integer, db.ForeignKey('propietarios.id_propietario'), nullable=False)
    id_especie = db.Column(db.Integer, db.ForeignKey('especies.id_especie'), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(50))
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(1))  # M = Macho, H = Hembra
    peso = db.Column(db.Numeric(5, 2))
    color = db.Column(db.String(30))
    observaciones = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    consultas = db.relationship('Consulta', backref='mascota', lazy='dynamic',
                                cascade='all, delete-orphan')
    vacunaciones = db.relationship('CalendarioVacunacion', backref='mascota', lazy='dynamic',
                                   cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Mascota {self.nombre}>'
    
    @property
    def edad(self):
        """Calcula la edad de la mascota en años"""
        if self.fecha_nacimiento:
            today = date.today()
            years = today.year - self.fecha_nacimiento.year
            if (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                years -= 1
            return years
        return None
    
    @property
    def edad_texto(self):
        """Retorna la edad en formato legible"""
        if self.fecha_nacimiento:
            today = date.today()
            delta = today - self.fecha_nacimiento
            years = delta.days // 365
            months = (delta.days % 365) // 30
            
            if years > 0:
                return f"{years} año(s), {months} mes(es)"
            elif months > 0:
                return f"{months} mes(es)"
            else:
                return f"{delta.days} día(s)"
        return "No especificada"
    
    @property
    def sexo_texto(self):
        """Retorna el sexo en formato legible"""
        sexos = {'M': 'Macho', 'H': 'Hembra'}
        return sexos.get(self.sexo, 'No especificado')
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_mascota,
            'nombre': self.nombre,
            'propietario': self.propietario.nombre if self.propietario else None,
            'propietario_id': self.id_propietario,
            'especie': self.especie.nombre if self.especie else None,
            'especie_id': self.id_especie,
            'raza': self.raza,
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%Y-%m-%d') if self.fecha_nacimiento else None,
            'edad': self.edad_texto,
            'sexo': self.sexo,
            'sexo_texto': self.sexo_texto,
            'peso': float(self.peso) if self.peso else None,
            'color': self.color,
            'observaciones': self.observaciones,
            'activo': self.activo,
            'num_consultas': self.consultas.count()
        }
    
    @staticmethod
    def get_activas():
        """Obtiene todas las mascotas activas"""
        return Mascota.query.filter_by(activo=True).order_by(Mascota.nombre).all()
    
    @staticmethod
    def buscar(termino):
        """Busca mascotas por nombre"""
        busqueda = f'%{termino}%'
        return Mascota.query.filter(
            db.and_(
                Mascota.activo == True,
                Mascota.nombre.ilike(busqueda)
            )
        ).order_by(Mascota.nombre).all()
    
    @staticmethod
    def get_by_propietario(id_propietario):
        """Obtiene todas las mascotas de un propietario"""
        return Mascota.query.filter_by(
            id_propietario=id_propietario,
            activo=True
        ).order_by(Mascota.nombre).all()
