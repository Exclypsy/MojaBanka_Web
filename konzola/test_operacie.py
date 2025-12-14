from modely.ucet import Ucet

def main():
    global input
    u = Ucet.nacitaj_podla_cisla(1)

    while True:
        print("Moznosti operacii:\n"
              "[1] - vklad\n"
              "[2] - vyber\n"
              "[3] - EXIT")

        vstup = int(input("Zadajte moznost: "))

        if vstup == 1:
            try:
                suma = float(input("Zadaj sumu vkladu: "))
                u.vklad(suma)
                print("Vklad prebehol, novy zostatok:", u.zostatok)
            except ValueError as e:
                print("Chyba pri vklade:", e)
        elif vstup == 2:
            try:
                suma = float(input("Zadaj sumu vyberu: "))
                u.vyber(suma, je_majitel=True)
                print("Vyber prebehol, novy zostatok:", u.zostatok)
            except (ValueError, PermissionError) as e:
                print("Chyba pri vybere:", e)
        elif vstup == 3:
            print("bye bye")
            break
        else:
            print("Zadana nespravna moznost")

if __name__ == "__main__":
    main()
