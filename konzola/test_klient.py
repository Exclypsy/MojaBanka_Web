from modely.klient import Klient

def main():
    print("Vytvorenie noveho klienta")
    name = input("Zadajte meno: ")
    surname = input("Zadajte preizvisko: ")
    mail = input("Zadajte email: ")
    password = input("Zadajte heslo: ")
    client_role = input("Zadajte rolu klienta (MAJITEL/OPERATOR): ")
    k = Klient(
        meno=name,
        priezvisko=surname,
        email=mail,
        heslo=password,
        rola=client_role
    )
    k.uloz_do_db()
    print("Ulozeny klient:", k)

    k2 = Klient.nacitaj_podla_emailu(mail)
    print("Nacitany klient:", k2)

if __name__ == "__main__":
    main()
