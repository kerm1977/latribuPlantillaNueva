from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re
# CORREGIDO: Se cambió 'from .db import ...' a 'from db import ...' para importación absoluta.
from db import get_db, hash_password, check_password

# Definición del Blueprint de 'user'
bp = Blueprint('user', __name__, url_prefix='/user')

# --- Rutas de Autenticación ---

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de nuevos usuarios."""
    if request.method == 'POST':
        db_conn = get_db()
        
        # Recolección de datos
        name = request.form.get('name', '').strip().title()
        first_lastname = request.form.get('first_lastname', '').strip().title()
        second_lastname = request.form.get('second_lastname', '').strip().title() or None
        phone = request.form.get('phone', '').strip()
        birthday = request.form.get('birthday', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validación
        error = None
        
        if not all([name, first_lastname, phone, birthday, email, password, confirm_password]):
            error = 'Todos los campos obligatorios deben ser completados.'
        elif password != confirm_password:
            error = 'Las contraseñas no coinciden.'
        elif len(phone) != 8 or not phone.isdigit():
            error = 'El número de teléfono debe ser exactamente de 8 dígitos y contener solo números.'
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error = 'Formato de email inválido.'
        elif len(password) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres.'
        
        # Comprobación de unicidad de email/teléfono
        if error is None:
            user_exists = db_conn.execute(
                "SELECT id FROM user WHERE email = ? OR phone = ?", (email, phone)
            ).fetchone()
            if user_exists is not None:
                error = 'El email o el número de teléfono ya están registrados.'

        # Registro si no hay errores
        if error is None:
            try:
                hashed_pwd = hash_password(password)
                db_conn.execute(
                    "INSERT INTO user (name, first_lastname, second_lastname, phone, birthday, email, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, first_lastname, second_lastname, phone, birthday, email, hashed_pwd)
                )
                db_conn.commit()
                flash('¡Registro exitoso! Por favor, inicia sesión.', 'success')
                return redirect(url_for('user.login'))
            except Exception as e:
                # Esto captura cualquier otro error de base de datos
                error = f"Ocurrió un error al intentar registrar la cuenta: {e}"

        # Si hay un error, mostrar un mensaje
        if error:
            flash(error, 'danger')

    # Renderizar la plantilla de registro (con errores si los hay)
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios."""
    if request.method == 'POST':
        db_conn = get_db()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = 'remember_me' in request.form
        
        error = None
        user = db_conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
        
        if user is None:
            error = 'Email o contraseña incorrectos.'
        elif not check_password(user['password_hash'], password):
            error = 'Email o contraseña incorrectos.'
            
        if error is None:
            # Login exitoso
            session.clear()
            session['user_id'] = user['id']
            
            # Nota: Flask session por defecto es temporal, 'remember_me' requeriría
            # una configuración de sesión permanente y manejar tokens en un
            # entorno real. Aquí solo usaremos la sesión estándar de Flask.
            
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('main.home'))
            
        # Si hay un error, mostrar un mensaje
        if error:
            flash(error, 'danger')

    # Renderizar la plantilla de inicio de sesión
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    flash('Has cerrado la sesión.', 'info')
    return redirect(url_for('main.home'))