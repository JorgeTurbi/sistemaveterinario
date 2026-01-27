"""
Modelo: Consulta
Representa las consultas médicas veterinarias
Con trazabilidad de usuario que registra
"""
from app import db
from datetime import datetime


class Consulta(db.Model):
    """Modelo para la tabla de consultas"""
    
    __tablename__ = 'consultas'
    
    # Estados posibles de una consulta
    ESTADO_PROGRAMADA = 'Programada'
    ESTADO_EN_CURSO = 'En Curso'
    ESTADO_COMPLETADA = 'Completada'
    ESTADO_CANCELADA = 'Cancelada'
    
    ESTADOS = [ESTADO_PROGRAMADA, ESTADO_EN_CURSO, ESTADO_COMPLETADA, ESTADO_CANCELADA]
    
    # Columnas
    id_consulta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascotas.id_mascota'), nullable=False)
    id_veterinario = db.Column(db.Integer, db.ForeignKey('veterinarios.id_veterinario'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    motivo = db.Column(db.String(200), nullable=False)
    diagnostico = db.Column(db.Text)
    peso_actual = db.Column(db.Numeric(5, 2))
    temperatura = db.Column(db.Numeric(4, 1))
    estado = db.Column(db.String(20), default=ESTADO_PROGRAMADA, nullable=False)
    observaciones = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ============================================
    # TRAZABILIDAD - Usuario que registró la consulta
    # ============================================
    id_usuario_registro = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    
    # Relaciones
    tratamientos = db.relationship('Tratamiento', backref='consulta', lazy='dynamic',
                                   cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Consulta {self.id_consulta} - {self.mascota.nombre if self.mascota else "N/A"}>'
    
    @property
    def fecha_formateada(self):
        """Retorna la fecha en formato legible"""
        if self.fecha_hora:
            return self.fecha_hora.strftime('%d/%m/%Y %H:%M')
        return None
    
    @property
    def estado_color(self):
        """Retorna el color según el estado"""
        colores = {
            'Programada': 'primary',
            'En Curso': 'warning',
            'Completada': 'success',
            'Cancelada': 'danger'
        }
        return colores.get(self.estado, 'secondary')
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_consulta,
            'mascota': self.mascota.nombre if self.mascota else None,
            'mascota_id': self.id_mascota,
            'propietario': self.mascota.propietario.nombre if self.mascota and self.mascota.propietario else None,
            'veterinario': self.veterinario.nombre if self.veterinario else None,
            'veterinario_id': self.id_veterinario,
            'fecha_hora': self.fecha_hora.strftime('%Y-%m-%d %H:%M') if self.fecha_hora else None,
            'fecha_formateada': self.fecha_formateada,
            'motivo': self.motivo,
            'diagnostico': self.diagnostico,
            'peso_actual': float(self.peso_actual) if self.peso_actual else None,
            'temperatura': float(self.temperatura) if self.temperatura else None,
            'estado': self.estado,
            'estado_color': self.estado_color,
            'observaciones': self.observaciones,
            'costo': float(self.costo) if self.costo else None,
            'num_tratamientos': self.tratamientos.count(),
            # Trazabilidad
            'registrado_por': self.usuario_registro.nombre_completo if self.usuario_registro else None,
            'usuario_registro_id': self.id_usuario_registro
        }
    
    @staticmethod
    def get_programadas():
        """Obtiene consultas programadas ordenadas por fecha"""
        return Consulta.query.filter_by(estado=Consulta.ESTADO_PROGRAMADA)\
            .order_by(Consulta.fecha_hora.asc()).all()
    
    @staticmethod
    def get_hoy():
        """Obtiene las consultas de hoy"""
        hoy = datetime.now().date()
        return Consulta.query.filter(
            db.func.cast(Consulta.fecha_hora, db.Date) == hoy
        ).order_by(Consulta.fecha_hora.asc()).all()
    
    @staticmethod
    def get_by_mascota(id_mascota):
        """Obtiene el historial de consultas de una mascota"""
        return Consulta.query.filter_by(id_mascota=id_mascota)\
            .order_by(Consulta.fecha_hora.desc()).all()
    
    @staticmethod
    def get_by_periodo(fecha_inicio, fecha_fin):
        """Obtiene consultas en un período"""
        return Consulta.query.filter(
            db.and_(
                Consulta.fecha_hora >= fecha_inicio,
                Consulta.fecha_hora <= fecha_fin
            )
        ).order_by(Consulta.fecha_hora.desc()).all()
    
    @staticmethod
    def get_by_usuario(id_usuario):
        """Obtiene consultas registradas por un usuario"""
        return Consulta.query.filter_by(id_usuario_registro=id_usuario)\
            .order_by(Consulta.fecha_hora.desc()).all()
