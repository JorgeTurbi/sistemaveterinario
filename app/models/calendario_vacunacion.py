"""
Modelo: CalendarioVacunacion
Representa el calendario de vacunación de las mascotas
Con trazabilidad de usuario que registra
"""
from app import db
from datetime import datetime, date, timedelta


class CalendarioVacunacion(db.Model):
    """Modelo para la tabla de calendario de vacunación"""
    
    __tablename__ = 'calendario_vacunacion'
    
    # Estados
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_APLICADA = 'Aplicada'
    ESTADO_VENCIDA = 'Vencida'
    ESTADO_CANCELADA = 'Cancelada'
    
    ESTADOS = [ESTADO_PENDIENTE, ESTADO_APLICADA, ESTADO_VENCIDA, ESTADO_CANCELADA]
    
    # Columnas
    id_calendario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascotas.id_mascota'), nullable=False)
    id_vacuna = db.Column(db.Integer, db.ForeignKey('vacunas.id_vacuna'), nullable=False)
    fecha_programada = db.Column(db.Date, nullable=False)
    fecha_aplicacion = db.Column(db.Date)
    fecha_proxima = db.Column(db.Date)
    dosis_numero = db.Column(db.Integer, default=1)
    estado = db.Column(db.String(20), default=ESTADO_PENDIENTE, nullable=False)
    recordatorio_enviado = db.Column(db.Boolean, default=False, nullable=False)
    observaciones = db.Column(db.String(200))
    lote_vacuna = db.Column(db.String(50))
    
    # Veterinario que aplicó la vacuna
    id_veterinario = db.Column(db.Integer, db.ForeignKey('veterinarios.id_veterinario'))
    
    # ============================================
    # TRAZABILIDAD - Usuario que registró/programó
    # ============================================
    id_usuario_registro = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CalendarioVacunacion {self.id_calendario}>'
    
    @property
    def estado_color(self):
        """Retorna el color según el estado"""
        colores = {
            'Pendiente': 'warning',
            'Aplicada': 'success',
            'Vencida': 'danger',
            'Cancelada': 'secondary'
        }
        return colores.get(self.estado, 'info')
    
    @property
    def dias_para_vencer(self):
        """Calcula los días restantes para la vacunación"""
        if self.estado == self.ESTADO_PENDIENTE and self.fecha_programada:
            delta = self.fecha_programada - date.today()
            return delta.days
        return None
    
    @property
    def requiere_recordatorio(self):
        """Verifica si debe enviarse un recordatorio (7 días antes)"""
        if self.estado == self.ESTADO_PENDIENTE and not self.recordatorio_enviado:
            dias = self.dias_para_vencer
            return dias is not None and 0 <= dias <= 7
        return False
    
    def aplicar(self, id_veterinario=None, id_usuario=None, lote=None, observaciones=None):
        """Marca la vacuna como aplicada y programa la siguiente"""
        self.estado = self.ESTADO_APLICADA
        self.fecha_aplicacion = date.today()
        self.id_veterinario = id_veterinario
        self.lote_vacuna = lote
        if observaciones:
            self.observaciones = observaciones
        
        # Calcular próxima fecha si aplica
        if self.vacuna and self.vacuna.intervalo_dias:
            self.fecha_proxima = self.fecha_aplicacion + timedelta(days=self.vacuna.intervalo_dias)
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_calendario,
            'mascota': self.mascota.nombre if self.mascota else None,
            'mascota_id': self.id_mascota,
            'propietario': self.mascota.propietario.nombre if self.mascota and self.mascota.propietario else None,
            'vacuna': self.vacuna.nombre if self.vacuna else None,
            'vacuna_id': self.id_vacuna,
            'fecha_programada': self.fecha_programada.strftime('%Y-%m-%d') if self.fecha_programada else None,
            'fecha_aplicacion': self.fecha_aplicacion.strftime('%Y-%m-%d') if self.fecha_aplicacion else None,
            'fecha_proxima': self.fecha_proxima.strftime('%Y-%m-%d') if self.fecha_proxima else None,
            'dosis_numero': self.dosis_numero,
            'estado': self.estado,
            'estado_color': self.estado_color,
            'dias_para_vencer': self.dias_para_vencer,
            'recordatorio_enviado': self.recordatorio_enviado,
            'observaciones': self.observaciones,
            'lote_vacuna': self.lote_vacuna,
            'veterinario': self.veterinario.nombre if self.veterinario else None,
            # Trazabilidad
            'registrado_por': self.usuario_registro.nombre_completo if self.usuario_registro else None,
            'usuario_registro_id': self.id_usuario_registro
        }
    
    @staticmethod
    def get_pendientes():
        """Obtiene vacunaciones pendientes"""
        return CalendarioVacunacion.query.filter_by(
            estado=CalendarioVacunacion.ESTADO_PENDIENTE
        ).order_by(CalendarioVacunacion.fecha_programada.asc()).all()
    
    @staticmethod
    def get_proximas(dias=7):
        """Obtiene vacunaciones próximas en los siguientes X días"""
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=dias)
        return CalendarioVacunacion.query.filter(
            db.and_(
                CalendarioVacunacion.estado == CalendarioVacunacion.ESTADO_PENDIENTE,
                CalendarioVacunacion.fecha_programada >= hoy,
                CalendarioVacunacion.fecha_programada <= fecha_limite
            )
        ).order_by(CalendarioVacunacion.fecha_programada.asc()).all()
    
    @staticmethod
    def get_vencidas():
        """Obtiene vacunaciones vencidas (pendientes con fecha pasada)"""
        hoy = date.today()
        return CalendarioVacunacion.query.filter(
            db.and_(
                CalendarioVacunacion.estado == CalendarioVacunacion.ESTADO_PENDIENTE,
                CalendarioVacunacion.fecha_programada < hoy
            )
        ).order_by(CalendarioVacunacion.fecha_programada.asc()).all()
    
    @staticmethod
    def get_by_mascota(id_mascota):
        """Obtiene el historial de vacunación de una mascota"""
        return CalendarioVacunacion.query.filter_by(id_mascota=id_mascota)\
            .order_by(CalendarioVacunacion.fecha_programada.desc()).all()
    
    @staticmethod
    def get_by_usuario(id_usuario):
        """Obtiene vacunaciones registradas por un usuario"""
        return CalendarioVacunacion.query.filter_by(id_usuario_registro=id_usuario)\
            .order_by(CalendarioVacunacion.fecha_registro.desc()).all()
    
    @staticmethod
    def actualizar_vencidas():
        """Actualiza el estado de las vacunaciones vencidas"""
        hoy = date.today()
        CalendarioVacunacion.query.filter(
            db.and_(
                CalendarioVacunacion.estado == CalendarioVacunacion.ESTADO_PENDIENTE,
                CalendarioVacunacion.fecha_programada < hoy
            )
        ).update({CalendarioVacunacion.estado: CalendarioVacunacion.ESTADO_VENCIDA})
        db.session.commit()
