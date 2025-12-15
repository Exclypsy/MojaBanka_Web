from flask import Flask, render_template, request, redirect, url_for, session
from modely.klient import Klient

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

if __name__ == "__main__":
    app.run(debug=True)
