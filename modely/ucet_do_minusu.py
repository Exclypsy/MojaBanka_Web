from modely.ucet import Ucet
from databaza.db import get_connection

class UcetDoMinusu(Ucet):
    def __init__(self, cislo_uctu=None, id_majitela=None,
                 zostatok=0.0, urok=0.0,
                 limit_precerpania=0.0, urok_v_minuse=0.0):
        super().__init__(
            cislo_uctu=cislo_uctu,
            id_majitela=id_majitela,
            zostatok=zostatok,
            urok=urok,
            typ="DOMINUSU",
            limit_precerpania=limit_precerpania,
            urok_v_minuse=urok_v_minuse
        )

    def vyber(self, suma, je_majitel=True, je_dominsu=False):
        if not je_majitel:
            raise PermissionError("Vyber môže robiť iba majiteľ účtu.")

        suma = float(suma)
        self.zostatok = float(self.zostatok)
        limit = float(self.limit_precerpania or 0)

        max_mozne = self.zostatok + limit
        if suma > max_mozne:
            raise ValueError("Prekročený limit prečerpania.")

        self.zostatok -= suma

        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE ucet SET zostatok = %s WHERE cislo_uctu = %s"
        cursor.execute(sql, (self.zostatok, self.cislo_uctu))
        conn.commit()
        cursor.close()
        conn.close()
        self._zaloguj_operaciu("VYBER", float(suma))
