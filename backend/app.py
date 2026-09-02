from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from DB import DB
from Chat import Chat

app = Flask(__name__)
CORS(app)
conexion = DB('./Every.db')
# ! AQUI METO TODO LO DEL SYSTEM PROMPT DEL FRONTEND

# ? FLASK

perfil = ""
@app.route('/systemPrompt', methods=['POST'])
def biografiaUsuario():
    global perfil
    if request.method == 'POST':
        datos = request.get_json()
        texto =  datos.get('systemPrompt')
        return jsonify({"respuesta": texto})
    # Esto se envía a chat2, para aplicar la explicación a lo que tiene el usuario ahí.
@app.route('/preguntar', methods=['POST']) #mete todo lo de después en una especie de carpeta. Cada vez que se accede a /preguntar, se ejecuta todo lo de dentro. La palabra return significa que llega el final de la ruta.
def atender_pregunta():
    def guardar_perfil():
        global perfil
        # Este json SOLO contiene la información enviada desde el cajón rosa
        datos = request.get_json()
        perfil = datos.get('systemPrompt')
        return jsonify({"estado": "Descripción guardada en memoria"})
    global perfil
    
    # Este json SOLO contiene la duda enviada desde el input inferior
    datos = request.get_json()
    queryUsuario = datos.get('prompt')
    
    # Arrancas tu IA
    chat1 = Chat('phi3:mini')
    respuestaChat1 = chat1.procesarPrompt(queryUsuario)
    
    chat2 = Chat('phi3:mini')
    
    # Si hay algo guardado en la memoria global, se lo inyectas como system prompt
    if perfil != "":
        chat2.set_system_prompt(perfil)
        
    respuestaChat2 = chat2.procesarPrompt(respuestaChat1)
    jsonificado = jsonify({'respuesta': respuestaChat2})
    return jsonificado
# TODO Recordar investigar sobre la extension del modelo (el modelo se puede extender todo lo que quiera), el aviso de que el modelo por cuestiones de privacidad y rendimiento se ejecute en pc y que el historial se sincronice con el móvil
# ! Cuando acabe el backend y tenfa el prototipo, hacer: 
# TODO MVC, System prompts en archivos de texto, login y register,que funcione el historial
# ? Además, tengo que hacer más bonito el mensaje devuelto (está todo pegadísimo)
if __name__ == '__main__':
    app.run(debug=True, port=5000)