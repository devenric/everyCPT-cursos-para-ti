El concepto base que hay que entender antes que nada: el servidor no recuerda nada por sí solo

Esto es lo primero y más importante. Cada vez que el navegador manda una petición HTTP a tu backend (un fetch), para el servidor es como si fuera la primera vez que habla con esa persona — no hay memoria automática de "ah, este ya había iniciado sesión antes". En PHP puro lo resolvías con session_start(), que crea una cookie en el navegador con un ID random, y el servidor guarda en su lado qué usuario corresponde a ese ID. La cookie viaja sola en cada petición siguiente, y así el servidor "recuerda" quién eres.

Flask + flask_login hacen exactamente lo mismo, solo que automatizado. Todo lo demás que te voy a explicar gira en torno a esto: cómo se crea esa cookie, cómo se lee, y qué pasa cuando no existe.

Viaje 1: el registro (POST /register)
El usuario rellena usuario y contraseña en tu frontend, y Astro hace fetch('/register', { method: 'POST', body: JSON.stringify({username, password}) }).
En routes.py, Flask recibe esa petición y ejecuta la función register().
request.get_json() lee el cuerpo de esa petición y lo convierte en un diccionario Python — el equivalente a leer $_POST en PHP, pero como aquí mandamos JSON en vez de un formulario clásico, se usa este método en vez de request.form.
User.query.filter_by(username=username).first() pregunta a la base de datos: "¿ya existe alguien con este nombre?". Esto es tu SELECT * FROM usuarios WHERE username = ? de PHP, pero escrito como Python en vez de SQL.
Si no existe, se crea un objeto User(username=username) — literalmente un objeto Python normal, como cualquier clase que hayas usado. nuevo_usuario.set_password(password) no guarda la contraseña tal cual, la convierte primero en un hash (una versión cifrada e irreversible) — esto es idéntico a password_hash() en PHP. Nunca, nunca se guarda una contraseña en texto plano en una base de datos, ni en PHP ni aquí.
db.session.add(nuevo_usuario) + db.session.commit(): esto son dos pasos separados a propósito. add() es como meter algo en un carrito de la compra — todavía no ha pasado nada de verdad. commit() es pasar por caja: ahí es cuando de verdad se escribe en el archivo .db. Si no llamas a commit(), nada se guarda, por mucho que hayas hecho add().
Viaje 2: el login (POST /login)
Búsqueda del usuario por nombre, igual que antes.
usuario.check_password(password): compara la contraseña que mandó el usuario con el hash guardado. Es tu password_verify() de PHP.
Si coincide, login_user(usuario) es el paso clave de todo esto. Por debajo, esta función:
Genera un identificador de sesión seguro.
Le dice al navegador (a través de las cabeceras HTTP de la respuesta) "guarda esta cookie".
El navegador la guarda automáticamente, sin que tu código de frontend tenga que hacer nada especial — así funcionan las cookies, es un mecanismo del propio navegador, no algo que tú programes.

Desde este momento, cada petición futura que el navegador mande a tu backend incluirá esa cookie automáticamente, siempre que uses fetch con la opción correcta (te explico esto en la parte del frontend).

Viaje 3: preguntar algo en el chat (POST /preguntar), ya logueado

Aquí está la magia de por qué todo esto vale la pena. Fíjate en la ruta:

@app.route('/preguntar', methods=['POST'])
@login_required
def atender_pregunta():

@login_required es un decorador — en Python, un decorador es una función que envuelve a otra y le añade comportamiento extra antes de que se ejecute. Aquí concretamente hace esto: antes de dejar entrar a atender_pregunta(), comprueba si la petición trae una cookie de sesión válida.

Si NO la trae → nunca llega a ejecutarse tu función; se ejecuta automáticamente no_autorizado() (la que definimos en app.py), que devuelve un error JSON de "necesitas iniciar sesión".
Si SÍ la trae → Flask, usando la función load_user() que definimos, va a la base de datos, recupera el usuario correspondiente a esa cookie, y lo deja disponible en la variable mágica current_user dentro de tu función. Tú nunca tienes que buscar manualmente quién es — ya te lo entrega hecho.

Por eso current_user.perfil y current_user.set_historial(...) funcionan sin que tú le pases ningún ID de usuario a mano — el sistema ya sabe quién está preguntando, gracias a la cookie.

Luego, dentro de la función:

obtener_chat_de(current_user) busca si ya existe un objeto Chat en memoria para este usuario (guardado en el diccionario chats_activos). Si no existe (por ejemplo, es su primera pregunta desde que arrancaste el servidor), crea uno nuevo y le carga el historial que tuviera guardado en la base de datos (usuario.get_historial()).
Después de responder, current_user.set_historial(chat.historial) + db.session.commit() guarda el historial actualizado en la base de datos, para que sobreviva si reinicias el servidor.
Por qué extensions.py existe como archivo aparte (esto suele confundir)

app.py, models.py y routes.py necesitan usar el mismo objeto db. Si cada archivo escribiera db = SQLAlchemy() por su cuenta, tendrías tres conexiones distintas sin relación entre sí — como si tres personas usaran la palabra "banco" pero cada una pensando en un banco físico diferente. Al crear db una sola vez en extensions.py, y que todos los demás archivos hagan from extensions import db, todos están hablando literalmente del mismo objeto.