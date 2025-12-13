from databaza.db import get_connection

class Ucet:
    def __init__(self, cislo_uctu=None, id_majitela=None,
                 zostatok=0.0, urok=0.0, typ="BEZNE",
                 limit_precerpania=None, urok_v_minuse=None):
        self.cislo_uctu = cislo_uctu
        self.id_majitela = id_majitela
        self.zostatok = zostatok
        self.urok = urok
        self.typ = typ
        self.limit_precerpania = limit_precerpania
        self.urok_v_minuse = urok_v_minuse

    def uloz_do_db(self):
        conn = get_connection()
        cursor = conn.cursor()

        if self.cislo_uctu is None:
            sql = """
                INSERT INTO ucet (id_majitela, zostatok, urok, typ,
                                  limit_precerpania, urok_v_minuse)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                self.id_majitela,
                self.zostatok,
                self.urok,
                self.typ,
                self.limit_precerpania,
                self.urok_v_minuse
            )
            cursor.execute(sql, values)
            conn.commit()
            self.cislo_uctu = cursor.lastrowid
        else:
            sql = """
                UPDATE ucet
                SET id_majitela = %s,
                    zostatok = %s,
                    urok = %s,
                    typ = %s,
                    limit_precerpania = %s,
                    urok_v_minuse = %s
                WHERE cislo_uctu = %s
            """
            values = (
                self.id_majitela,
                self.zostatok,
                self.urok,
                self.typ,
                self.limit_precerpania,
                self.urok_v_minuse,
                self.cislo_uctu
            )
            cursor.execute(sql, values)
            conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def nacitaj_podla_cisla(cislo_uctu):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM ucet WHERE cislo_uctu = %s"
        cursor.execute(sql, (cislo_uctu,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return None

        return Ucet(
            cislo_uctu=row["cislo_uctu"],
            id_majitela=row["id_majitela"],
            zostatok=float(row["zostatok"]),
            urok=float(row["urok"]),
            typ=row["typ"],
            limit_precerpania=row["limit_precerpania"],
            urok_v_minuse=row["urok_v_minuse"]
        )

    def __str__(self):
        return f"Ucet {self.cislo_uctu}, majitel {self.id_majitela}, zostatok {self.zostatok}"
