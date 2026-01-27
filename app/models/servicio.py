"""
Modelo: Servicio
Representa los servicios ofrecidos por la veterinaria
"""
from app import db
from datetime import datetime


class Servicio(db.Model):
    """Modelo para la tabla de servicios"""

    __tablename__ = 'servicios'

    # Categorías de servicios
    CATEGORIA_CONSULTA = 'Consulta'
    CATEGORIA_CIRUGIA = 'Cirugía'
    CATEGORIA_VACUNACION = 'Vacunación'
    CATEGORIA_LABORATORIO = 'Laboratorio'
    CATEGORIA_ESTETICA = 'Estética'
    CATEGORIA_HOSPITALIZACION = 'Hospitalización'
    CATEGORIA_EMERGENCIA = 'Emergencia'
    CATEGORIA_OTRO = 'Otro'

    CATEGORIAS = [
        CATEGORIA_CONSULTA,
        CATEGORIA_CIRUGIA,
        CATEGORIA_VACUNACION,
        CATEGORIA_LABORATORIO,
        CATEGORIA_ESTETICA,
        CATEGORIA_HOSPITALIZACION,
        CATEGORIA_EMERGENCIA,
        CATEGORIA_OTRO
    ]

    # Columnas
    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50), default=CATEGORIA_OTRO)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    duracion_minutos = db.Column(db.Integer)  # Duración estimada en minutos
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    detalles_factura = db.relationship('DetalleFactura', backref='servicio', lazy='dynamic')

    def __repr__(self):
        return f'<Servicio {self.codigo} - {self.nombre}>'

    @property
    def precio_formateado(self):
        """Retorna el precio en formato moneda"""
        if self.precio:
            return f"S/ {self.precio:,.2f}"
        return "S/ 0.00"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_servicio,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'precio': float(self.precio) if self.precio else 0,
            'precio_formateado': self.precio_formateado,
            'duracion_minutos': self.duracion_minutos,
            'activo': self.activo
        }

    @staticmethod
    def get_activos():
        """Obtiene servicios activos ordenados por categoría y nombre"""
        return Servicio.query.filter_by(activo=True)\
            .order_by(Servicio.categoria, Servicio.nombre).all()

    @staticmethod
    def get_by_categoria(categoria):
        """Obtiene servicios activos de una categoría"""
        return Servicio.query.filter_by(activo=True, categoria=categoria)\
            .order_by(Servicio.nombre).all()

    @staticmethod
    def buscar(termino):
        """Busca servicios por código, nombre o descripción"""
        busqueda = f"%{termino}%"
        return Servicio.query.filter(
            db.and_(
                Servicio.activo == True,
                db.or_(
                    Servicio.codigo.ilike(busqueda),
                    Servicio.nombre.ilike(busqueda),
                    Servicio.descripcion.ilike(busqueda)
                )
            )
        ).order_by(Servicio.nombre).all()

    @staticmethod
    def generar_codigo():
        """Genera un código único para un nuevo servicio"""
        ultimo = Servicio.query.order_by(Servicio.id_servicio.desc()).first()
        if ultimo:
            nuevo_num = ultimo.id_servicio + 1
        else:
            nuevo_num = 1
        return f"SRV-{nuevo_num:04d}"
