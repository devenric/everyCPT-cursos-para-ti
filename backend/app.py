from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from DB import DB
from Chat import Chat

app = Flask(__name__)
CORS(app)
conexion = DB('./Every.db')
# ! AQUI METO TODO LO DEL SYSTEM PROMPT DEL FRONTEND

# ? FLASK
@app.route('/preguntar', methods=['POST']) #mete todo lo de después en una especie de carpeta. Cada vez que se accede a /preguntar, se ejecuta todo lo de dentro. La palabra return significa que llega el final de la ruta.
def atender_pregunta():
    chat1 = Chat('phi3:mini')
    datosRecibidos = request.json
    queryUsuario = datosRecibidos['prompt']
    # Como tu clase ya hace el request.json y el jsonify...
    respuestaChat1 = chat1.procesarPrompt(queryUsuario)
    chat2 = Chat('phi3:mini')
    respuestaChat2 = chat2.procesarPrompt(respuestaChat1)
    jsonificado = jsonify({'respuesta': respuestaChat2})
    return jsonificado
# TODO Recordar investigar sobre la extension del modelo (el modelo se puede extender todo lo que quiera), el aviso de que el modelo por cuestiones de privacidad y rendimiento se ejecute en pc y que el historial se sincronice con el móvil
# ? Además, tengo que hacer más bonito el mensaje devuelto (está todo pegadísimo)
if __name__ == '__main__':
    app.run(debug=True, port=5000)