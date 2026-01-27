"""
Controlador de Facturación
Gestión completa de facturas y cobros
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.factura import Factura, DetalleFactura
from app.models.servicio import Servicio
from app.models.propietario import Propietario
from app.models.mascota import Mascota
from app.models.consulta import Consulta
from datetime import datetime, timedelta

facturacion_bp = Blueprint('facturacion', __name__)


@facturacion_bp.route('/')
@login_required
def index():
    """Lista de facturas con filtros"""
    busqueda = request.args.get('q', '')
    estado = request.args.get('estado', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    query = Factura.query

    if busqueda:
        busqueda_like = f"%{busqueda}%"
        query = query.join(Propietario).filter(
            db.or_(
                Factura.numero_factura.ilike(busqueda_like),
                Propietario.nombre.ilike(busqueda_like),
                Propietario.documento.ilike(busqueda_like)
            )
        )

    if estado:
        query = query.filter_by(estado=estado)

    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Factura.fecha_emision >= fecha_desde_dt)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Factura.fecha_emision <= fecha_hasta_dt)
        except ValueError:
            pass

    facturas = query.order_by(Factura.fecha_emision.desc()).all()

    # Estadísticas rápidas
    stats = {
        'total_pendiente': sum(float(f.saldo_pendiente) for f in facturas if f.estado in ['Pendiente', 'Pago Parcial']),
        'total_pagado': sum(float(f.monto_pagado or 0) for f in facturas if f.estado == 'Pagada'),
        'num_pendientes': len([f for f in facturas if f.estado == 'Pendiente']),
        'num_pagadas': len([f for f in facturas if f.estado == 'Pagada'])
    }

    return render_template('facturacion/index.html',
                           facturas=facturas,
                           busqueda=busqueda,
                           estado_filtro=estado,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta,
                           estados=Factura.ESTADOS,
                           stats=stats)


@facturacion_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nueva factura"""
    if request.method == 'POST':
        id_propietario = request.form.get('id_propietario')
        id_mascota = request.form.get('id_mascota')
        id_consulta = request.form.get('id_consulta')
        observaciones = request.form.get('observaciones', '').strip()
        aplicar_igv = request.form.get('aplicar_igv') == 'on'

        # Validaciones
        errores = []

        if not id_propietario:
            errores.append('Debe seleccionar un propietario/cliente.')
        else:
            propietario = Propietario.query.get(id_propietario)
            if not propietario:
                errores.append('El propietario seleccionado no existe.')

        if errores:
            for error in errores:
                flash(error, 'danger')
            return redirect(url_for('facturacion.create'))

        # Crear factura
        factura = Factura(
            numero_factura=Factura.generar_numero(),
            id_propietario=id_propietario,
            id_mascota=id_mascota if id_mascota else None,
            id_consulta=id_consulta if id_consulta else None,
            observaciones=observaciones if observaciones else None,
            id_usuario_registro=current_user.id_usuario
        )

        try:
            db.session.add(factura)
            db.session.commit()
            flash(f'Factura {factura.numero_factura} creada. Ahora agregue los servicios.', 'success')
            return redirect(url_for('facturacion.edit', id=factura.id_factura))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear factura: {str(e)}', 'danger')

    propietarios = Propietario.get_activos()
    return render_template('facturacion/create.html', propietarios=propietarios)


@facturacion_bp.route('/<int:id>')
@login_required
def show(id):
    """Ver detalle de una factura"""
    factura = Factura.query.get_or_404(id)
    detalles = factura.detalles.all()
    return render_template('facturacion/show.html', factura=factura, detalles=detalles)


