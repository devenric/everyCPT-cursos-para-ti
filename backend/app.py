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
        perfil =  datos.get('systemPrompt')
        debug = datos.get('systemPrompt')
        return jsonify({"respuesta": perfil})
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
    
    print(f"--- DEBUG SYSTEM PROMPT ---")
    print(f"Perfil actual en memoria: '{perfil}'")
    print(f"---------------------------")
 # 1. El primer agente extrae la información objetiva
    chat1 = Chat('qwen2.5:3b')
    respuestaChat1 = chat1.procesarPrompt(queryUsuario)
    
    # 2. Preparamos el agente refinador
    chat2 = Chat('qwen2.5:3b')
    
    if perfil != "":
        chat2.set_system_prompt(perfil)
        
        # 3. La pieza clave: Orden explícita de adaptación
        orden_traduccion = (
            f"Actúa estrictamente bajo tu perfil configurado. "
            f"Tu tarea es reescribir la siguiente información adaptándola a ese tono y estilo exacto, "
            f"teniendo en cuenta este contexto adicional proporcionado por el usuario: '{perfil}'. "
            f"No inventes datos nuevos, solo transforma esta explicación: {respuestaChat1}"
            )        
        respuestaFinal = chat2.procesarPrompt(orden_traduccion) if hasattr(chat2, 'processarPrompt') else chat2.procesarPrompt(orden_traduccion)
        # Si no hay perfil en memoria, evitamos procesar dos veces
    else:
        respuestaFinal = respuestaChat1
    jsonificado = jsonify({'respuesta': respuestaFinal})
    return jsonificado
# TODO Recordar investigar sobre la extension del modelo (el modelo se puede extender todo lo que quiera), el aviso de que el modelo por cuestiones de privacidad y rendimiento se ejecute en pc y que el historial se sincronice con el móvil
# ! Cuando acabe el backend y tenfa el prototipo, hacer: 
# TODO MVC, System prompts en archivos de texto, login y register,que funcione el historial
# ? Además, tengo que hacer más bonito el mensaje devuelto (está todo pegadísimo)
if __name__ == '__main__':
    app.run(debug=True, port=5000)