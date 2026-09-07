from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import json

# ============================================================
#  ANTES tenías DOS sitios con datos de usuario:
#  - Usuario.py (tu clase antigua, con ID/username/systemPrompt,
#    pero login() y registrar() vacíos con 'pass')
#  - models.py (la clase User de SQLAlchemy, solo con login,
#    sin perfil ni historial)
#
#  Cada una vivía en un archivo .db DISTINTO sin que te dieras cuenta
#  (backend/Every.db vs backend/instance/Every.db). Ahora hay una
#  sola clase, una sola tabla, un solo archivo .db.
#
#  UserMixin: le añade a la clase los métodos que flask_login necesita
#  para gestionar sesiones (is_authenticated, is_active, get_id...).
#  Es el equivalente a que, en PHP puro, tú mismo tuvieras que escribir
#  esas comprobaciones en cada script. Aquí vienen ya hechas.
# ============================================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Esto es lo que antes era la variable global 'perfil' en app.py.
    # Ahora vive en la base de datos, ligado a CADA usuario, no
    # compartido entre todos los que usan la app a la vez.
    perfil = db.Column(db.Text, default="")

    # SQLite no tiene un tipo de dato "lista" nativo, así que el
    # historial de la conversación (una lista de mensajes) lo guardamos
    # como texto en formato JSON, y lo convertimos a lista de Python
    # y viceversa con las dos funciones de abajo. Es un patrón muy
    # común: "serializar" una estructura compleja para guardarla en
    # una columna de texto simple.
    historial_json = db.Column(db.Text, default="[]")

    def set_password(self, password):
        # generate_password_hash = tu password_hash() de PHP.
        # Nunca guardamos la contraseña tal cual, solo su hash.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # check_password_hash = tu password_verify() de PHP.
        return check_password_hash(self.password_hash, password)

    def get_historial(self):
        """Convierte el texto guardado en la DB de vuelta a una lista de Python."""
        return json.loads(self.historial_json) if self.historial_json else []

    def set_historial(self, historial_lista):
        """Convierte la lista de Python a texto para poder guardarla en la DB."""
        self.historial_json = json.dumps(historial_lista)