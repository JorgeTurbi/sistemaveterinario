"""
Modelo: Factura
Representa las facturas emitidas por la veterinaria
"""
from app import db
from datetime import datetime


class Factura(db.Model):
    """Modelo para la tabla de facturas"""

    __tablename__ = 'facturas'

    # Estados de factura
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_PAGADA = 'Pagada'
    ESTADO_PARCIAL = 'Pago Parcial'
    ESTADO_ANULADA = 'Anulada'

    ESTADOS = [ESTADO_PENDIENTE, ESTADO_PAGADA, ESTADO_PARCIAL, ESTADO_ANULADA]

    # Métodos de pago
    METODO_EFECTIVO = 'Efectivo'
    METODO_TARJETA = 'Tarjeta'
    METODO_TRANSFERENCIA = 'Transferencia'
    METODO_YAPE = 'Yape/Plin'
    METODO_OTRO = 'Otro'

    METODOS_PAGO = [METODO_EFECTIVO, METODO_TARJETA, METODO_TRANSFERENCIA, METODO_YAPE, METODO_OTRO]

    # Columnas
    id_factura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    id_propietario = db.Column(db.Integer, db.ForeignKey('propietarios.id_propietario'), nullable=False)
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascotas.id_mascota'), nullable=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id_consulta'), nullable=True)

    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_vencimiento = db.Column(db.Date)

    subtotal = db.Column(db.Numeric(10, 2), default=0)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    igv = db.Column(db.Numeric(10, 2), default=0)  # Impuesto (18% en Perú)
    total = db.Column(db.Numeric(10, 2), default=0)

    estado = db.Column(db.String(20), default=ESTADO_PENDIENTE, nullable=False)
    metodo_pago = db.Column(db.String(30))
    fecha_pago = db.Column(db.DateTime)
    monto_pagado = db.Column(db.Numeric(10, 2), default=0)

    observaciones = db.Column(db.Text)

    # Trazabilidad
    id_usuario_registro = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    propietario = db.relationship('Propietario', backref=db.backref('facturas', lazy='dynamic'))
    mascota = db.relationship('Mascota', backref=db.backref('facturas', lazy='dynamic'))
    consulta = db.relationship('Consulta', backref=db.backref('factura', uselist=False))
    usuario_registro = db.relationship('Usuario', backref=db.backref('facturas_registradas', lazy='dynamic'))
    detalles = db.relationship('DetalleFactura', backref='factura', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Factura {self.numero_factura}>'

    @property
    def fecha_formateada(self):
        """Retorna la fecha en formato legible"""
        if self.fecha_emision:
            return self.fecha_emision.strftime('%d/%m/%Y %H:%M')
        return None

    @property
    def estado_color(self):
        """Retorna el color según el estado"""
        colores = {
            'Pendiente': 'warning',
            'Pagada': 'success',
            'Pago Parcial': 'info',
            'Anulada': 'danger'
        }
        return colores.get(self.estado, 'secondary')

    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago"""
        monto_pagado = float(self.monto_pagado) if self.monto_pagado else 0
        total = float(self.total) if self.total else 0
        return total - monto_pagado

    def calcular_totales(self, aplicar_igv=True):
        """Calcula subtotal, IGV y total basado en los detalles"""
        subtotal = sum(float(d.subtotal) for d in self.detalles)
        self.subtotal = subtotal
        self.igv = subtotal * 0.18 if aplicar_igv else 0
        descuento = float(self.descuento) if self.descuento else 0
        self.total = subtotal + float(self.igv) - descuento

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_factura,
            'numero_factura': self.numero_factura,
            'propietario': self.propietario.nombre if self.propietario else None,
            'propietario_id': self.id_propietario,
            'mascota': self.mascota.nombre if self.mascota else None,
            'mascota_id': self.id_mascota,
            'fecha_emision': self.fecha_emision.strftime('%Y-%m-%d %H:%M') if self.fecha_emision else None,
            'fecha_formateada': self.fecha_formateada,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'descuento': float(self.descuento) if self.descuento else 0,
            'igv': float(self.igv) if self.igv else 0,
            'total': float(self.total) if self.total else 0,
            'estado': self.estado,
            'estado_color': self.estado_color,
            'metodo_pago': self.metodo_pago,
            'monto_pagado': float(self.monto_pagado) if self.monto_pagado else 0,
            'saldo_pendiente': self.saldo_pendiente,
            'num_items': self.detalles.count(),
            'registrado_por': self.usuario_registro.nombre_completo if self.usuario_registro else None
        }

    @staticmethod
    def get_pendientes():
        """Obtiene facturas pendientes de pago"""
        return Factura.query.filter(
            Factura.estado.in_([Factura.ESTADO_PENDIENTE, Factura.ESTADO_PARCIAL])
        ).order_by(Factura.fecha_emision.desc()).all()

    @staticmethod
    def get_by_propietario(id_propietario):
        """Obtiene facturas de un propietario"""
        return Factura.query.filter_by(id_propietario=id_propietario)\
            .order_by(Factura.fecha_emision.desc()).all()

    @staticmethod
    def get_by_periodo(fecha_inicio, fecha_fin):
        """Obtiene facturas en un período"""
        return Factura.query.filter(
            db.and_(
                Factura.fecha_emision >= fecha_inicio,
                Factura.fecha_emision <= fecha_fin
            )
        ).order_by(Factura.fecha_emision.desc()).all()

    @staticmethod
    def generar_numero():
        """Genera un número de factura único"""
        hoy = datetime.now()
        prefijo = f"F{hoy.year}{hoy.month:02d}"

        ultima = Factura.query.filter(
            Factura.numero_factura.like(f"{prefijo}%")
        ).order_by(Factura.id_factura.desc()).first()

        if ultima:
            try:
                ultimo_num = int(ultima.numero_factura[-4:])
                nuevo_num = ultimo_num + 1
            except ValueError:
                nuevo_num = 1
        else:
            nuevo_num = 1

        return f"{prefijo}-{nuevo_num:04d}"


class DetalleFactura(db.Model):
    """Modelo para los detalles/items de una factura"""

    __tablename__ = 'detalles_factura'

    id_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id_factura'), nullable=False)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicios.id_servicio'), nullable=True)

    descripcion = db.Column(db.String(200), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<DetalleFactura {self.id_detalle} - {self.descripcion}>'

    def calcular_subtotal(self):
        """Calcula el subtotal del detalle"""
        precio = float(self.precio_unitario) if self.precio_unitario else 0
        cantidad = self.cantidad if self.cantidad else 1
        descuento = float(self.descuento) if self.descuento else 0
        self.subtotal = (precio * cantidad) - descuento

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_detalle,
            'servicio_id': self.id_servicio,
            'servicio_nombre': self.servicio.nombre if self.servicio else None,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else 0,
            'descuento': float(self.descuento) if self.descuento else 0,
            'subtotal': float(self.subtotal) if self.subtotal else 0
        }
