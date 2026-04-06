# app.py
import os
import json
import csv
import io
from datetime import datetime


# En app.py, reemplaza tu importación de modelos por esta:
from models import Usuario, Cliente, Producto, Categoria, Venta, DetalleVenta

from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

# 1. Importamos la conexión y el objeto db único
from conexion.conexion import db, configurar_db

# 2. Inicializamos la App y configuramos la DB de inmediato
app = Flask(__name__)
app.config['SECRET_KEY'] = 'licoreria2026_segura'
configurar_db(app)

# 3. Importamos los modelos y formularios (DESPUÉS de configurar_db para evitar ImportErrors)
from models import Usuario, Cliente
from forms import RegistroForm, LoginForm, ProductoForm, ClienteForm, BuscarForm, VentaForm

# 4. Importamos el Servicio (Asegúrate de que la carpeta se llame 'services')
from services.inventario_service import Inventario

# 5. CONFIGURACIÓN DE FLASK-LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "⚠️ Acceso restringido. Por favor inicia sesión."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# 6. INSTANCIA GLOBAL DEL SERVICIO
inventario_obj = Inventario()

# 7. CARGA INICIAL DE DATOS (Soluciona el 'Working outside of application context')
with app.app_context():
    try:
        # Sincroniza la colección en memoria con MySQL
        inventario_obj.cargar_desde_db()
        print("✅ Inventario sincronizado correctamente con la base de datos.")
    except Exception as e:
        print(f"⚠️ Error en carga inicial del inventario: {e}")

#app = Flask(__name__)
#app.secret_key = 'licoreria2025'
#app.config['WTF_CSRF_CHECK_DEFAULT'] = False

# ────────────────────────────────────────────
# CONEXION A LA BASE DE DATOS SQLITE
# ────────────────────────────────────────────
#--app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licoreria.db' --#

# Ahora (MySQL):
# Así debe quedar si tu usuario root no tiene clave:
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/licoreria_db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

# ────────────────────────────────────────────
# CONEXION A LA BASE DE DATOS EXTERNA MYSQL
# ────────────────────────────────────────────


# ════════════════════════════════════════════
# COLECCIONES PARA GESTIÓN DEL INVENTARIO
# ════════════════════════════════════════════

# ── TUPLA: categorías fijas del negocio ──
# No cambian, por eso se usa tupla (inmutable)
CATEGORIAS = ('Whisky', 'Ron', 'Cerveza', 'Vino', 'Vodka', 'Otros')

# ── CONJUNTO: marcas registradas (sin duplicados) ──
# El conjunto garantiza que no haya marcas repetidas
MARCAS = {'Zhumir', 'Cristal', 'Pilsener', 'Club', 'Johnnie Walker', 'Smirnoff'}

# ── DICCIONARIO: información del negocio ──
INFO_NEGOCIO = {
    'nombre':    'Licorería Central',
    'ciudad':    'Quito',
    'telefono':  '099-000-0000',
    'moneda':    'USD',
    'version':   '1.0'
}

# ── FUNCIONES CON COLECCIONES ──

def obtener_resumen_inventario():
    """Retorna un diccionario con estadísticas del inventario"""
    productos = Producto.query.all()

    # Lista de precios
    precios = [p.precio for p in productos]

    # Lista de stocks
    stocks = [p.stock for p in productos]

    # Conjunto de categorías únicas en uso
    categorias_en_uso = {p.categoria for p in productos}

    # Conjunto de marcas únicas en uso
    marcas_en_uso = {p.marca for p in productos}

    # Diccionario resumen
    resumen = {
        'total_productos':  len(productos),
        'precio_promedio':  round(sum(precios) / len(precios), 2) if precios else 0,
        'precio_max':       max(precios) if precios else 0,
        'precio_min':       min(precios) if precios else 0,
        'stock_total':      sum(stocks),
        'categorias_en_uso': list(categorias_en_uso),
        'marcas_en_uso':    list(marcas_en_uso),
        'productos_agotados': [p.nombre for p in productos if p.stock == 0],
        'productos_bajos':    [p.nombre for p in productos if 0 < p.stock < 5],
    }
    return resumen


