import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",          # zmeň, ak používaš iného užívateľa
        password="",          # ak máš heslo, dopíš sem
        database="banka4SB"
    )
    return conn
