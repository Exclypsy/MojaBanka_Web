from modely.klient import Klient

def main():
    # vytvorenie noveho klienta
    k = Klient(
        meno="Janko",
        priezvisko="Hrasok",
        email="janko@example.com",
        heslo="tajneheslo",   # zatiaľ bez hashovania
        rola="MAJITEL"
    )
    k.uloz_do_db()
    print("Ulozeny klient:", k)

    # nacitanie podla emailu
    k2 = Klient.nacitaj_podla_emailu("janko@example.com")
    print("Nacitany klient:", k2)

if __name__ == "__main__":
    main()