def agrupar_por_categoria():
    """Retorna un diccionario agrupando productos por categoría"""
    productos = Producto.query.all()
    agrupado = {}

    for p in productos:
        if p.categoria not in agrupado:
            agrupado[p.categoria] = []       # lista vacía por categoría
        agrupado[p.categoria].append({
            'nombre': p.nombre,
            'marca':  p.marca,
            'precio': p.precio,
            'stock':  p.stock
        })
    return agrupado

# ════════════════════════════════════════════
# RUTAS - CLIENTES
# ════════════════════════════════════════════

# ── Listar clientes ──
@app.route('/clientes')
@login_required  # <--- Protege esta ruta para que solo usuarios logueados puedan verla
def clientes():
    lista = Cliente.query.all()
    total = len(lista)
    return render_template('clientes.html', clientes=lista, total=total)
# ── Agregar cliente (Ruta Unificada) ──
@app.route('/clientes/agregar', methods=['GET', 'POST'])
def agregar_cliente():
    form = ClienteForm()
    
    if form.validate_on_submit():
        # Los datos pasaron las reglas de forms.py
        nuevo_cliente = Cliente(
            nombre=form.nombre.data,
            cedula=form.cedula.data,
            telefono=form.telefono.data,
            email=form.email.data,
            direccion=form.direccion.data
        )
        
        try:
            db.session.add(nuevo_cliente)
            db.session.commit()
            flash('✅ Cliente guardado exitosamente en el sistema.', 'success')
            return redirect(url_for('clientes')) # <--- Asegúrate que este nombre sea igual al 'def'
            
        except IntegrityError:
            db.session.rollback()
            # Este error ocurre si la cédula ya existe en DBeaver
            flash('❌ Error de Auditoría: La cédula ya está registrada para otro cliente.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error inesperado: {str(e)}', 'danger')
    
    # ── DETECCIÓN DE ERRORES DE VALIDACIÓN ──
    # Si el formulario NO es válido, esto nos dirá por qué en la terminal y en la web
    if form.errors:
        print(f"Errores encontrados: {form.errors}") # Revisa tu terminal de VS Code
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo {getattr(form, field).label.text}: {error}", 'warning')

    return render_template('agregar_cliente.html', form=form)

# ── Editar cliente ──
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre    = request.form['nombre']
        cliente.cedula    = request.form['cedula']
        cliente.telefono  = request.form.get('telefono', '')
        cliente.email     = request.form.get('email', '')
        cliente.direccion = request.form.get('direccion', '')
        db.session.commit()
        flash('✅ Cliente actualizado correctamente', 'success')
        return redirect(url_for('clientes'))
    return render_template('editar_cliente.html', cliente=cliente)

# ── Eliminar cliente ──
@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('🗑️ Cliente eliminado', 'danger')
    return redirect(url_for('clientes'))

# ────────────────────────────────────────────
# RUTAS
# ────────────────────────────────────────────

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')



# ── SECCIÓN INVENTARIO (Semana 15) ──
@app.route('/inventario', methods=['GET', 'POST'])
@login_required
def inventario():
    form = BuscarForm()
    
    # Sincronizamos con MySQL antes de mostrar
    inventario_obj.cargar_desde_db()

    if form.validate_on_submit() and form.busqueda.data:
        # Llamada exacta al método del servicio
        productos_lista = inventario_obj.buscar_por_nombre(form.busqueda.data)
    else:
        # Llamada exacta al método del servicio
        productos_lista = inventario_obj.mostrar_todos()

    total = inventario_obj.total_productos()
    
    return render_template('inventario.html', 
                           productos=productos_lista, 
                           total=total, 
                           form=form)

