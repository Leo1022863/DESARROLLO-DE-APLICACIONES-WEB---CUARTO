import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        # Estas líneas deben tener un espacio (Tab) a la derecha
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  
            database='licoreria_db',
            port=3306
        )
        if connection.is_connected():
            return connection
            
    except Error as e:
        # Esta línea también debe tener un espacio a la derecha
        print(f"Error al conectar a MySQL: {e}")
        return None