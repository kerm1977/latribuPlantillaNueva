import sqlite3
import bcrypt
import os
from flask import g # Importar g para manejo seguro de hilos

# Nombre del archivo de la base de datos
DATABASE = 'db.db'

def get_db():
    """
    Establece la conexión con la base de datos SQLite.
    
    Usa flask.g para asegurar que la conexión se crea y accede en el mismo hilo/contexto
    de la solicitud, previniendo errores de concurrencia.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Habilitar el modo de filas para obtener resultados como diccionarios
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos si está abierta en el contexto actual.
    """
    # pop() elimina la conexión de g y la devuelve (o None si no existe)
    db = g.pop('db', None) 
    if db is not None:
        db.close()

def hash_password(password):
    """Hashea una contraseña usando bcrypt."""
    # Generar un salt y hashear la contraseña
    salt = bcrypt.gensalt()
    # Codificar la contraseña a bytes antes de hashear
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(hashed_password, user_password):
    """Verifica una contraseña hasheada."""
    try:
        # Codificar la contraseña de usuario a bytes antes de la verificación
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        # Captura errores si el hash no tiene el formato correcto
        return False

def init_db():
    """Inicializa la base de datos: crea la tabla de usuarios si no existe y el superusuario."""
    db = get_db()
    
    # 1. Crear la tabla de usuarios
    db.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            first_lastname TEXT NOT NULL,
            second_lastname TEXT NULL,
            phone TEXT NOT NULL UNIQUE, 
            cedula TEXT UNIQUE NULL,
            birthday TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_superuser BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    db.commit()

    # 2. Crear superusuario por defecto (lógica extraída de la salida del usuario)
    DEFAULT_EMAIL = "kenth1977@gmail.com"
    DEFAULT_PASSWORD = "CR129x7848n"
    
    cursor = db.execute("SELECT id FROM user WHERE email = ? AND is_superuser = 1", (DEFAULT_EMAIL,))
    if cursor.fetchone() is None:
        print(f"--> Creando superusuario: {DEFAULT_EMAIL}")
        try:
            hashed_pwd = hash_password(DEFAULT_PASSWORD)
            db.execute("""
                INSERT INTO user (name, first_lastname, second_lastname, phone, birthday, email, password_hash, is_superuser)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Super", # Nombre por defecto
                "User",  # Primer Apellido por defecto
                None,    # Segundo Apellido (opcional)
                "88888888", # Teléfono (8 dígitos por defecto)
                "1977-01-01", # Fecha de Cumpleaños por defecto
                DEFAULT_EMAIL,
                hashed_pwd,
                1
            ))
            db.commit()
            print("--> Superusuario creado exitosamente.")
        except sqlite3.IntegrityError as e:
            print(f"Error al crear el superusuario: {e}")
    else:
        print("--> Superusuario predeterminado ya existe.")

# Para ejecutar la inicialización de la DB por separado si es necesario
if __name__ == '__main__':
    pass