# ── CREATE ──
@app.route('/productos', methods=['GET', 'POST'])
@login_required
def productos():
    form = ProductoForm()
    if form.validate_on_submit():
        nuevo = Producto(
            nombre    = form.nombre.data,
            categoria = form.categoria.data,
            marca     = form.marca.data,
            precio    = form.precio.data,
            stock     = form.stock.data
        )
        db.session.add(nuevo)
        db.session.commit()
        inventario_obj.agregar_producto(nuevo)   # ← agrega al diccionario
        flash('✅ Producto agregado correctamente', 'success')
        return redirect(url_for('inventario'))

    return render_template('productos.html', form=form)

# ── UPDATE ──
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    # Literal 2.3.5: Leer datos de la BD
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)

    if form.validate_on_submit():
        try:
            # Actualizamos usando los métodos de la clase (Encapsulamiento)
            producto.set_nombre(form.nombre.data)
            producto.set_categoria(form.categoria.data)
            producto.set_marca(form.marca.data)
            producto.set_precio(form.precio.data)
            producto.set_stock(form.stock.data)
            
            # Literal 2.3.4: Guardar cambios en SQLite
            db.session.commit()
            
            # Sincronización con la colección (Diccionario)
            inventario_obj.actualizar_producto(id, 
                                               cantidad=producto.stock, 
                                               precio=producto.precio)
            
            flash('✅ Producto actualizado exitosamente', 'success')
            return redirect(url_for('inventario'))
        except ValueError as e:
            db.session.rollback()
            flash(f'❌ Error de validación: {str(e)}', 'danger')

    return render_template('editar.html', form=form, producto=producto)

# ── DELETE ──
@app.route('/eliminar/<int:id>')
def eliminar(id):
    # Buscamos el producto o lanzamos 404 si no existe
    producto = Producto.query.get_or_404(id)
    nombre_borrado = producto.nombre
    
    try:
        # Literal 2.3.3: Interacción de borrado
        db.session.delete(producto)
        db.session.commit()
        
        # Eliminar de la colección en memoria (O(1) con el set de la clase Inventario)
        inventario_obj.eliminar_producto(id)
        
        flash(f'🗑️ El producto "{nombre_borrado}" ha sido eliminado', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ No se pudo eliminar: {str(e)}', 'danger')
        
    return redirect(url_for('inventario'))


# ── Reportes ──
@app.route('/reportes')
@login_required  # <--- Protege esta ruta para que solo usuarios logueados puedan verla
def reportes():
    resumen  = obtener_resumen_inventario()
    agrupado = agrupar_por_categoria()
    return render_template('reportes.html',
                           resumen=resumen,
                           agrupado=agrupado,
                           info=INFO_NEGOCIO)


## ── LOGIN UNIFICADO (Semana 13) ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está logueado, lo mandamos al inicio
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # 1. Buscamos al usuario por su correo/usuario
        user = Usuario.query.filter_by(usuario=form.usuario.data).first()
        
        # 2. Verificamos: ¿Existe el usuario? y ¿La contraseña coincide con el Hash?
        if user and check_password_hash(user.password, form.password.data):
            login_user(user) # <--- Aquí Flask-Login crea la sesión
            flash(f'✅ ¡Bienvenido de nuevo, {user.nombre}!', 'success')
            
            # Si intentó entrar a una página protegida, lo mandamos allá
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('inicio'))
        else:
            flash('❌ Usuario o contraseña incorrectos', 'danger')
            
    return render_template('login.html', form=form)


@app.route('/debug_users')
def debug_users():
    usuarios = Usuario.query.all()
    # Esto imprimirá la lista de usuarios en tu consola/terminal
    for u in usuarios:
        print(f"Usuario: {u.usuario} | Password: {u.password}")
    return "Revisa la terminal de VS Code"


# ── Logout ( añadirlo de una vez) ──
@app.route('/logout')
@login_required # Solo alguien logueado puede desloguearse
def logout():
    logout_user()
    flash(' ✅ Has cerrado sesión correctamente. ¡Vuelve pronto!', 'info')
    return redirect(url_for('login'))

