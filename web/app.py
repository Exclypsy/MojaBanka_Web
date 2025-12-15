from flask import Flask, render_template, request, redirect, url_for, session
from databaza.db import get_connection
from modely.klient import Klient
from modely.ucet import Ucet

app = Flask(__name__)
app.secret_key = "tajne_tajne"

@app.route("/")
def index():
    if "klient_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    chyba = None
    if request.method == "POST":
        email = request.form.get("email", "")
        heslo = request.form.get("heslo", "")

        klient = Klient.nacitaj_podla_emailu(email)
        if klient is None or klient.heslo != heslo:
            chyba = "Nesprávny email alebo heslo."
        else:
            session["klient_id"] = klient.id
            session["klient_meno"] = klient.meno
            session["klient_rola"] = klient.rola
            session["klient_priezvisko"] = klient.priezvisko
            return redirect(url_for("dashboard"))

    return render_template("login.html", chyba=chyba)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "klient_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        meno=session.get("klient_meno"),
        rola=session.get("klient_rola")
    )

def vyzaduje_prihlasenie():
    if "klient_id" not in session:
        return False
    return True

def vyzaduje_operatora():
    return vyzaduje_prihlasenie() and session.get("klient_rola") == "OPERATOR"

@app.route("/registrovat_klienta", methods=["GET", "POST"])
def registrovat_klienta():
    if not vyzaduje_operatora():
        return redirect(url_for("login"))

    chyba = None
    sprava = None

    if request.method == "POST":
        meno = request.form.get("meno", "").strip()
        priezvisko = request.form.get("priezvisko", "").strip()
        email = request.form.get("email", "").strip()
        heslo = request.form.get("heslo", "").strip()
        rola = request.form.get("rola", "MAJITEL").strip()

        if not meno or not priezvisko or not email or not heslo:
            chyba = "Všetky polia sú povinné."
        else:
            existujuci = Klient.nacitaj_podla_emailu(email)
            if existujuci is not None:
                chyba = "Klient s týmto emailom už existuje."
            else:
                try:
                    k = Klient(meno=meno, priezvisko=priezvisko,
                               email=email, heslo=heslo, rola=rola)
                    k.uloz_do_db()
                    sprava = f"Klient vytvorený, ID: {k.id}"
                except Exception as e:
                    chyba = f"Chyba pri vytváraní klienta: {e}"

    return render_template("registrovat_klienta.html",
                           chyba=chyba, sprava=sprava)

@app.route("/vytvor_ucet", methods=["GET", "POST"])
def vytvor_ucet_web():
    if not vyzaduje_operatora():
        return redirect(url_for("login"))

    chyba = None
    sprava = None

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, meno, priezvisko, email FROM klient ORDER BY id")
    klienti = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == "POST":
        try:
            id_majitela = int(request.form.get("id_majitela", "0"))
            zostatok = float(request.form.get("zostatok", "0"))
            urok = float(request.form.get("urok", "0"))
            typ = request.form.get("typ", "BEZNE")
            limit = request.form.get("limit_precerpania", "")
            urok_m = request.form.get("urok_v_minuse", "")

            limit_val = float(limit) if limit else None
            urok_m_val = float(urok_m) if urok_m else None

            u = Ucet(
                id_majitela=id_majitela,
                zostatok=zostatok,
                urok=urok,
                typ=typ,
                limit_precerpania=limit_val,
                urok_v_minuse=urok_m_val
            )
            u.uloz_do_db()
            sprava = f"Účet vytvorený, číslo: {u.cislo_uctu}"
        except Exception as e:
            chyba = f"Chyba pri vytváraní účtu: {e}"

    return render_template(
        "vytvor_ucet.html",
        chyba=chyba,
        sprava=sprava,
        klienti=klienti
    )
@app.route("/klienti")
def klienti_prehlad():
    if not vyzaduje_operatora():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, meno, priezvisko, email, rola FROM klient ORDER BY id")
    klienti = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("klienti.html", klienti=klienti)


@app.route("/ucty")
def ucty_prehlad():
    if not vyzaduje_operatora():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.cislo_uctu, u.id_majitela, u.zostatok, u.urok, u.typ,
               u.limit_precerpania, u.urok_v_minuse,
               k.meno, k.priezvisko, k.email
        FROM ucet u
        JOIN klient k ON u.id_majitela = k.id
        ORDER BY u.cislo_uctu
    """)
    ucty = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("ucty.html", ucty=ucty)

@app.route("/moje_ucty")
def moje_ucty():
    if not vyzaduje_prihlasenie():
        return redirect(url_for("login"))

    klient_id = session.get("klient_id")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT cislo_uctu, zostatok, urok, typ,
               limit_precerpania, urok_v_minuse
        FROM ucet
        WHERE id_majitela = %s
        ORDER BY cislo_uctu
    """, (klient_id,))
    ucty = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("moje_ucty.html", ucty=ucty)

@app.route("/ucet/<int:cislo_uctu>", methods=["GET", "POST"])
def detail_uctu(cislo_uctu):
    if not vyzaduje_prihlasenie():
        return redirect(url_for("login"))

    klient_id = session.get("klient_id")
    rola = session.get("klient_rola")

    u = Ucet.nacitaj_podla_cisla(cislo_uctu)
    if u is None:
        return "Účet neexistuje.", 404

    if rola != "OPERATOR" and u.id_majitela != klient_id:
        return "Nemáš právo vidieť tento účet.", 403

    chyba = None
    sprava = None

    if request.method == "POST":
        akcia = request.form.get("akcia")

        try:
            if akcia == "vklad":
                suma = float(request.form.get("suma", "0"))
                u.vklad(suma)
                sprava = "Vklad bol úspešný."
            elif akcia == "vyber":
                suma = float(request.form.get("suma", "0"))
                je_dominsu = (u.typ == "DOMINUSU")
                u.vyber(suma, je_majitel=(rola != "OPERATOR"), je_dominsu=je_dominsu)
                sprava = "Výber bol úspešný."
            elif akcia == "urok":
                u.zapocitaj_urok()
                sprava = "Úrok bol započítaný."
        except Exception as e:
            chyba = str(e)

        u = Ucet.nacitaj_podla_cisla(cislo_uctu)

    return render_template(
        "detail_uctu.html",
        u=u,
        rola=rola,
        chyba=chyba,
        sprava=sprava
    )

@app.route("/verejny_vklad", methods=["GET", "POST"])
def verejny_vklad():
    chyba = None
    sprava = None

    if request.method == "POST":
        try:
            cislo_uctu = int(request.form.get("cislo_uctu", "0"))
            suma = float(request.form.get("suma", "0"))

            u = Ucet.nacitaj_podla_cisla(cislo_uctu)
            if u is None:
                chyba = "Účet s týmto číslom neexistuje."
            else:
                u.vklad(suma)
                sprava = f"Vklad bol úspešný. Nový zostatok: {u.zostatok}"
        except Exception as e:
            chyba = f"Chyba pri vklade: {e}"

    return render_template("verejny_vklad.html", chyba=chyba, sprava=sprava)

if __name__ == "__main__":
    app.run(debug=True)
