from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash  # Libreria para Cifrar contraseñas
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import json
import csv
import io
# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response

# 1. Importamos la conexión y el objeto db único
from conexion.conexion import db, configurar_db

# 2. Inicializamos la App y configuramos la DB de inmediato
app = Flask(__name__)
app.config['SECRET_KEY'] = 'licoreria2026_segura'
configurar_db(app)

# 3. Importamos los modelos y formularios (Después de configurar_db)
# Nota: Usuario y Cliente vienen de models.py, Producto y Categoria están abajo.
from models import Usuario, Cliente 
from forms import RegistroForm, LoginForm, ProductoForm, ClienteForm, BuscarForm

# 4. CONFIGURACIÓN DE FLASK-LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "⚠️ Acceso restringido. Por favor inicia sesión."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    # Recupera al usuario de la base de datos por su ID
    return Usuario.query.get(int(user_id))

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


# ────────────────────────────────────────────
# POO - MODELO PRODUCTO
# ────────────────────────────────────────────

class Producto(db.Model):
    __tablename__ = 'productos'

    # ── ATRIBUTOS ──
    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50),  nullable=False)
    marca     = db.Column(db.String(50),  nullable=False)
    precio    = db.Column(db.Float,       nullable=False)
    stock     = db.Column(db.Integer,     nullable=False)

    # ── CONSTRUCTOR ──
    def __init__(self, nombre, categoria, marca, precio, stock):
        self.nombre    = nombre
        self.categoria = categoria
        self.marca     = marca
        self.set_precio(precio)   # usa setter para validar
        self.set_stock(stock)     # usa setter para validar

    # ── GETTERS (obtener atributos) ──
    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre

    def get_categoria(self):
        return self.categoria

    def get_marca(self):
        return self.marca

    def get_precio(self):
        return self.precio

    def get_stock(self):
        return self.stock

    # ── SETTERS (establecer y validar atributos) ──
    def set_nombre(self, nombre):
        if len(nombre) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        self.nombre = nombre

    def set_categoria(self, categoria):
        categorias_validas = ('Whisky', 'Ron', 'Cerveza', 'Vino', 'Vodka', 'Otros')
        if categoria not in categorias_validas:
            raise ValueError(f'Categoría no válida: {categoria}')
        self.categoria = categoria

    def set_marca(self, marca):
        if len(marca) < 2:
            raise ValueError('La marca debe tener al menos 2 caracteres')
        self.marca = marca

    def set_precio(self, precio):
        if precio <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        self.precio = round(precio, 2)

    def set_stock(self, stock):
        if stock < 0:
            raise ValueError('El stock no puede ser negativo')
        self.stock = stock

    # ── MÉTODOS ADICIONALES ──
    def __repr__(self):
        return f'<Producto {self.nombre}>'

    def to_dict(self):
        return {
            'id':        self.get_id(),
            'nombre':    self.get_nombre(),
            'categoria': self.get_categoria(),
            'marca':     self.get_marca(),
            'precio':    self.get_precio(),
            'stock':     self.get_stock()
        }

    def estado_stock(self):
        stock = self.get_stock()
        if stock == 0:
            return 'Agotado'
        elif stock < 5:
            return 'Bajo'
        else:
            return 'Disponible'

    def aplicar_descuento(self, porcentaje):
        if 0 < porcentaje < 100:
            descuento = self.precio * (porcentaje / 100)
            return round(self.precio - descuento, 2)
        raise ValueError('El porcentaje debe estar entre 1 y 99')
        

# ════════════════════════════════════════════
# MODELO - CATEGORÍA
# ════════════════════════════════════════════
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id     = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, nombre):
        self.nombre = nombre

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

    def to_dict(self):
        return {
            'id':     self.id,
            'nombre': self.nombre
        }




# ════════════════════════════════════════════
# MODELO - PROVEEDOR
# ════════════════════════════════════════════
class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20),  nullable=True)
    email    = db.Column(db.String(100), nullable=True)
    productos_str = db.Column(db.String(200), nullable=True)

    def __init__(self, nombre, contacto=None, telefono=None, email=None, productos_str=None):
        self.nombre       = nombre
        self.contacto     = contacto
        self.telefono     = telefono
        self.email        = email
        self.productos_str = productos_str

    def get_nombre(self):   return self.nombre
    def get_contacto(self): return self.contacto
    def get_telefono(self): return self.telefono

    def to_dict(self):
        return {
            'id':        self.id,
            'nombre':    self.nombre,
            'contacto':  self.contacto,
            'telefono':  self.telefono,
            'email':     self.email,
            'productos': self.productos_str
        }

    def __repr__(self):
        return f'<Proveedor {self.nombre}>'


# ════════════════════════════════════════════
# MODELO - VENTA
# ════════════════════════════════════════════
class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    total = db.Column(db.Float)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relación con detalle
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True, cascade="all, delete-orphan")
    

    def __init__(self, fecha, cliente_id, usuario_id, total=0.0):
        self.fecha = fecha
        self.cliente_id = cliente_id
        self.usuario_id = usuario_id 
        self.total      = total

    def get_total(self):  return self.total
    def get_fecha(self):  return self.fecha

    def calcular_total(self):
        """Calcula el total sumando los detalles"""
        self.total = sum(d.subtotal for d in self.detalles)
        return self.total

    def to_dict(self):
        return {
        'id': self.id,
        'fecha': self.fecha.strftime('%Y-%m-%d %H:%M'),
        'total': self.total,
        'cliente_id': self.cliente_id,
        'usuario_id': self.usuario_id
    }

    def __repr__(self):
        return f'<Venta {self.id} - ${self.total}>'