# ── Registro ──
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        # Ciframos la contraseña antes de guardarla
        hashed_password = generate_password_hash(form.password.data)
        
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            usuario=form.usuario.data,
            password=hashed_password, # <--- Guardamos el hash, no la clave real
            rol=form.rol.data
        )
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('✅ Registro exitoso. ¡Ahora puedes iniciar sesión!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('❌ El correo ya está registrado.', 'danger')
            
    return render_template('registro.html', form=form)


# ────────────────────────────────────────────
# EXPORTAR JSON, CSV, TXT
# ────────────────────────────────────────────

# Ruta a la carpeta data
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'inventario', 'data')

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# ── Exportar y guardar JSON ──
@app.route('/exportar/json')
def exportar_json():
    productos = Producto.query.all()
    datos = {
        'fecha_exportacion': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'total_productos':   len(productos),
        'productos':         [p.to_dict() for p in productos]
    }
    contenido = json.dumps(datos, indent=4, ensure_ascii=False)

    # Guardar en archivo local
    with open(os.path.join(DATA_PATH, 'datos.json'), 'w', encoding='utf-8') as f:
        f.write(contenido)

    # Descargar al navegador
    return Response(
        contenido,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=productos.json'}
    )


# ── Exportar y guardar CSV ──
@app.route('/exportar/csv')
def exportar_csv():
    productos = Producto.query.all()

    # Guardar en archivo local
    ruta_csv = os.path.join(DATA_PATH, 'datos.csv')
    with open(ruta_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Nombre', 'Categoria', 'Marca', 'Precio', 'Stock', 'Estado'])
        for p in productos:
            writer.writerow([p.id, p.nombre, p.categoria,
                             p.marca, p.precio, p.stock, p.estado_stock()])

    # Descargar al navegador
    output = io.StringIO()
    writer2 = csv.writer(output)
    writer2.writerow(['ID', 'Nombre', 'Categoria', 'Marca', 'Precio', 'Stock', 'Estado'])
    for p in productos:
        writer2.writerow([p.id, p.nombre, p.categoria,
                          p.marca, p.precio, p.stock, p.estado_stock()])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=productos.csv'}
    )


# ── Exportar y guardar TXT ──
@app.route('/exportar/txt')
def exportar_txt():
    productos = Producto.query.all()
    lineas = [
        '=' * 50,
        '   REPORTE DE INVENTARIO - LICORERIA',
        f'   Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'   Total productos: {len(productos)}',
        '=' * 50, ''
    ]
    for p in productos:
        lineas += [
            f'ID:        {p.id}',
            f'Nombre:    {p.nombre}',
            f'Categoria: {p.categoria}',
            f'Marca:     {p.marca}',
            f'Precio:    ${p.precio:.2f}',
            f'Stock:     {p.stock} unidades',
            f'Estado:    {p.estado_stock()}',
            '-' * 30
        ]
    contenido = '\n'.join(lineas)

    # Guardar en archivo local
    with open(os.path.join(DATA_PATH, 'datos.txt'), 'w', encoding='utf-8') as f:
        f.write(contenido)

    # Descargar al navegador
    return Response(
        contenido,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=reporte.txt'}
    )

# --- RUTA PARA VER LOS ARCHIVOS GUARDADOS ---
import json # Asegúrate de tenerlo arriba

@app.route('/datos')
def ver_datos():
    datos_json_obj = None # Cambiamos de texto vacío a None o un objeto
    contenido_txt = ""
    
    # Leer JSON y convertirlo a objeto Python para usarlo con Bootstrap
    ruta_json = os.path.join(DATA_PATH, 'datos.json')
    if os.path.exists(ruta_json):
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos_json_obj = json.load(f) # <--- Aquí la magia: json.load en lugar de read()

    # Leer TXT (este sí se queda como texto plano)
    ruta_txt = os.path.join(DATA_PATH, 'datos.txt')
    if os.path.exists(ruta_txt):
        with open(ruta_txt, 'r', encoding='utf-8') as f:
            contenido_txt = f.read()

    return render_template('datos.html', 
                           json_obj=datos_json_obj, 
                           txt_data=contenido_txt)


