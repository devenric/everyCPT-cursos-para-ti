# Este archivo no cambia respecto al tuyo. Su única función es evitar el
# problema de "importación circular": tanto app.py como models.py y routes.py
# necesitan usar 'db', pero si cada uno lo creara por su cuenta, tendrías
# varias bases de datos distintas sin conectar entre sí. Al crearla UNA vez
# aquí y que todos los demás archivos la importen desde aquí, todos hablan
# con la misma base de datos.
#
# Equivalente en PHP puro: sería como tener un único archivo db.php con
# la conexión PDO, e incluirlo (require) en todos los demás scripts en
# vez de abrir una conexión nueva en cada uno.

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()