from modely.klient import Klient
from modely.ucet import Ucet
from databaza.db import get_connection

def prihlasenie():
    print("=== Prihlasenie ===")
    email = input("Email: ")
    heslo = input("Heslo: ")

    klient = Klient.nacitaj_podla_emailu(email)
    if klient is None:
        print("Chyba: Klient s takym emailom neexistuje.")
        return None

    if klient.heslo != heslo:
        print("Chyba: Nespravne heslo.")
        return None

    print(f"Prihlaseny: {klient.meno} {klient.priezvisko} ({klient.rola})")
    return klient

def menu_operator():
    while True:
        print("\n=== MENU OPERÁTOR ===")
        print("1 - Vytvor klienta")
        print("2 - Vytvor účet")
        print("3 - Zobraz všetkých klientov")
        print("4 - Zobraz všetky účty")
        print("5 - Vklad na účet")
        print("6 - Zarátať úrok na účte")
        print("7 - Zmazať klienta")
        print("8 - Zmazať účet")
        print("0 - Odhlásiť")

        volba = input("Zadaj voľbu: ")

        if volba == "1":
            vytvor_klienta()
        elif volba == "2":
            vytvor_ucet()
        elif volba == "3":
            zobraz_vsetkych_klientov()
        elif volba == "4":
            zobraz_vsetky_ucty()
        elif volba == "5":
            vklad_na_ucet()
        elif volba == "6":
            zarataj_urok()
        elif volba == "7":
            zmaz_klienta()
        elif volba == "8":
            zmaz_ucet()
        elif volba == "0":
            break
        else:
            print("Neplatná voľba.")

def menu_majitel(klient):
    while True:
        print("\n=== MENU MAJITEL ===")
        print("1 - Zobraz moje ucty")
        print("2 - Vklad na moj ucet")
        print("3 - Vyber z mojho uctu")
        print("0 - Odhlasit")

        volba = input("Zadaj volbu: ")

        if volba == "1":
            zobraz_moje_ucty(klient)
        elif volba == "2":
            vklad_moj_ucet(klient)
        elif volba == "3":
            vyber_moj_ucet(klient)
        elif volba == "0":
            break
        else:
            print("Neplatna volba.")

def vytvor_klienta():
    print("\n=== Vytvorenie klienta ===")
    meno = input("Meno: ")
    priezvisko = input("Priezvisko: ")
    email = input("Email: ")
    heslo = input("Heslo: ")
    rola = input("Rola (MAJITEL/OPERATOR): ") or "MAJITEL"

    k = Klient(meno=meno, priezvisko=priezvisko, email=email, heslo=heslo, rola=rola)
    try:
        k.uloz_do_db()
        print("Klient vytvoreny, id:", k.id)
    except Exception as e:
        print("Chyba pri vytvarani klienta:", e)

def vytvor_ucet():
    print("\n=== Vytvorenie uctu ===")
    try:
        id_maj = int(input("ID majitela: "))
        zostatok = float(input("Pociatocny zostatok: "))
        urok = float(input("Urok (%): "))
        typ = input("Typ (BEZNE/DOMINUSU): ") or "BEZNE"

        limit = None
        urok_m = None
        if typ == "DOMINUSU":
            limit = float(input("Limit precerpania: "))
            urok_m = float(input("Urok v minuse (%): "))

        u = Ucet(
            id_majitela=id_maj,
            zostatok=zostatok,
            urok=urok,
            typ=typ,
            limit_precerpania=limit,
            urok_v_minuse=urok_m
        )
        u.uloz_do_db()
        print("Ucet vytvoreny, cislo:", u.cislo_uctu)
    except Exception as e:
        print("Chyba pri vytvarani uctu:", e)

def zobraz_vsetky_ucty():
    print("\n=== Vsetky ucty ===")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cislo_uctu, id_majitela, zostatok FROM ucet")
    for cislo, maj, zostatok in cursor.fetchall():
        print(f"Ucet {cislo}, majitel {maj}, zostatok {zostatok}")
    cursor.close()
    conn.close()

