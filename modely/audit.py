from databaza.db import get_connection
from flask import session

def zaloguj_audit(akcia, detail, email=None, rola=None):
    try:
        if email is None:
            email = session.get("klient_email")
        if rola is None:
            rola = session.get("klient_rola") or "ANONYM"

        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO main_log (email, rola, akcia, detail)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (email, rola, akcia, detail))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass
