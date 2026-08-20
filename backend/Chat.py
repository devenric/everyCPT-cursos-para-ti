from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import ollama
# nombre clase 
class Chat:
    def __init__(self, modelo, systemPrompt=""):
        self.modelo = modelo
        self.__system_prompt = "Eres un asistente por defecto" # Propiedad privada inicial    
    def procesarPrompt(self):
        datosRecibidos = request.json
        queryUsuario = datosRecibidos['prompt']
# Interactuar con el modelo
        respuesta = ollama.chat(model=self.modelo, messages=[{'role': 'user', 'content': queryUsuario}])
        textoClean = respuesta['message']['content']
#JSON-ificamos la respuesta
        return jsonify({'respuesta': textoClean})
    
    def set_system_prompt(self, nuevo_prompt):
            self.__system_prompt = nuevo_prompt
    
    def get_system_prompt(self):
        return self.__system_prompt
    
    def get_mensaje_usuario(self):
        datosRecibidos = request.json
        return datosRecibidos.get('prompt')