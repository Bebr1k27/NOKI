from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from activities import *

app = Flask(__name__)
app.secret_key = 'cb02820a3e94d72c9f950ee10ef7e3f7a35b3f5b'

# Конфигурация базы данных
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def section(nm):
    name = session.get('user_fullname', 'Войти')
    return render_template(f"{nm}.html", usname=name)

# @app.route("/")
# def main():
#     name = "Личный кабинет"
#     if "login" in session:
#         name = session["login"]
#     return render_template("main_page.html", usname=name)
@app.route("/")
def main_page():
    return section("main_page")

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

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    social_media = db.Column(db.String(100))  # Ссылка на соцсеть
    avatar_url = db.Column(db.String(200))  # Ссылка на аватар на внешнем сервере
    department = db.Column(db.String(100))
    role = db.Column(db.SmallInteger, default=0)  # 0=user, 1=moderator, 2=admin
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    birthdate = db.Column(db.Date)  # Новое поле: дата рождения

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_avatar_url(self):
        return self.avatar_url or url_for('def_avatar')

    def get_age(self):
        if not self.birthdate:
            return None
        today = datetime.today().date()
        born = self.birthdate
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# Создаем таблицы
with app.app_context():
    db.create_all()

@app.route("/login_style.css")
def login_style():
    return send_file("login_style.css")


@app.route("/style.css")
def style():
    return send_file("style.css")


@app.route("/script")
def script():
    return send_file("script.js")


@app.route("/pe")
def pe():
    return send_file("PragmaticaExtended-Black.ttf")

@app.route("/logo.png")
def logo_png():
    return send_file("images/logo.png")

# Страница входа
@app.route('/login')
def login_page():
    usname = session.get('user_fullname', 'Войти')
    return render_template('login.html', usname=usname)

# Обработчик входа
@app.route('/login-handler', methods=['POST'])
def login_handler():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Успешный вход
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_fullname'] = user.get_full_name()
        session['user_role'] = user.role
        flash('Вы успешно вошли в систему!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Неверный email или пароль', 'error')
        return redirect(url_for('login_page'))

# Обработчик регистрации
@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')
    department = request.form.get('department')
    birthdate_str = request.form.get('birthdate')
    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Некорректная дата рождения', 'error')
        return redirect(url_for('login_page'))

    if password != confirm_password:
        flash('Пароли не совпадают', 'error')
        return redirect(url_for('login_page'))

    if User.query.filter_by(email=email).first():
        flash('Пользователь с таким email уже существует', 'error')
        return redirect(url_for('login_page'))

    if User.query.filter_by(username=username).first():
        flash('Пользователь с таким логином уже существует', 'error')
        return redirect(url_for('login_page'))

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        department=department,
        role=0,  # По умолчанию обычный пользователь
        birthdate = birthdate
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти', 'success')
        return redirect(url_for('login_page'))
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при регистрации: {str(e)}', 'error')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_fullname', None)
    session.pop('user_role', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect("/")

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Для доступа к профилю необходимо войти в систему', 'warning')
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    user_activities = get_user_activities(user.id)

    return render_template(
        'profile.html',
        user=user,
        usname=user.get_full_name(),
        activities=user_activities
    )

@app.route("/profile_style.css")
def profile_style():
    return send_file("profile_style.css")

@app.route("/default-avatar.png")
def def_avatar():
    return send_file("images/avatar.png")

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    user.first_name = request.form.get('firstName', user.first_name)
    user.last_name = request.form.get('lastName', user.last_name)
    user.social_media = request.form.get('socialMedia', user.social_media)
    user.department = request.form.get('department', user.department)
    user.avatar_url = request.form.get('avatarUrl', user.avatar_url)

    new_username = request.form.get('username')
    if new_username and new_username != user.username:
        if User.query.filter(User.username == new_username, User.id != user.id).first():
            flash('Пользователь с таким логином уже существует', 'error')
            return redirect(url_for('profile'))
        user.username = new_username

    try:
        db.session.commit()
        session['user_fullname'] = user.get_full_name()
        flash('Профиль успешно обновлен!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при обновлении профиля: {str(e)}', 'error')

    return redirect(url_for('profile'))

@app.route("/admin_panel")
def admin_panel():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    if user.role < 1:
        flash("Недостаточно прав", "error")
        return redirect("/login")

    return render_template("admin_panel.html", user=user, activities=get_all_activities())

@app.route("/mmm")   # FOR DEBUG ONLY!!! Delete that later
def mmm():
    user = User.query.get(session['user_id'])
    print(user.role, user.id)
    user.role = 2
    print(user.role, user.id)
    db.session.commit()
    return redirect("/")

@app.route("/favicon.ico")
def ico():
    return send_file("images/logo.ico")

if __name__ == '__main__':
    app.run(debug=True)