# ── IMPORTAR DESDE JSON ──

@app.route('/importar/json', methods=['POST'])
def importar_json():
    if 'archivo_json' not in request.files:
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('inventario'))
    
    archivo = request.files['archivo_json']
    if archivo.filename == '':
        flash('Archivo sin nombre', 'danger')
        return redirect(url_for('inventario'))

    if archivo and archivo.filename.endswith('.json'):
        try:
            datos = json.load(archivo)
            # 'productos' es la clave que definimos al exportar
            for p_data in datos['productos']:
                # Creamos un nuevo objeto Producto con los datos del JSON
                nuevo_p = Producto(
                    nombre=p_data['nombre'],
                    categoria=p_data['categoria'],
                    marca=p_data['marca'],
                    precio=p_data['precio'],
                    stock=p_data['stock']
                )
                db.session.add(nuevo_p)
            
            db.session.commit()
            flash(f"Se importaron {len(datos['productos'])} productos correctamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el archivo: {str(e)}", "danger")
            
    return redirect(url_for('inventario'))


# ── IMPORTAR DESDE CSV ──
@app.route('/importar/csv', methods=['POST'])
def importar_csv():
    archivo = request.files.get('archivo_csv')
    if not archivo or not archivo.filename.endswith('.csv'):
        flash('Por favor selecciona un archivo CSV válido', 'danger')
        return redirect(url_for('inventario'))

    try:
        # Leer el contenido del archivo subido
        contenido = archivo.read().decode('utf-8')
        lector_csv = csv.DictReader(io.StringIO(contenido))
        
        for fila in lector_csv:
            # Crear objeto Producto desde cada fila del CSV
            nuevo_p = Producto(
                nombre=fila['Nombre'],
                categoria=fila['Categoria'],
                marca=fila['Marca'],
                precio=float(fila['Precio']),
                stock=int(fila['Stock'])
            )
            db.session.add(nuevo_p)
        
        db.session.commit()
        flash("Datos del CSV cargados exitosamente en la Base de Datos.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar CSV: {str(e)}", "danger")
    
    return redirect(url_for('inventario'))

# ── IMPORTAR DESDE TXT ──
@app.route('/importar/txt', methods=['POST'])
def importar_txt():
    archivo = request.files.get('archivo_txt')
    if not archivo or not archivo.filename.endswith('.txt'):
        flash('Selecciona un archivo TXT', 'danger')
        return redirect(url_for('inventario'))

    try:
        # Requisito 2.2.2: Usar lectura de archivo plano
        lineas = archivo.read().decode('utf-8').splitlines()
        for linea in lineas:
            # Suponiendo formato: Nombre,Categoria,Marca,Precio,Stock
            datos = linea.split(',')
            if len(datos) == 5:
                nuevo_p = Producto(
                    nombre=datos[0].strip(),
                    categoria=datos[1].strip(),
                    marca=datos[2].strip(),
                    precio=float(datos[3].strip()),
                    stock=int(datos[4].strip())
                )
                db.session.add(nuevo_p)
        
        db.session.commit()
        flash("Datos del TXT procesados.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error en formato TXT. Use: Nombre,Cat,Marca,Precio,Stock", "danger")
        
    return redirect(url_for('inventario'))



# ──REGISTRAR VENTA──

