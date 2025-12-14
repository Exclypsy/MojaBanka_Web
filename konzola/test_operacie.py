from modely.ucet import Ucet

def main():
    u = Ucet.nacitaj_podla_cisla(1)

    print("Povodny zostatok:", u.zostatok)
    u.vklad(50)
    print("Po vklade:", u.zostatok)

    try:
        u.vyber(30, je_majitel=True)
        print("Po vybere:", u.zostatok)
    except Exception as e:
        print("Chyba pri vybere:", e)

    u.zapocitaj_urok()
    print("Po zapocitani uroku:", u.zostatok)

if __name__ == "__main__":
    main()
