from DB import DB
db = DB('./Every.db')
class Usuario:
    def __init__(self,ID, username, systemPrompt, historialRespuestas ): # ? No sé porqué quitar lo de historial resuestas, hace que no funcione el chat
        self.ID = ID
        self.username = username
        self.systemPrompt = systemPrompt
        self.historialRespuestas = []
    def login():
        pass
    def registrar():
        pass
        