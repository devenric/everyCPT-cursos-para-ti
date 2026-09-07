from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db

# ============================================================
#  ANTES: render_template('register.html') — esperaba servir una
#  página HTML propia con un <form>, como haría un Flask "clásico".
#
#  AHORA: jsonify({...}) — igual que el resto de tu API (/preguntar,
#  /systemPrompt). Tu frontend Astro seguirá haciendo fetch() a estas
#  rutas y leyendo la respuesta como JSON, en vez de que el navegador
#  cargue una página nueva servida por Flask.
#
#  Es la misma diferencia que en PHP entre un script que hace
#  "echo json_encode([...])" al final, frente a uno que hace
#  "include 'formulario.php'" para pintar HTML.
# ============================================================

def register_routes(app):

    @app.route('/register', methods=['POST'])
    def register():
        datos = request.get_json()
        username = datos.get('username') if datos else None
        password = datos.get('password') if datos else None

        if not username or not password:
            return jsonify({"error": "Faltan usuario o contraseña"}), 400

        if User.query.filter_by(username=username).first():
            # 409 = "Conflict", el código HTTP correcto para "ya existe"
            return jsonify({"error": "Ese usuario ya está registrado"}), 409

        nuevo_usuario = User(username=username)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({"mensaje": "Cuenta creada, ya puedes iniciar sesión"}), 201

    @app.route('/login', methods=['POST'])
    def login():
        datos = request.get_json()
        username = datos.get('username') if datos else None
        password = datos.get('password') if datos else None

        usuario = User.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            # login_user guarda una cookie de sesión segura en el navegador
            # del usuario. A partir de aquí, cualquier ruta con
            # @login_required sabrá quién está preguntando sin que tengas
            # que mandar la contraseña otra vez en cada petición.
            login_user(usuario)
            return jsonify({"mensaje": f"Bienvenido, {usuario.username}"})

        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({"mensaje": "Sesión cerrada"})

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # current_user es un "proxy" que apunta automáticamente al usuario
        # logueado en ESTA petición concreta. Es tu $_SESSION['user_id']
        # ya convertido en el objeto User completo, sin tener que ir
        # a buscarlo tú a la base de datos cada vez.
        return jsonify({
            "username": current_user.username,
            "perfil": current_user.perfil
        })