# models.py
from conexion.conexion import db  # <--- IMPORTANTE: Importamos el db que ya existe
from flask_login import UserMixin

# ════════════════════════════════════════════
# MODELO - USUARIO
# ════════════════════════════════════════════


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios' # Coincide con DBeaver

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), unique=True, nullable=False) # Aquí se guarda el correo
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='vendedor')
    
    # Relación para escalabilidad futura
    ventas_realizadas = db.relationship('Venta', backref='vendedor', lazy=True)

    def __init__(self, nombre, usuario, password, rol='vendedor'):
        self.nombre = nombre
        self.usuario = usuario
        self.password = password
        self.rol = rol

    # Métodos de utilidad corregidos
    def get_nombre(self): return self.nombre
    def get_usuario(self): return self.usuario
    def get_rol(self): return self.rol
    def es_admin(self): return self.rol == 'admin'

    def __repr__(self):
        return f'<Usuario {self.usuario}>'


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

    # Relación con ventas
    ventas = db.relationship('Venta', backref='cliente', lazy=True)

    def __init__(self, nombre, cedula, telefono=None, email=None, direccion=None):
        self.nombre    = nombre
        self.cedula    = cedula
        self.telefono  = telefono
        self.email     = email
        self.direccion = direccion

    def get_nombre(self):   return self.nombre
    def get_cedula(self):   return self.cedula
    def get_telefono(self): return self.telefono
    def get_email(self):    return self.email

    def to_dict(self):
        return {
            'id':        self.id,
            'nombre':    self.nombre,
            'cedula':    self.cedula,
            'telefono':  self.telefono,
            'email':     self.email,
            'direccion': self.direccion
        }

    def __repr__(self):
        return f'<Cliente {self.nombre}>'
