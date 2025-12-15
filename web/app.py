from flask import Flask, render_template, request, redirect, url_for, session
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

if __name__ == "__main__":
    app.run(debug=True)
