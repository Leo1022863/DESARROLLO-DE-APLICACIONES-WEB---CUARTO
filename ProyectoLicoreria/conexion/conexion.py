# conexion/conexion.py
from flask_sqlalchemy import SQLAlchemy

# Creamos el objeto db aquí para que sea global
db = SQLAlchemy()

def configurar_db(app):
    # Usamos los mismos datos que ya pusiste, pero en formato URI para SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/licoreria_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializamos la conexión
    db.init_app(app)