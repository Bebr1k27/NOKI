from flask import Flask, render_template, send_file, session, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cb02820a3e94d72c9f950ee10ef7e3f7a35b3f5b'

def section(nm):
    name = "Личный кабинет"
    if "login" in session:
        name = session["login"]
    return render_template(f"{nm}.html", usname=name)

@app.route("/")
def main():
    name = "Личный кабинет"
    if "login" in session:
        name = session["login"]
    return render_template("main_page.html", usname=name)

@app.route("/style.css")
def style():
    return send_file("style.css")

@app.route("/login_style.css")
def login_style():
    return send_file("login_style.css")

@app.route("/pe")
def pe():
    return send_file("PragmaticaExtended-Black.ttf")


@app.route("/logo.png")
def logo_png():
    return send_file("images/logo.png")

@app.route('/login/', methods=['post', 'get'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')  # запрос к данным формы
        password = request.form.get('password')

        if username == 'root' and password == 'pass':
            message = "Correct username and password"
        else:
            message = "Wrong username or password"

    return render_template('login.html', message=message)

@app.route("/login-handler", methods=["POST", "GET"])
def login_handler():
    if request.method == "POST":
        print(request.form)
    return "Ok"

@app.route("/history", methods=["GET"])
def history():
    return section("history")

@app.route("/img1")
def img1():
    return send_file("images/img1.png")

@app.route("/departments")
def departments():
    return section("departments")

@app.route("/activities")
def activities():
    return section("activities")

@app.route("/img2")
def img2():
    return send_file("images/img2.png")

@app.route("/img3")
def img3():
    return send_file("images/img3.png")

@app.route("/mobile")
def mobile_test():
    return section("mobile_test")

@app.route("/script")
def script():
    return send_file("script.js")

if __name__ == "__main__":
    app.run("0.0.0.0")
