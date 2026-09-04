from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from DB import DB
from Chat import Chat

app = Flask(__name__)
CORS(app)
conexion = DB('./Every.db')
MODELO = 'qwen2.5:7b-instruct'  

# ! AQUI METO TODO LO DEL SYSTEM PROMPT DEL FRONTEND

# ? FLASK

perfil = ""
chat = Chat(MODELO)

@app.route('/systemPrompt', methods=['POST'])
def guardarPerfil():
    global perfil
    if request.method == 'POST':
        datos = request.get_json()
        nuevoperfil =  datos.get('systemPrompt') if datos else None
        if nuevoperfil is None:
            return jsonify({"error": "Falta el campo 'systemPrompt'"}), 400
        perfil = nuevoperfil
        return jsonify({"respuesta": perfil})
#! Que ha cambiado: se verifica que el usuario ha metido un system prompt
@app.route('/preguntar', methods=['POST']) #mete todo lo de después en una especie de carpeta. Cada vez que se accede a /preguntar, se ejecuta todo lo de dentro. La palabra return significa que llega el final de la ruta.

def atender_pregunta():
    global perfil
        # Este json SOLO contiene la información enviada desde el cajón rosa
    datos = request.get_json()
    pregunta_usuario = datos.get('prompt') if datos else None
    if not pregunta_usuario or pregunta_usuario.strip() == "":
        return jsonify({"error": "Falta el campo 'prompt' o está vacío"}), 400
    respuesta = chat.procesarPrompt(pregunta_usuario, perfil_usuario=perfil)
    return jsonify({'respuesta': respuesta})
# TODO Recordar investigar sobre la extension del modelo (el modelo se puede extender todo lo que quiera), el aviso de que el modelo por cuestiones de privacidad y rendimiento se ejecute en pc y que el historial se sincronice con el móvil
# ! Cuando acabe el backend y tenfa el prototipo, hacer: 
# TODO MVC, System prompts en archivos de texto, login y register,que funcione el historial
# ? Además, tengo que hacer más bonito el mensaje devuelto (está todo pegadísimo)
if __name__ == '__main__':
    app.run(debug=True, port=5000)