def zobraz_vsetkych_klientov():
    print("\n=== Všetci klienti ===")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, meno, priezvisko, email, rola
            FROM klient
            ORDER BY id
        """)
        rows = cursor.fetchall()

        if not rows:
            print("V databáze nie sú žiadni klienti.")
        else:
            for row in rows:
                print(
                    f"ID {row['id']}: {row['meno']} {row['priezvisko']}, "
                    f"email {row['email']}, rola {row['rola']}"
                )

        cursor.close()
        conn.close()
    except Exception as e:
        print("Chyba pri zobrazovaní klientov:", e)

def vklad_na_ucet():
    print("\n=== Vklad na ucet ===")
    try:
        cislo = int(input("Cislo uctu: "))
        suma = float(input("Suma: "))
        u = Ucet.nacitaj_podla_cisla(cislo)
        if u is None:
            print("Ucet neexistuje.")
            return
        u.vklad(suma)
        print("Vklad ok, novy zostatok:", u.zostatok)
    except Exception as e:
        print("Chyba pri vklade:", e)

def zarataj_urok():
    print("\n=== Zaratat urok ===")
    try:
        cislo = int(input("Cislo uctu: "))
        u = Ucet.nacitaj_podla_cisla(cislo)
        if u is None:
            print("Ucet neexistuje.")
            return
        u.zapocitaj_urok()
        print("Urok zaratany, novy zostatok:", u.zostatok)
    except Exception as e:
        print("Chyba pri ucte:", e)

def zobraz_moje_ucty(klient):
    print("\n=== Moje ucty ===")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cislo_uctu, zostatok FROM ucet WHERE id_majitela = %s",
        (klient.id,)
    )
    rows = cursor.fetchall()
    if not rows:
        print("Nemate ziadne ucty.")
    else:
        for cislo, zostatok in rows:
            print(f"Ucet {cislo}, zostatok {zostatok}")
    cursor.close()
    conn.close()

def vklad_moj_ucet(klient):
    print("\n=== Vklad na moj ucet ===")
    try:
        cislo = int(input("Cislo mojho uctu: "))
        suma = float(input("Suma: "))
        u = Ucet.nacitaj_podla_cisla(cislo)
        if u is None or u.id_majitela != klient.id:
            print("Tento ucet vam nepatri.")
            return
        u.vklad(suma)
        print("Vklad ok, novy zostatok:", u.zostatok)
    except Exception as e:
        print("Chyba pri vklade:", e)

def vyber_moj_ucet(klient):
    print("\n=== Vyber z mojho uctu ===")
    try:
        cislo = int(input("Cislo mojho uctu: "))
        suma = float(input("Suma: "))
        u = Ucet.nacitaj_podla_cisla(cislo)
        if u is None or u.id_majitela != klient.id:
            print("Tento ucet vam nepatri.")
            return
        je_dominsu = (u.typ == "DOMINUSU")
        u.vyber(suma, je_majitel=True, je_dominsu=je_dominsu)
        print("Vyber ok, novy zostatok:", u.zostatok)
    except Exception as e:
        print("Chyba pri vybere:", e)

def zmaz_klienta():
    print("\n=== Zmazanie klienta ===")
    try:
        id_klienta = int(input("Zadaj ID klienta na zmazanie: "))

        k = Klient.nacitaj_podla_id(id_klienta) if hasattr(Klient, "nacitaj_podla_id") else None
        if k is None:
            from databaza.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM klient WHERE id = %s", (id_klienta,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row is None:
                print("Klient s týmto ID neexistuje.")
                return

        potvrdenie = input("Naozaj zmazať klienta a jeho účty? (a/n): ").lower()
        if potvrdenie != "a":
            print("Zmazanie zrušené.")
            return

        from databaza.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM ucet WHERE id_majitela = %s", (id_klienta,))
        cursor.execute("DELETE FROM klient WHERE id = %s", (id_klienta,))

        conn.commit()
        cursor.close()
        conn.close()

        print("Klient a jeho účty boli zmazané.")
    except Exception as e:
        print("Chyba pri mazaní klienta:", e)

def zmaz_ucet():
    print("\n=== Zmazanie účtu ===")
    try:
        cislo = int(input("Zadaj číslo účtu na zmazanie: "))

        u = Ucet.nacitaj_podla_cisla(cislo)
        if u is None:
            print("Účet s týmto číslom neexistuje.")
            return

        potvrdenie = input(f"Naozaj zmazať účet {cislo}? (a/n): ").lower()
        if potvrdenie != "a":
            print("Zmazanie zrušené.")
            return

        from databaza.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ucet WHERE cislo_uctu = %s", (cislo,))
        conn.commit()
        cursor.close()
        conn.close()

        print("Účet bol zmazaný.")
    except Exception as e:
        print("Chyba pri mazaní účtu:", e)


def main():
    while True:
        print("\n=== MojaBanka konzola ===")
        print("1 - Prihlasit")
        print("0 - Koniec")
        volba = input("Zadaj volbu: ")

        if volba == "1":
            klient = prihlasenie()
            if klient is None:
                continue
            if klient.rola == "OPERATOR":
                menu_operator(klient)
            else:
                menu_majitel(klient)
        elif volba == "0":
            print("Koniec programu.")
            break
        else:
            print("Neplatna volba.")

if __name__ == "__main__":
    main()
