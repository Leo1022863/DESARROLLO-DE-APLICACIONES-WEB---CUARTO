from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Length

# ── CONFIGURACIÓN DE CATEGORÍAS ──
CATEGORIAS = [
    ('Whisky', 'Whisky'),
    ('Ron', 'Ron'),
    ('Cerveza', 'Cerveza'),
    ('Vino', 'Vino'),
    ('Vodka', 'Vodka'),
    ('Otros', 'Otros')
]

# ── FORMULARIO AGREGAR / EDITAR PRODUCTO ──
class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del producto',
                        validators=[DataRequired(message='El nombre es obligatorio'),
                                    Length(min=2, max=100)])
    categoria = SelectField('Categoría',
                           choices=CATEGORIAS,
                           validators=[DataRequired()])
    marca = StringField('Marca',
                       validators=[DataRequired(message='La marca es obligatoria'),
                                   Length(min=2, max=50)])
    precio = FloatField('Precio ($)',
                       validators=[DataRequired(),
                                   NumberRange(min=0.01, message='El precio debe ser mayor a 0')])
    stock = IntegerField('Stock (unidades)',
                        validators=[DataRequired(),
                                    NumberRange(min=0, message='El stock no puede ser negativo')])
    submit = SubmitField('Guardar producto')


# ── FORMULARIO BUSCAR PRODUCTO ──
class BuscarForm(FlaskForm):
    busqueda = StringField('Buscar producto',
                          validators=[DataRequired(message='Ingresa un término de búsqueda')])
    submit = SubmitField('Buscar')


# ── FORMULARIO LOGIN ──
class LoginForm(FlaskForm):
    usuario = StringField('Correo electrónico',
                         validators=[DataRequired(message='El usuario es obligatorio'),
                                     Length(min=3, max=100)])
    password = PasswordField('Contraseña',
                            validators=[DataRequired(message='La contraseña es obligatoria'),
                                        Length(min=4)])
    submit = SubmitField('Iniciar sesión')


# ── FORMULARIO REGISTRO (CON ROL) ──
class RegistroForm(FlaskForm):
    nombre = StringField('Nombre completo', 
                        validators=[DataRequired(message='El nombre es obligatorio')])
    
    usuario = StringField('Correo electrónico', 
                         validators=[DataRequired(message='El correo es obligatorio'), 
                                     Email(message='Ingresa un correo válido')])
    
    rol = SelectField('Rol del usuario',
                     choices=[('vendedor', 'Vendedor'), ('administrador', 'Administrador')],
                     validators=[DataRequired(message='Selecciona un rol')])
    
    password = PasswordField('Contraseña', 
                            validators=[DataRequired(message='La contraseña es obligatoria'),
                                        Length(min=4, message='Mínimo 4 caracteres')])
    
    submit = SubmitField('Registrarse')


# ── FORMULARIO AGREGAR CLIENTE (AUDITORÍA) ──
class ClienteForm(FlaskForm):
    nombre = StringField('Nombre completo', 
                        validators=[DataRequired(message='El nombre es obligatorio')])
    
    # Bajamos la restricción de longitud para pruebas
    cedula = StringField('Cédula', 
                        validators=[DataRequired(message='La cédula es obligatoria'),
                                    Length(min=5, max=15, message='Longitud de cédula no permitida')])
    
    telefono = StringField('Teléfono', 
                          validators=[DataRequired(message='El teléfono es obligatorio')])
    
    email = StringField('Email', 
                       validators=[DataRequired(message='El correo es obligatorio'),
                                   Email(message='Formato de correo inválido')])
    
    direccion = StringField('Dirección', 
                           validators=[DataRequired(message='La dirección es obligatoria')])
    
    submit = SubmitField('Guardar Cliente')