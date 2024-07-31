from peewee import SqliteDatabase

# Aqui, o programa cria um banco toda vez que é reiniciado, porém, caso o banco já exista, ele não cria, mas usa o que já existe
db = SqliteDatabase('banco_sistema.db')