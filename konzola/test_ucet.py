from modely.klient import Klient
from modely.ucet import Ucet

def main():
    k = Klient.nacitaj_podla_emailu("janko@example.com")
    if k is None:
        print("Klient neexistuje")
        return

    u = Ucet(
        id_majitela=k.id,
        zostatok=200.0,
        urok=1.7,
        typ="BEZNE"
    )
    u.uloz_do_db()
    print("Ulozeny ucet:", u)

    u2 = Ucet.nacitaj_podla_cisla(u.cislo_uctu)
    print("Nacitany ucet:", u2)

if __name__ == "__main__":
    main()