@facturacion_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar factura y agregar/quitar items"""
    factura = Factura.query.get_or_404(id)

    if factura.estado == 'Pagada':
        flash('No se puede editar una factura pagada.', 'warning')
        return redirect(url_for('facturacion.show', id=id))

    if factura.estado == 'Anulada':
        flash('No se puede editar una factura anulada.', 'warning')
        return redirect(url_for('facturacion.show', id=id))

    if request.method == 'POST':
        observaciones = request.form.get('observaciones', '').strip()
        descuento_general = request.form.get('descuento', '0').strip()
        aplicar_igv = request.form.get('aplicar_igv') == 'on'

        try:
            descuento_general = float(descuento_general.replace(',', '.'))
            if descuento_general < 0:
                descuento_general = 0
        except ValueError:
            descuento_general = 0

        factura.observaciones = observaciones if observaciones else None
        factura.descuento = descuento_general
        factura.calcular_totales(aplicar_igv)

        try:
            db.session.commit()
            flash('Factura actualizada exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    detalles = factura.detalles.all()
    servicios = Servicio.get_activos()
    mascotas = factura.propietario.mascotas.filter_by(activo=True).all() if factura.propietario else []

    return render_template('facturacion/edit.html',
                           factura=factura,
                           detalles=detalles,
                           servicios=servicios,
                           mascotas=mascotas)


@facturacion_bp.route('/<int:id>/agregar-item', methods=['POST'])
@login_required
def agregar_item(id):
    """Agregar un item/servicio a la factura"""
    factura = Factura.query.get_or_404(id)

    if factura.estado in ['Pagada', 'Anulada']:
        flash('No se pueden agregar items a esta factura.', 'warning')
        return redirect(url_for('facturacion.show', id=id))

    id_servicio = request.form.get('id_servicio')
    descripcion = request.form.get('descripcion', '').strip()
    cantidad = request.form.get('cantidad', '1').strip()
    precio_unitario = request.form.get('precio_unitario', '0').strip()
    descuento = request.form.get('descuento_item', '0').strip()

    # Validaciones
    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        cantidad = 1

    try:
        precio_unitario = float(precio_unitario.replace(',', '.'))
    except ValueError:
        precio_unitario = 0

    try:
        descuento = float(descuento.replace(',', '.'))
        if descuento < 0:
            descuento = 0
    except ValueError:
        descuento = 0

    # Si seleccionó un servicio, usar sus datos
    servicio = None
    if id_servicio:
        servicio = Servicio.query.get(id_servicio)
        if servicio and not descripcion:
            descripcion = servicio.nombre
        if servicio and precio_unitario == 0:
            precio_unitario = float(servicio.precio)

    if not descripcion:
        flash('La descripción es requerida.', 'danger')
        return redirect(url_for('facturacion.edit', id=id))

    # Crear detalle
    detalle = DetalleFactura(
        id_factura=id,
        id_servicio=servicio.id_servicio if servicio else None,
        descripcion=descripcion,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        descuento=descuento
    )
    detalle.calcular_subtotal()

    try:
        db.session.add(detalle)
        factura.calcular_totales()
        db.session.commit()
        flash(f'Item "{descripcion}" agregado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar item: {str(e)}', 'danger')

    return redirect(url_for('facturacion.edit', id=id))


@facturacion_bp.route('/<int:id>/quitar-item/<int:id_detalle>', methods=['POST'])
@login_required
def quitar_item(id, id_detalle):
    """Quitar un item de la factura"""
    factura = Factura.query.get_or_404(id)
    detalle = DetalleFactura.query.get_or_404(id_detalle)

    if factura.estado in ['Pagada', 'Anulada']:
        flash('No se pueden quitar items de esta factura.', 'warning')
        return redirect(url_for('facturacion.show', id=id))

    if detalle.id_factura != id:
        flash('El item no pertenece a esta factura.', 'danger')
        return redirect(url_for('facturacion.edit', id=id))

    try:
        descripcion = detalle.descripcion
        db.session.delete(detalle)
        factura.calcular_totales()
        db.session.commit()
        flash(f'Item "{descripcion}" eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar item: {str(e)}', 'danger')

    return redirect(url_for('facturacion.edit', id=id))


@facturacion_bp.route('/<int:id>/pagar', methods=['GET', 'POST'])
@login_required
def pagar(id):
    """Registrar pago de factura"""
    factura = Factura.query.get_or_404(id)

    if factura.estado == 'Anulada':
        flash('No se puede pagar una factura anulada.', 'warning')
        return redirect(url_for('facturacion.show', id=id))

    if factura.estado == 'Pagada':
        flash('Esta factura ya está pagada.', 'info')
        return redirect(url_for('facturacion.show', id=id))

    if request.method == 'POST':
        monto = request.form.get('monto', '0').strip()
        metodo_pago = request.form.get('metodo_pago', Factura.METODO_EFECTIVO)

        try:
            monto = float(monto.replace(',', '.'))
            if monto <= 0:
                flash('El monto debe ser mayor a cero.', 'danger')
                return redirect(url_for('facturacion.pagar', id=id))
        except ValueError:
            flash('Monto inválido.', 'danger')
            return redirect(url_for('facturacion.pagar', id=id))

        # Calcular nuevo monto pagado
        monto_pagado_actual = float(factura.monto_pagado or 0)
        nuevo_monto_pagado = monto_pagado_actual + monto
        total = float(factura.total or 0)

        factura.monto_pagado = nuevo_monto_pagado
        factura.metodo_pago = metodo_pago
        factura.fecha_pago = datetime.now()

        # Determinar estado
        if nuevo_monto_pagado >= total:
            factura.estado = Factura.ESTADO_PAGADA
            factura.monto_pagado = total  # No exceder el total
            flash(f'Factura {factura.numero_factura} pagada completamente.', 'success')
        else:
            factura.estado = Factura.ESTADO_PARCIAL
            flash(f'Pago parcial registrado. Saldo pendiente: S/ {factura.saldo_pendiente:.2f}', 'info')

        try:
            db.session.commit()
            return redirect(url_for('facturacion.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar pago: {str(e)}', 'danger')

    return render_template('facturacion/pagar.html',
                           factura=factura,
                           metodos_pago=Factura.METODOS_PAGO)


@facturacion_bp.route('/<int:id>/anular', methods=['POST'])
@login_required
def anular(id):
    """Anular una factura"""
    factura = Factura.query.get_or_404(id)

    if factura.estado == 'Anulada':
        flash('La factura ya está anulada.', 'info')
        return redirect(url_for('facturacion.show', id=id))

    try:
        factura.estado = Factura.ESTADO_ANULADA
        db.session.commit()
        flash(f'Factura {factura.numero_factura} anulada.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al anular factura: {str(e)}', 'danger')

    return redirect(url_for('facturacion.show', id=id))


@facturacion_bp.route('/imprimir/<int:id>')
@login_required
def imprimir(id):
    """Vista de impresión de factura"""
    factura = Factura.query.get_or_404(id)
    detalles = factura.detalles.all()
    return render_template('facturacion/imprimir.html', factura=factura, detalles=detalles)


# =====================================================
# Facturación rápida desde consulta
# =====================================================

@facturacion_bp.route('/desde-consulta/<int:id_consulta>')
@login_required
def desde_consulta(id_consulta):
    """Crear factura desde una consulta"""
    consulta = Consulta.query.get_or_404(id_consulta)

    if not consulta.mascota or not consulta.mascota.propietario:
        flash('La consulta no tiene propietario asociado.', 'danger')
        return redirect(url_for('consultas.show', id=id_consulta))

    # Verificar si ya tiene factura
    if consulta.factura:
        flash('Esta consulta ya tiene una factura asociada.', 'info')
        return redirect(url_for('facturacion.show', id=consulta.factura.id_factura))

    # Crear factura
    factura = Factura(
        numero_factura=Factura.generar_numero(),
        id_propietario=consulta.mascota.id_propietario,
        id_mascota=consulta.id_mascota,
        id_consulta=id_consulta,
        id_usuario_registro=current_user.id_usuario
    )

    try:
        db.session.add(factura)
        db.session.flush()  # Para obtener el ID

        # Agregar costo de consulta si existe
        if consulta.costo and float(consulta.costo) > 0:
            detalle = DetalleFactura(
                id_factura=factura.id_factura,
                descripcion=f"Consulta: {consulta.motivo}",
                cantidad=1,
                precio_unitario=float(consulta.costo),
                descuento=0
            )
            detalle.calcular_subtotal()
            db.session.add(detalle)

        # Agregar tratamientos si existen
        for tratamiento in consulta.tratamientos:
            if tratamiento.costo and float(tratamiento.costo) > 0:
                detalle = DetalleFactura(
                    id_factura=factura.id_factura,
                    descripcion=f"Tratamiento: {tratamiento.descripcion}",
                    cantidad=1,
                    precio_unitario=float(tratamiento.costo),
                    descuento=0
                )
                detalle.calcular_subtotal()
                db.session.add(detalle)

        factura.calcular_totales()
        db.session.commit()
        flash(f'Factura {factura.numero_factura} creada desde la consulta.', 'success')
        return redirect(url_for('facturacion.edit', id=factura.id_factura))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear factura: {str(e)}', 'danger')
        return redirect(url_for('consultas.show', id=id_consulta))


# =====================================================
# API JSON para AJAX
# =====================================================

@facturacion_bp.route('/api/mascotas/<int:id_propietario>')
@login_required
def api_mascotas_propietario(id_propietario):
    """API para obtener mascotas de un propietario"""
    propietario = Propietario.query.get_or_404(id_propietario)
    mascotas = propietario.mascotas.filter_by(activo=True).all()
    return jsonify([{
        'id': m.id_mascota,
        'nombre': m.nombre,
        'especie': m.especie.nombre if m.especie else None
    } for m in mascotas])


@facturacion_bp.route('/api/consultas/<int:id_mascota>')
@login_required
def api_consultas_mascota(id_mascota):
    """API para obtener consultas de una mascota sin facturar"""
    consultas = Consulta.query.filter_by(id_mascota=id_mascota)\
        .filter(Consulta.factura == None)\
        .order_by(Consulta.fecha_hora.desc()).limit(10).all()
    return jsonify([{
        'id': c.id_consulta,
        'fecha': c.fecha_formateada,
        'motivo': c.motivo,
        'costo': float(c.costo) if c.costo else 0
    } for c in consultas])


@facturacion_bp.route('/api/pendientes')
@login_required
def api_pendientes():
    """API para obtener facturas pendientes"""
    facturas = Factura.get_pendientes()
    return jsonify([f.to_dict() for f in facturas])
