from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from Chat import Chat

app = Flask(__name__)
CORS(app)
chat1 = Chat('phi3:mini')
# ! FLASK
@app.route('/preguntar', methods=['POST'])
def atender_pregunta():
    # Como tu clase ya hace el request.json y el jsonify...
    # El trabajador solo llama a tu objeto y devuelve directamente lo que escupa
    return chat1.procesarPrompt()
if chat1.get_system_prompt() == True:
    systemPrompt = chat1.get_system_prompt()
    chat2 = Chat('phi3:mini')
    chat2.get_mensaje_usuario()
    chat2.set_system_prompt()
else:
    exit

if __name__ == '__main__':
    app.run(debug=True, port=5000)