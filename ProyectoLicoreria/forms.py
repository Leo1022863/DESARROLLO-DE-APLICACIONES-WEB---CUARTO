from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

# Tupla de categorías (colección)
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
    nombre    = StringField('Nombre del producto',
                    validators=[DataRequired(message='El nombre es obligatorio'),
                                Length(min=2, max=100)])
    categoria = SelectField('Categoría',
                    choices=CATEGORIAS,
                    validators=[DataRequired()])
    marca     = StringField('Marca',
                    validators=[DataRequired(message='La marca es obligatoria'),
                                Length(min=2, max=50)])
    precio    = FloatField('Precio ($)',
                    validators=[DataRequired(),
                                NumberRange(min=0.01, message='El precio debe ser mayor a 0')])
    stock     = IntegerField('Stock (unidades)',
                    validators=[DataRequired(),
                                NumberRange(min=0, message='El stock no puede ser negativo')])
    submit    = SubmitField('Guardar producto')


# ── FORMULARIO BUSCAR PRODUCTO ──
class BuscarForm(FlaskForm):
    busqueda  = StringField('Buscar producto',
                    validators=[DataRequired(message='Ingresa un término de búsqueda')])
    submit    = SubmitField('Buscar')


# ── FORMULARIO LOGIN ──
class LoginForm(FlaskForm):
    usuario   = StringField('Usuario',
                    validators=[DataRequired(message='El usuario es obligatorio'),
                                Length(min=3, max=50)])
    password  = StringField('Contraseña',
                    validators=[DataRequired(message='La contraseña es obligatoria'),
                                Length(min=4)])
    submit    = SubmitField('Iniciar sesión')


# ── FORMULARIO REGISTRO ──
class RegistroForm(FlaskForm):
    nombre    = StringField('Nombre completo',
                    validators=[DataRequired(), Length(min=3, max=100)])
    usuario   = StringField('Usuario',
                    validators=[DataRequired(), Length(min=3, max=50)])
    password  = StringField('Contraseña',
                    validators=[DataRequired(), Length(min=4)])
    submit    = SubmitField('Registrarse')