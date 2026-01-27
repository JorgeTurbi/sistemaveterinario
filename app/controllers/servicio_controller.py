"""
Controlador de Servicios
CRUD completo para la gestión de servicios y precios
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.servicio import Servicio

servicio_bp = Blueprint('servicios', __name__)


@servicio_bp.route('/')
@login_required
def index():
    """Lista todos los servicios"""
    busqueda = request.args.get('q', '')
    categoria = request.args.get('categoria', '')

    query = Servicio.query.filter_by(activo=True)

    if busqueda:
        busqueda_like = f"%{busqueda}%"
        query = query.filter(
            db.or_(
                Servicio.codigo.ilike(busqueda_like),
                Servicio.nombre.ilike(busqueda_like),
                Servicio.descripcion.ilike(busqueda_like)
            )
        )

    if categoria:
        query = query.filter_by(categoria=categoria)

    servicios = query.order_by(Servicio.categoria, Servicio.nombre).all()

    return render_template('servicios/index.html',
                           servicios=servicios,
                           busqueda=busqueda,
                           categoria_filtro=categoria,
                           categorias=Servicio.CATEGORIAS)


@servicio_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nuevo servicio"""
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria = request.form.get('categoria', Servicio.CATEGORIA_OTRO)
        precio = request.form.get('precio', '0').strip()
        duracion = request.form.get('duracion_minutos', '').strip()

        # Validaciones
        errores = []

        if not codigo:
            codigo = Servicio.generar_codigo()
        elif Servicio.query.filter_by(codigo=codigo).first():
            errores.append('Ya existe un servicio con este código.')

        if not nombre:
            errores.append('El nombre es requerido.')

        try:
            precio = float(precio.replace(',', '.'))
            if precio < 0:
                errores.append('El precio no puede ser negativo.')
        except ValueError:
            errores.append('El precio debe ser un número válido.')
            precio = 0

        if duracion:
            try:
                duracion = int(duracion)
                if duracion < 0:
                    errores.append('La duración no puede ser negativa.')
            except ValueError:
                errores.append('La duración debe ser un número entero.')
                duracion = None
        else:
            duracion = None

        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('servicios/create.html',
                                   categorias=Servicio.CATEGORIAS)

        # Crear servicio
        servicio = Servicio(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion if descripcion else None,
            categoria=categoria,
            precio=precio,
            duracion_minutos=duracion
        )

        try:
            db.session.add(servicio)
            db.session.commit()
            flash(f'Servicio "{nombre}" creado exitosamente.', 'success')
            return redirect(url_for('servicios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear servicio: {str(e)}', 'danger')

    return render_template('servicios/create.html',
                           categorias=Servicio.CATEGORIAS,
                           codigo_sugerido=Servicio.generar_codigo())


@servicio_bp.route('/<int:id>')
@login_required
def show(id):
    """Ver detalle de un servicio"""
    servicio = Servicio.query.get_or_404(id)
    return render_template('servicios/show.html', servicio=servicio)


@servicio_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar servicio"""
    servicio = Servicio.query.get_or_404(id)

    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria = request.form.get('categoria', Servicio.CATEGORIA_OTRO)
        precio = request.form.get('precio', '0').strip()
        duracion = request.form.get('duracion_minutos', '').strip()

        # Validaciones
        errores = []

        if not codigo:
            errores.append('El código es requerido.')
        else:
            existente = Servicio.query.filter_by(codigo=codigo).first()
            if existente and existente.id_servicio != id:
                errores.append('Ya existe otro servicio con este código.')

        if not nombre:
            errores.append('El nombre es requerido.')

        try:
            precio = float(precio.replace(',', '.'))
            if precio < 0:
                errores.append('El precio no puede ser negativo.')
        except ValueError:
            errores.append('El precio debe ser un número válido.')
            precio = servicio.precio

        if duracion:
            try:
                duracion = int(duracion)
                if duracion < 0:
                    errores.append('La duración no puede ser negativa.')
            except ValueError:
                errores.append('La duración debe ser un número entero.')
                duracion = servicio.duracion_minutos
        else:
            duracion = None

        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('servicios/edit.html',
                                   servicio=servicio,
                                   categorias=Servicio.CATEGORIAS)

        # Actualizar
        servicio.codigo = codigo
        servicio.nombre = nombre
        servicio.descripcion = descripcion if descripcion else None
        servicio.categoria = categoria
        servicio.precio = precio
        servicio.duracion_minutos = duracion

        try:
            db.session.commit()
            flash('Servicio actualizado exitosamente.', 'success')
            return redirect(url_for('servicios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    return render_template('servicios/edit.html',
                           servicio=servicio,
                           categorias=Servicio.CATEGORIAS)


@servicio_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar servicio (eliminación lógica)"""
    servicio = Servicio.query.get_or_404(id)

    try:
        servicio.activo = False
        db.session.commit()
        flash(f'Servicio "{servicio.nombre}" eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')

    return redirect(url_for('servicios.index'))


@servicio_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_activo(id):
    """Activar/Desactivar servicio"""
    servicio = Servicio.query.get_or_404(id)

    try:
        servicio.activo = not servicio.activo
        db.session.commit()
        estado = "activado" if servicio.activo else "desactivado"
        flash(f'Servicio "{servicio.nombre}" {estado}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('servicios.index'))


# =====================================================
# API JSON para AJAX
# =====================================================

@servicio_bp.route('/api/search')
@login_required
def api_search():
    """API para búsqueda de servicios (AJAX)"""
    q = request.args.get('q', '')
    categoria = request.args.get('categoria', '')

    if len(q) < 2 and not categoria:
        return jsonify([])

    query = Servicio.query.filter_by(activo=True)

    if q:
        busqueda_like = f"%{q}%"
        query = query.filter(
            db.or_(
                Servicio.codigo.ilike(busqueda_like),
                Servicio.nombre.ilike(busqueda_like)
            )
        )

    if categoria:
        query = query.filter_by(categoria=categoria)

    servicios = query.order_by(Servicio.nombre).limit(20).all()
    return jsonify([s.to_dict() for s in servicios])


@servicio_bp.route('/api/<int:id>')
@login_required
def api_get(id):
    """API para obtener un servicio por ID"""
    servicio = Servicio.query.get_or_404(id)
    return jsonify(servicio.to_dict())


@servicio_bp.route('/api/categorias')
@login_required
def api_categorias():
    """API para obtener las categorías disponibles"""
    return jsonify(Servicio.CATEGORIAS)
