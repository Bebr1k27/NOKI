from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ'  # Обязательно замените на случайную строку!

# Конфигурация базы данных
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'  # Явное указание имени таблицы

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Создаем таблицы
with app.app_context():
    db.create_all()


# Главная страница
@app.route('/')
def home():
    usname = session.get('user_fullname', 'Войти')
    return render_template('index.html', usname=usname)  # Замените на ваш шаблон

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
        session['user_fullname'] = user.full_name
        flash('Вы успешно вошли в систему!', 'success')
        return redirect(url_for('profile'))  # Перенаправляем в профиль
    else:
        flash('Неверный email или пароль', 'error')
        return redirect(url_for('login_page'))


# Обработчик регистрации
@app.route('/register', methods=['POST'])
def register():
    full_name = request.form.get('fullName')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')
    birthdate_str = request.form.get('birthdate')

    # Проверка совпадения паролей
    if password != confirm_password:
        flash('Пароли не совпадают', 'error')
        return redirect(url_for('login_page'))

    # Проверка уникальности email
    if User.query.filter_by(email=email).first():
        flash('Пользователь с таким email уже существует', 'error')
        return redirect(url_for('login_page'))

    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Некорректная дата рождения', 'error')
        return redirect(url_for('login_page'))

    # Создание нового пользователя
    new_user = User(
        full_name=full_name,
        email=email,
        birthdate=birthdate
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


# Выход из системы
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_fullname', None)
    flash('Вы успешно вышли из системы', 'success')
    return "Loged out"
    # return redirect(url_for('home'))


# Страница профиля (пример)
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Для доступа к профилю необходимо войти в систему', 'warning')
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route("/profile_style.css")
def profile_style():
    return send_file("profile_style.css")

@app.route("/default-avatar.png")
def def_avatar():
    return send_file("images/avatar.png")

if __name__ == '__main__':
    app.run(debug=True)
