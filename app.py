from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('heslo')
        print(email, password)
        return f"Data boli prijate na spracovanie"
    return render_template("HlavnyWeb.html")


@app.route('/fnfn/')
def AhojSvet():  # put application's code here
    return 'Ahoj svet!!!'


if __name__ == '__main__':
    app.run()

