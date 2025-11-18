from flask import Flask, render_template, g, session, redirect, url_for, Blueprint
import os
import sqlite3
# Importar el blueprint y las funciones de la DB
# Se ha cambiado 'from . import db' y 'from . import user' a importaciones absolutas
# para permitir la ejecución directa con 'python app.py'.
import db
import user

# Crear el Blueprint 'main' para las rutas principales (home)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    """Ruta principal (Home)."""
    # Determinar si el usuario está autenticado
    is_logged_in = 'user_id' in session
    
    # Obtener el nombre del usuario si está logueado para mostrar un saludo
    user_name = None
    if is_logged_in:
        db_conn = db.get_db()
        user_data = db_conn.execute(
            "SELECT name FROM user WHERE id = ?", (session['user_id'],)
        ).fetchone()
        if user_data:
            user_name = user_data['name']
    
    return render_template('home.html', is_logged_in=is_logged_in, user_name=user_name)

def create_app(test_config=None):
    """Función de factoría de la aplicación Flask."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración de la aplicación
    app.config.from_mapping(
        SECRET_KEY='dev', # Cambiar esto en producción
        DATABASE=os.path.join(app.instance_path, db.DATABASE),
    )

    if test_config is None:
        # Cargar la configuración de la instancia si existe
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Cargar la configuración de prueba
        app.config.from_mapping(test_config)

    # Asegurarse de que el directorio de la instancia exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicializar la base de datos
    with app.app_context():
        db.init_db()

    # Registrar funciones de la base de datos para manejar el ciclo de vida de la conexión
    app.teardown_appcontext(db.close_db)

    # Registrar Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(user.bp)
    
    # Establecer la ruta predeterminada de '/' para el blueprint principal
    app.add_url_rule('/', endpoint='main.home')

    return app

# Para ejecución local
if __name__ == '__main__':
    app = create_app()
    # Ejecutar la aplicación
    # NOTA: Para un uso real, las plantillas deben estar en una carpeta 'templates'
    # y el CSS en 'static/css', pero aquí se genera todo el código para el entorno
    # de un solo archivo.
    print("Iniciando la aplicación Flask...")
    app.run(debug=True)