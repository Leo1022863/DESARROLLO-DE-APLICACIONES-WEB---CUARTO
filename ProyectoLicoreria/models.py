# models.py
from conexion.conexion import db  
from flask_login import UserMixin
from datetime import datetime

# ════════════════════════════════════════════
# MODELO - USUARIO
# ════════════════════════════════════════════
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), unique=True, nullable=False) 
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='vendedor')
    
    ventas_realizadas = db.relationship('Venta', backref='vendedor', lazy=True)

    def __init__(self, nombre, usuario, password, rol='vendedor'):
        self.nombre = nombre
        self.usuario = usuario
        self.password = password
        self.rol = rol

    def get_nombre(self): return self.nombre
    def get_usuario(self): return self.usuario
    def get_rol(self): return self.rol
    def es_admin(self): return self.rol == 'admin'

# ════════════════════════════════════════════
# MODELO - CLIENTE
# ════════════════════════════════════════════
class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula    = db.Column(db.String(20),  nullable=False, unique=True)
    telefono  = db.Column(db.String(20),  nullable=True)
    email     = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)

    # Relación con ventas (Asegúrate de que la clase Venta esté definida en este archivo)
    ventas = db.relationship('Venta', backref='cliente', lazy=True)

    # 1. Constructor (init): Mantenlo tal cual, está muy bien.
    def __init__(self, nombre, cedula, telefono=None, email=None, direccion=None):
        self.nombre    = nombre
        self.cedula    = cedula
        self.telefono  = telefono
        self.email     = email
        self.direccion = direccion

    # 2. Métodos Get (Solucionan el error de Jinja2 en clientes.html)
    def get_nombre(self): return self.nombre
    def get_cedula(self): return self.cedula
    def get_telefono(self): return self.telefono
    def get_email(self): return self.email
    def get_direccion(self): return self.direccion

    # 3. Conversión a diccionario (Útil para exportar JSON)
    def to_dict(self):
        return {
            'id': self.id, 
            'nombre': self.nombre, 
            'cedula': self.cedula,
            'telefono': self.telefono, 
            'email': self.email, 
            'direccion': self.direccion
        }

    # 4. Representación (Opcional, pero ayuda mucho a debuguear en consola)
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
# ════════════════════════════════════════════
# MODELO - PRODUCTO (Semana 15)
# ════════════════════════════════════════════
# models.py - Clase Producto Corregida

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def __init__(self, nombre, categoria, marca, precio, stock):
        self.nombre = nombre
        self.categoria = categoria
        self.marca = marca
        self.precio = precio
        self.stock = stock

    # 1. MÉTODOS GET (Para evitar UndefinedError en el HTML)
    def get_id(self): return self.id
    def get_nombre(self): return self.nombre
    def get_categoria(self): return self.categoria
    def get_marca(self): return self.marca
    def get_precio(self): return self.precio
    def get_stock(self): return self.stock

    # 2. LÓGICA DE NEGOCIO (Estado del stock)
    def estado_stock(self):
        if self.stock == 0: 
            return "Agotado"
        elif self.stock < 5: 
            return "Bajo"
        return "Disponible"

    # 3. SETTERS CON VALIDACIÓN (Para la ruta de edición en app.py)
    def set_nombre(self, val): 
        self.nombre = val
        
    def set_categoria(self, val): 
        self.categoria = val
        
    def set_marca(self, val): 
        self.marca = val
        
    def set_precio(self, val):
        if float(val) <= 0: 
            raise ValueError("El precio debe ser mayor a 0")
        self.precio = float(val)
        
    def set_stock(self, val):
        if int(val) < 0: 
            raise ValueError("El stock no puede ser negativo")
        self.stock = int(val)

    # 4. CONVERSIÓN A DICCIONARIO (Para el InventarioService y JSON)
    def to_dict(self):
        return {
            'id': self.id, 
            'nombre': self.nombre, 
            'categoria': self.categoria,
            'marca': self.marca, 
            'precio': self.precio, 
            'stock': self.stock,
            'estado': self.estado_stock()
        }

    def __repr__(self):
        return f'<Producto {self.nombre}>'
# ════════════════════════════════════════════
# MODELOS ADICIONALES (Ventas y Categorías)
# ════════════════════════════════════════════
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    """Almacena el desglose de productos vendidos (corregido según DB real)"""
    __tablename__ = 'detalle_venta'
    
    # Campos ajustados a tu estructura de MySQL en Quito
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unit = db.Column(db.Float, nullable=False)  # Antes: precio_unitario
    subtotal = db.Column(db.Float, nullable=False)     # Campo nuevo según tu imagen