# ════════════════════════════════════════════
# MODELO - DETALLE VENTA
# ════════════════════════════════════════════
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'

    id          = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad    = db.Column(db.Integer, nullable=False)
    precio_unit = db.Column(db.Float,   nullable=False)
    subtotal    = db.Column(db.Float,   nullable=False)

    producto = db.relationship('Producto')

    def __init__(self, venta_id, producto_id, cantidad, precio_unit):
        self.venta_id    = venta_id
        self.producto_id = producto_id
        self.cantidad    = cantidad
        self.precio_unit = precio_unit
        self.subtotal    = round(cantidad * precio_unit, 2)

    def get_subtotal(self):   return self.subtotal
    def get_cantidad(self):   return self.cantidad

    def to_dict(self):
        return {
            'id':          self.id,
            'producto_id': self.producto_id,
            'cantidad':    self.cantidad,
            'precio_unit': self.precio_unit,
            'subtotal':    self.subtotal
        }

    def __repr__(self):
        return f'<DetalleVenta producto={self.producto_id} cantidad={self.cantidad}>'



# ════════════════════════════════════════════
# CLASE INVENTARIO (POO + Colecciones)
# ════════════════════════════════════════════
class Inventario:
    def __init__(self):
        self._productos = {}           # Diccionario principal {id: producto}
        self._nombres_index = {}       # Diccionario índice {nombre_lower: id}
        self._categorias_index = {}    # Diccionario índice {categoria: [ids]}
        self._ids_set = set()          # Conjunto de IDs registrados

    def cargar_desde_db(self):
        productos = Producto.query.all()
        self._productos = {}
        self._nombres_index = {}
        self._categorias_index = {}
        self._ids_set = set()

        for p in productos:
            d = p.to_dict()
            d['estado'] = p.estado_stock()
            self._productos[p.id] = d

            # Índice por nombre (búsqueda rápida)
            self._nombres_index[p.nombre.lower()] = p.id

            # Índice por categoría
            if p.categoria not in self._categorias_index:
                self._categorias_index[p.categoria] = []
            self._categorias_index[p.categoria].append(p.id)

            # Conjunto de IDs
            self._ids_set.add(p.id)

        return self._productos

    def agregar_producto(self, producto):
        d = producto.to_dict()
        d['estado'] = producto.estado_stock()
        self._productos[producto.id] = d
        self._nombres_index[producto.nombre.lower()] = producto.id
        self._ids_set.add(producto.id)

        if producto.categoria not in self._categorias_index:
            self._categorias_index[producto.categoria] = []
        self._categorias_index[producto.categoria].append(producto.id)

    def eliminar_producto(self, id):
        if id in self._ids_set:                          # búsqueda O(1) con conjunto
            p = self._productos[id]
            # Limpiar índices
            self._nombres_index.pop(p['nombre'].lower(), None)
            self._categorias_index.get(p['categoria'], []).remove(id)
            del self._productos[id]
            self._ids_set.discard(id)
            return True
        return False

    def actualizar_producto(self, id, cantidad=None, precio=None):
        if id not in self._ids_set:                      # búsqueda O(1) con conjunto
            return False
        if cantidad is not None:
            if cantidad < 0:
                raise ValueError('La cantidad no puede ser negativa')
            self._productos[id]['stock'] = cantidad
        if precio is not None:
            if precio <= 0:
                raise ValueError('El precio debe ser mayor a 0')
            self._productos[id]['precio'] = round(precio, 2)
        return True

    def buscar_por_nombre(self, nombre):
        """Búsqueda parcial usando lista por comprensión"""
        nombre = nombre.lower()
        return [p for p in self._productos.values()
                if nombre in p['nombre'].lower()
                or nombre in p['marca'].lower()]

    def buscar_por_id(self, id):
        """Búsqueda directa O(1) usando diccionario"""
        return self._productos.get(id, None)

    def buscar_por_categoria(self, categoria):
        """Búsqueda usando índice de categorías"""
        ids = self._categorias_index.get(categoria, [])
        return [self._productos[id] for id in ids if id in self._productos]

    def mostrar_todos(self):
        return list(self._productos.values())

    def total_productos(self):
        return len(self._ids_set)                        # O(1) con conjunto

    def existe_id(self, id):
        """Verifica si un ID existe — O(1) con conjunto"""
        return id in self._ids_set

    def get_categorias_activas(self):
        """Retorna conjunto de categorías en uso"""
        return set(self._categorias_index.keys())

    def get_ids_registrados(self):
        """Retorna copia del conjunto de IDs"""
        return self._ids_set.copy()

    def productos_agotados(self):
        return [p for p in self._productos.values() if p['stock'] == 0]

    def productos_stock_bajo(self):
        return [p for p in self._productos.values() if 0 < p['stock'] < 5]

    def precios_como_lista(self):
        """Retorna lista de precios para cálculos"""
        return [p['precio'] for p in self._productos.values()]

    def precio_promedio(self):
        precios = self.precios_como_lista()
        return round(sum(precios) / len(precios), 2) if precios else 0

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



# Instancia global del inventario
inventario_obj = Inventario()

# ── READ ──
@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    form = BuscarForm()
    inventario_obj.cargar_desde_db()

    if form.validate_on_submit():
        productos = inventario_obj.buscar_por_nombre(form.busqueda.data)
    else:
        productos = inventario_obj.mostrar_todos()

    total = inventario_obj.total_productos()
    return render_template('inventario.html',
                           productos=productos,
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
            flash(f'¡Bienvenido de nuevo, {user.nombre}!', 'success')
            
            # Si intentó entrar a una página protegida, lo mandamos allá
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('inicio'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            
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
    flash('Has cerrado sesión correctamente. ¡Vuelve pronto!', 'info')
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


if __name__ == '__main__':
    app.run(debug=True)