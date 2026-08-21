from DB import DB

dbEvery = DB('./Every.db')
dbEvery.query('INSERT INTO Usuario VALUES ("1", "Paco", "Ejemplo System prompt")')