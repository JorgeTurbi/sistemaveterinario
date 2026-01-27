"""
Modelo: Veterinario
Representa a los veterinarios del sistema
Con relación a Usuario para login
"""
from app import db


class Veterinario(db.Model):
    """Modelo para la tabla de veterinarios"""
    
    __tablename__ = 'veterinarios'
    
    # Columnas
    id_veterinario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    colegiatura = db.Column(db.String(20), nullable=False, unique=True)
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # ============================================
    # RELACIÓN CON USUARIO (1:1)
    # ============================================
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True, unique=True)
    
    # Relaciones
    consultas = db.relationship('Consulta', 
                                foreign_keys='Consulta.id_veterinario',
                                backref='veterinario', 
                                lazy='dynamic')
    vacunaciones = db.relationship('CalendarioVacunacion',
                                   foreign_keys='CalendarioVacunacion.id_veterinario',
                                   backref='veterinario',
                                   lazy='dynamic')
    
    def __repr__(self):
        return f'<Veterinario {self.nombre}>'
    
    @property
    def tiene_usuario(self):
        """Verifica si tiene cuenta de usuario asociada"""
        return self.id_usuario is not None
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_veterinario,
            'nombre': self.nombre,
            'colegiatura': self.colegiatura,
            'especialidad': self.especialidad,
            'telefono': self.telefono,
            'email': self.email,
            'activo': self.activo,
            'tiene_usuario': self.tiene_usuario,
            'usuario_id': self.id_usuario,
            'num_consultas': self.consultas.count()
        }
    
    @staticmethod
    def get_activos():
        """Obtiene todos los veterinarios activos"""
        return Veterinario.query.filter_by(activo=True).order_by(Veterinario.nombre).all()
    
    @staticmethod
    def buscar(termino):
        """Busca veterinarios por nombre o colegiatura"""
        busqueda = f'%{termino}%'
        return Veterinario.query.filter(
            db.and_(
                Veterinario.activo == True,
                db.or_(
                    Veterinario.nombre.ilike(busqueda),
                    Veterinario.colegiatura.ilike(busqueda),
                    Veterinario.especialidad.ilike(busqueda)
                )
            )
        ).order_by(Veterinario.nombre).all()
    
    @staticmethod
    def get_sin_usuario():
        """Obtiene veterinarios sin cuenta de usuario"""
        return Veterinario.query.filter(
            Veterinario.activo == True,
            Veterinario.id_usuario == None
        ).order_by(Veterinario.nombre).all()
