from databaza.db import get_connection

class Klient:
    def __init__(self, id=None, meno="", priezvisko="", email="", heslo="", rola="MAJITEL"):
        self.id = id
        self.meno = meno
        self.priezvisko = priezvisko
        self.email = email
        self.heslo = heslo
        self.rola = rola

    def uloz_do_db(self):
        conn = get_connection()
        cursor = conn.cursor()

        if self.id is None:
            sql = """
                INSERT INTO klient (meno, priezvisko, email, heslo, rola)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (self.meno, self.priezvisko, self.email, self.heslo, self.rola)
            cursor.execute(sql, values)
            conn.commit()
            self.id = cursor.lastrowid
        else:
            sql = """
                UPDATE klient
                SET meno = %s, priezvisko = %s, email = %s, heslo = %s, rola = %s
                WHERE id = %s
            """
            values = (self.meno, self.priezvisko, self.email, self.heslo, self.rola, self.id)
            cursor.execute(sql, values)
            conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def nacitaj_podla_emailu(email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM klient WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return None

        return Klient(
            id=row["id"],
            meno=row["meno"],
            priezvisko=row["priezvisko"],
            email=row["email"],
            heslo=row["heslo"],
            rola=row["rola"]
        )

    def __str__(self):
        return f"{self.id}: {self.meno} {self.priezvisko} ({self.email}) - {self.rola}"
