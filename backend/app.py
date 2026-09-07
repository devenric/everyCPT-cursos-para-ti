from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import login_required, current_user
from extensions import db, login_manager
from models import User
from routes import register_routes
from Chat import Chat

app = Flask(__name__)

# supports_credentials=True es NECESARIO para que la cookie de sesión que
# crea flask_login viaje correctamente entre tu frontend Astro (en otro
# puerto) y este backend. Sin esto, el navegador bloquea la cookie por
# seguridad y current_user aparecería siempre como "no logueado" aunque
# hayas hecho login bien. Desde el frontend, cada fetch() a este backend
# necesita además la opción { credentials: 'include' }.
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'tu-clave-secreta'  # TODO: mover esto a .env antes de subir a producción
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Every.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MODELO = 'qwen2.5:7b-instruct'

db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # flask_login llama a esta función automáticamente en cada petición
    # para reconstruir el objeto User a partir del ID guardado en la cookie.
    # Es el equivalente a: $user = buscarUsuarioPorId($_SESSION['user_id']);
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def no_autorizado():
    # Por defecto, si alguien sin sesión intenta entrar a una ruta con
    # @login_required, flask_login intenta REDIRIGIR a una página de login
    # HTML (porque está pensado para apps clásicas con plantillas). Como
    # tu API habla en JSON, sobreescribimos ese comportamiento para que
    # devuelva un error JSON limpio en su lugar.
    return jsonify({"error": "Necesitas iniciar sesión"}), 401


register_routes(app)

with app.app_context():
    db.create_all()  # crea la tabla User la primera vez; no toca nada si ya existe

# ============================================================
#  Un objeto Chat por usuario logueado, mientras el servidor esté
#  encendido. ANTES había un único 'chat' global compartido por todos.
#  Ahora cada user.id tiene su propia instancia con su propio historial
#  en memoria, y ese historial se sincroniza con la base de datos para
#  que no se pierda si reinicias el servidor.
# ============================================================
chats_activos = {}


def obtener_chat_de(usuario):
    if usuario.id not in chats_activos:
        nuevo_chat = Chat(MODELO)
        nuevo_chat.historial = usuario.get_historial()  # recupera lo que había guardado
        chats_activos[usuario.id] = nuevo_chat
    return chats_activos[usuario.id]


@app.route('/systemPrompt', methods=['POST'])
@login_required
def guardar_perfil():
    datos = request.get_json()
    nuevo_perfil = datos.get('systemPrompt') if datos else None
    if nuevo_perfil is None:
        return jsonify({"error": "Falta el campo 'systemPrompt'"}), 400

    current_user.perfil = nuevo_perfil
    db.session.commit()  # sin esto, el cambio no se guarda de verdad en el .db
    return jsonify({"respuesta": current_user.perfil})


@app.route('/preguntar', methods=['POST'])
@login_required
def atender_pregunta():
    datos = request.get_json()
    pregunta_usuario = datos.get('prompt') if datos else None
    if not pregunta_usuario or pregunta_usuario.strip() == "":
        return jsonify({"error": "Falta el campo 'prompt' o está vacío"}), 400

    chat = obtener_chat_de(current_user)
    respuesta = chat.procesarPrompt(pregunta_usuario, perfil_usuario=current_user.perfil)

    # Guardamos el historial actualizado en la base de datos para que
    # sobreviva a un reinicio del servidor.
    current_user.set_historial(chat.historial)
    db.session.commit()

    return jsonify({'respuesta': respuesta})


if __name__ == '__main__':
    app.run(debug=True, port=5000)