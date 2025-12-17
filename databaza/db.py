import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="banka4SB" #zmenit nazov na nazov svojej databazy
    )
    return conn
