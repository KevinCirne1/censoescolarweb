import sqlite3

# 1 - Abri a conexão
connection = sqlite3.connect('DadosBR.db')

# 2 - Cursor
# 3 - Executar
with open('schemas.sql') as f:
    connection.executescript(f.read())

# 4 - Commit ou fecth
connection.commit()

# 5 - Fechar
connection.close()
