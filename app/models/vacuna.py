"""
Modelo: Vacuna
Representa el catálogo de vacunas disponibles
"""
from app import db


class Vacuna(db.Model):
    """Modelo para la tabla de vacunas"""
    
    __tablename__ = 'vacunas'
    
    # Columnas
    id_vacuna = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    intervalo_dias = db.Column(db.Integer, nullable=False, default=365)  # Días entre dosis
    id_especie = db.Column(db.Integer, db.ForeignKey('especies.id_especie'))  # NULL = todas
    dosis_requeridas = db.Column(db.Integer, default=1)
    edad_minima_dias = db.Column(db.Integer)  # Edad mínima para aplicar
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    calendario = db.relationship('CalendarioVacunacion', backref='vacuna', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vacuna {self.nombre}>'
    
    @property
    def especie_texto(self):
        """Retorna el nombre de la especie o 'Todas'"""
        return self.especie.nombre if self.especie else 'Todas las especies'
    
    @property
    def intervalo_texto(self):
        """Retorna el intervalo en formato legible"""
        if self.intervalo_dias >= 365:
            años = self.intervalo_dias // 365
            return f"Cada {años} año(s)"
        elif self.intervalo_dias >= 30:
            meses = self.intervalo_dias // 30
            return f"Cada {meses} mes(es)"
        else:
            return f"Cada {self.intervalo_dias} día(s)"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_vacuna,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'intervalo_dias': self.intervalo_dias,
            'intervalo_texto': self.intervalo_texto,
            'especie_id': self.id_especie,
            'especie': self.especie_texto,
            'dosis_requeridas': self.dosis_requeridas,
            'edad_minima_dias': self.edad_minima_dias,
            'activo': self.activo
        }
    
    @staticmethod
    def get_activas():
        """Obtiene todas las vacunas activas"""
        return Vacuna.query.filter_by(activo=True).order_by(Vacuna.nombre).all()
    
    @staticmethod
    def get_by_especie(id_especie):
        """Obtiene vacunas aplicables a una especie"""
        return Vacuna.query.filter(
            db.and_(
                Vacuna.activo == True,
                db.or_(
                    Vacuna.id_especie == id_especie,
                    Vacuna.id_especie == None
                )
            )
        ).order_by(Vacuna.nombre).all()
