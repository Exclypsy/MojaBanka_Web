from databaza.db import get_connection
from modely.audit import zaloguj_audit

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

    def vklad(self, suma):
        if suma <= 0:
            raise ValueError("Suma vkladu musi byt kladna.")

        self.zostatok += suma

        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE ucet SET zostatok = %s WHERE cislo_uctu = %s"
        self._zaloguj_operaciu("VKLAD", suma)
        zaloguj_audit("VKLAD", f"ucet={self.cislo_uctu}, suma={suma}")
        cursor.execute(sql, (self.zostatok, self.cislo_uctu))
        conn.commit()
        cursor.close()
        conn.close()

    def vyber(self, suma, je_majitel=True, je_dominsu=False):
        suma = float(suma)
        self.zostatok = float(self.zostatok)
        if self.limit_precerpania is not None:
            self.limit_precerpania = float(self.limit_precerpania)
        if suma <= 0:
            raise ValueError("Suma vyberu musi byt kladna.")

        if not je_majitel:
            raise PermissionError("Vyber moze robit iba majitel uctu.")

        if not je_dominsu:
            if self.zostatok < suma:
                raise ValueError("Nedostatok prostriedkov na ucte.")
        else:
            max_mozne = float(self.zostatok) + float(self.limit_precerpania or 0)
            if suma > max_mozne:
                raise ValueError("Prekroceny limit precerpania.")

        self.zostatok -= suma

        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE ucet SET zostatok = %s WHERE cislo_uctu = %s"
        cursor.execute(sql, (self.zostatok, self.cislo_uctu))
        conn.commit()
        cursor.close()
        conn.close()
        self._zaloguj_operaciu("VYBER", suma)
        zaloguj_audit("VYBER", f"ucet={self.cislo_uctu}, suma={suma}")

    def zapocitaj_urok(self):
        stary = float(self.zostatok)
        if self.zostatok >= 0:
            self.zostatok = self.zostatok * (1 + self.urok / 100.0)
        else:
            if self.urok_v_minuse is None:
                raise ValueError("Pre minusovy ucet chyba urok_v_minuse.")
            self.zostatok = self.zostatok * (1 + self.urok_v_minuse / 100.0)

        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE ucet SET zostatok = %s WHERE cislo_uctu = %s"
        delta = float(self.zostatok) - stary
        self._zaloguj_operaciu("UROK", delta, popis="Započítanie úroku")
        cursor.execute(sql, (self.zostatok, self.cislo_uctu))
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

        if row["typ"] == "DOMINUSU":
            from modely.ucet_do_minusu import UcetDoMinusu
            return UcetDoMinusu(
                cislo_uctu=row["cislo_uctu"],
                id_majitela=row["id_majitela"],
                zostatok=float(row["zostatok"]),
                urok=float(row["urok"]),
                limit_precerpania=row["limit_precerpania"],
                urok_v_minuse=row["urok_v_minuse"]
            )

        return Ucet(
            cislo_uctu=row["cislo_uctu"],
            id_majitela=row["id_majitela"],
            zostatok=float(row["zostatok"]),
            urok=float(row["urok"]),
            typ=row["typ"],
            limit_precerpania=row["limit_precerpania"],
            urok_v_minuse=row["urok_v_minuse"]
        )

    def _zaloguj_operaciu(self, typ_operacie, suma=None, popis=None):
        from databaza.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO transakcia (cislo_uctu, typ_operacie, suma, popis)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (self.cislo_uctu, typ_operacie, suma, popis))
        conn.commit()
        cursor.close()
        conn.close()

    def __str__(self):
        return f"Ucet {self.cislo_uctu}, majitel {self.id_majitela}, zostatok {self.zostatok}"