@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    """Registra una venta usando los campos exactos de la tabla detalle_venta"""
    form = VentaForm()
    # Cargar opciones para los SelectField
    form.cliente_id.choices = [(c.id, f"{c.nombre} ({c.cedula})") for c in Cliente.query.all()]
    form.producto_id.choices = [(p.id, f"{p.nombre} - ${p.precio}") for p in Producto.query.all()]

    if form.validate_on_submit():
        producto = Producto.query.get(form.producto_id.data)
        cantidad_vendida = form.cantidad.data
        
        # 1. Validar stock en el servicio de inventario (memoria)
        if inventario_obj.validar_y_descontar(producto.id, cantidad_vendida):
            try:
                # Calcular total y subtotal
                valor_subtotal = producto.precio * cantidad_vendida
                
                # 2. Crear encabezado de Venta
                nueva_v = Venta(
                    fecha=datetime.now(), 
                    cliente_id=form.cliente_id.data, 
                    usuario_id=current_user.id, 
                    total=valor_subtotal
                )
                db.session.add(nueva_v)
                db.session.flush() # Obtener ID de venta para el detalle

                # 3. Crear DetalleVenta con los campos de tu imagen:
                # id (auto), venta_id, producto_id, cantidad, precio_unit, subtotal
                detalle = DetalleVenta(
                    venta_id=nueva_v.id,
                    producto_id=producto.id,
                    cantidad=cantidad_vendida,
                    precio_unit=producto.precio, # Nombre exacto según tu imagen
                    subtotal=valor_subtotal       # Nombre exacto según tu imagen
                )
                
                # 4. Actualizar stock físico en MySQL
                producto.set_stock(producto.stock - cantidad_vendida)
                
                db.session.add(detalle)
                db.session.commit()
                
                flash('✅ Venta procesada exitosamente', 'success')
                return redirect(url_for('inventario'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Error al guardar en DB: {str(e)}', 'danger')
        else:
            flash('⚠️ No hay suficiente stock disponible', 'warning')

    return render_template('registrar_venta.html', form=form)



    #-- CUANTO SE VENDIO--
@app.route('/reportes')
@login_required
def ver_reportes():
    """
    Genera el reporte de inventario y recupera el historial de ventas 
    utilizando una consulta moderna para evitar advertencias de consola.
    """
    try:
        # --- SECCIÓN: DATOS DE INVENTARIO ---
        # Obtenemos todos los productos para las estadísticas superiores
        productos_all = Producto.query.all()
        
        resumen = {
            'total_productos': len(productos_all),
            'precio_promedio': round(sum(p.precio for p in productos_all) / len(productos_all), 2) if productos_all else 0,
            'stock_total': sum(p.stock for p in productos_all),
            'productos_agotados': [p.nombre for p in productos_all if p.stock == 0],
            'productos_bajos': [p.nombre for p in productos_all if 0 < p.stock <= 5]
        }

        # Agrupamos productos por categoría para las tablas detalladas
        agrupado = {}
        for p in productos_all:
            cat = p.categoria or "Sin Categoría"
            if cat not in agrupado:
                agrupado[cat] = []
            agrupado[cat].append(p)

        # --- SECCIÓN: HISTORIAL DE VENTAS (SOLUCIÓN) ---
        # Realizamos un JOIN explícito para evitar que la tabla aparezca vacía.
        # Usamos labels para asegurar que Jinja2 identifique los nombres correctamente.
        ventas_db = db.session.query(
            Venta.id,
            Venta.fecha,
            Venta.total,
            Cliente.nombre.label('cliente_nombre'),
            Usuario.username.label('vendedor_nombre')
        ).join(Cliente, Venta.cliente_id == Cliente.id)\
         .join(Usuario, Venta.usuario_id == Usuario.id)\
         .order_by(Venta.fecha.desc()).all()

        # Enviamos 'ventas_detalladas' con los resultados de la base de datos
        return render_template(
            'reportes.html', 
            info=INFO_NEGOCIO, 
            resumen=resumen, 
            agrupado=agrupado,
            ventas_detalladas=ventas_db 
        )

    except Exception as e:
        # En caso de error, lo imprimimos para depurar en la terminal
        print(f"Error cargando reportes: {e}")
        return "Hubo un problema al cargar los datos.", 500

if __name__ == '__main__':
    app.run(debug=True)


