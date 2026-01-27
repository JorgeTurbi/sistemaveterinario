"""
Modelo: Usuario
Representa a los usuarios del sistema (para autenticación)
Con relaciones a veterinarios y trazabilidad de acciones
"""
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Usuario(UserMixin, db.Model):
    """Modelo para la tabla de usuarios"""
    
    __tablename__ = 'usuarios'
    
    # Roles disponibles
    ROL_ADMIN = 'Administrador'
    ROL_VETERINARIO = 'Veterinario'
    ROL_RECEPCIONISTA = 'Recepcionista'
    
    ROLES = [ROL_ADMIN, ROL_VETERINARIO, ROL_RECEPCIONISTA]
    
    # Columnas
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    rol = db.Column(db.String(20), nullable=False, default=ROL_RECEPCIONISTA)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    # ============================================
    # RELACIONES
    # ============================================
    
    # Relación 1:1 con Veterinario (un usuario puede ser veterinario)
    veterinario = db.relationship('Veterinario', backref='usuario', uselist=False)
    
    # Relación 1:N - Consultas registradas por este usuario
    consultas_registradas = db.relationship('Consulta', 
                                            foreign_keys='Consulta.id_usuario_registro',
                                            backref='usuario_registro', 
                                            lazy='dynamic')
    
    # Relación 1:N - Vacunaciones registradas por este usuario
    vacunaciones_registradas = db.relationship('CalendarioVacunacion',
                                               foreign_keys='CalendarioVacunacion.id_usuario_registro',
                                               backref='usuario_registro',
                                               lazy='dynamic')
    
    # Para Flask-Login
    def get_id(self):
        return str(self.id_usuario)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def set_password(self, password):
        """Genera el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def actualizar_acceso(self):
        """Actualiza la fecha de último acceso"""
        self.ultimo_acceso = datetime.utcnow()
        db.session.commit()
    
    @property
    def es_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == self.ROL_ADMIN
    
    @property
    def es_veterinario(self):
        """Verifica si el usuario es veterinario"""
        return self.rol == self.ROL_VETERINARIO
    
    @property
    def tiene_ficha_veterinario(self):
        """Verifica si el usuario tiene ficha de veterinario asociada"""
        return self.veterinario is not None
    
    @property
    def rol_color(self):
        """Retorna el color según el rol"""
        colores = {
            'Administrador': 'danger',
            'Veterinario': 'success',
            'Recepcionista': 'primary'
        }
        return colores.get(self.rol, 'secondary')
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_usuario,
            'username': self.username,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol,
            'rol_color': self.rol_color,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M') if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.strftime('%Y-%m-%d %H:%M') if self.ultimo_acceso else None,
            'veterinario_id': self.veterinario.id_veterinario if self.veterinario else None
        }
    
    @staticmethod
    def get_activos():
        """Obtiene todos los usuarios activos"""
        return Usuario.query.filter_by(activo=True).order_by(Usuario.nombre_completo).all()
    
    @staticmethod
    def get_by_username(username):
        """Busca un usuario por username"""
        return Usuario.query.filter_by(username=username, activo=True).first()
    
    @staticmethod
    def get_by_email(email):
        """Busca un usuario por email"""
        return Usuario.query.filter_by(email=email, activo=True).first()
    
    @staticmethod
    def get_veterinarios_sin_usuario():
        """Obtiene veterinarios que no tienen usuario asignado"""
        from app.models.veterinario import Veterinario
        return Veterinario.query.filter(
            Veterinario.activo == True,
            Veterinario.id_usuario == None
        ).all()


# Callback para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario por su ID"""
    return Usuario.query.get(int(user_id))
