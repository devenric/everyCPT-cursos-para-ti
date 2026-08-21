import sqlite3

class DB:
    # 1. Al crear el objeto, le pasamos el nombre del archivo (ej: 'mi_chat.db')
    def __init__(self, archivo_db):
        # Guardamos ese nombre en la "memoria" de la clase usando self
        self.db = archivo_db

    # 2. Cuando ejecutamos una consulta...
    def query(self, consulta):
        # 3. Usamos self.db para recuperar ese nombre de la memoria
        conexion = sqlite3.connect(self.db)
        
        cursor = conexion.cursor()
        cursor.execute(consulta)
        conexion.commit()
        conexion.close()