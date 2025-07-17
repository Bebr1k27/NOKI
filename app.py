from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from regions import regions
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

def text(text):
    name = session.get('user_fullname', 'Войти')
    return render_template("text_plate.html", usname=name, text=text)

# @app.route("/")
# def main():
#     name = "Личный кабинет"
#     if "login" in session:
#         name = session["login"]
#     return render_template("main_page.html", usname=name)
@app.route("/")
def main_page():
    return section("main_page")

@app.route("/regions")
def get_regions():
    return jsonify(regions)

# @app.route('/login/', methods=['post', 'get'])
# def login():
#     message = ''
#     if request.method == 'POST':
#         username = request.form.get('username')  # запрос к данным формы
#         password = request.form.get('password')
#
#         if username == 'root' and password == 'pass':
#             message = "Correct username and password"
#         else:
#             message = "Wrong username or password"
#
#     return render_template('login.html', message=message, regions=regions)

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
    department = db.Column(db.Integer)
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
    return render_template('login.html', usname=usname, regions=regions)

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
    print(new_user.department)

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
        session['user_id'] = None
        return redirect(url_for('login_page'))

    user_activities = get_user_activities(user.id)
    print(user.department)

    return render_template(
        'profile.html',
        user=user,
        usname=user.get_full_name(),
        activities=user_activities,
        regions=regions
    )

@app.route("/profile/<uid>")
def another_profile(uid):
    return "!"
    if 'user_id' not in session:
        flash('Для доступа к профилю необходимо войти в систему', 'warning')
        return redirect(url_for('login_page'))

    urole = User.query.get(session["user_role"])
    if urole < 1:
        return text("Недостаточно прав")

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    # auser =
    user_activities = get_user_activities(uid)

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

@app.route("/admin_panel/create_form", methods=["GET", "POST"])
def admin_create_form():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    if user.role < 1:
        flash("Недостаточно прав", "error")
        return redirect("/login")

    if request.method == "GET":
        return section("create_form_test")
    else:
        try:
            data = request.json
            name = data['name']
            args = data['args']

            if os.path.exists(f"activities/{name}.json"):
                return jsonify({
                    'status': 'error',
                    'message': 'Мероприятие с таким названием уже существует'
                }), 400

            activity_data = {
                "Registration is open": True,
                "Number of participants": 0,
                "status": "planned",
                "date": str(date.today()),
                "args": args
            }

            with open(f"activities/{name}.json", 'w') as f:
                json.dump(activity_data, f, ensure_ascii=False, indent=4)

            return jsonify({
                'status': 'success',
                'message': 'Мероприятие успешно создано'
            })

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

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

@app.route("/activity/m/<name>")
def my_activity(name):
    if 'user_id' not in session:
        flash('Для доступа к профилю необходимо войти в систему', 'warning')
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    nm = session.get('user_fullname', 'Войти')
    data, activity = user_activity(user.id, name)

    return render_template("activity.html", usname=nm, text=data, activity=activity)

@app.route("/activity/r/<name>", methods=["GET", "POST"])
def reg_to_activity(name):
    if 'user_id' not in session:
        flash('Для доступа к профилю необходимо войти в систему', 'warning')
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login_page'))

    nm = session.get('user_fullname', 'Войти')
    ans = get_register_data(name)
    if ans == "e1":
        return text("Регистрация на данное мероприятие закрыта!")
    if ans == "e2":
        return text("Регистрация невозможна: не найдены данные формы регистрации")
    if ans == "e3":
        return text("Такого мероприятия не существует")
    data, activity = ans
    if request.method == "GET":
        return render_template("reg.html", usname=nm, text=data, activity=activity)
    else:
        ercode = add_user_to_cativity(name, str(session.get("user_id")), dict(request.form))
        return text({"Ok": "Регистрация прошла успешно!", "e1": "Регистрация на данное мероприятие закрыта!", "e2": "Данный пользователь уже зарегистрирован на это мероприятие", "e3": "Такого мероприятия не существует"}[ercode])

@app.route("/test")
def test():
    return render_template("official_ya_test.html")


@app.route("/event/manage/<event_name>")
def manage_event(event_name):
    if 'user_id' not in session:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])
    if user.role < 1:  # Только для модераторов и админов
        flash('Недостаточно прав', 'error')
        return redirect('/')

    # Загружаем данные мероприятия
    event_path = f"activities/{event_name}.json"
    if not os.path.exists(event_path):
        flash('Мероприятие не найдено', 'error')
        return redirect('/admin_panel')

    with open(event_path, 'r', encoding='utf-8') as f:
        event_data = json.load(f)

    # Фильтруем участников (исключаем служебные поля)
    participants = []
    for key, value in event_data.items():
        if key.isdigit():  # ID участника
            participants.append((key, value))

    return render_template(
        'request.html',
        usname=user.get_full_name(),
        event=event_data,
        event_name=event_name,
        participants=participants
    )


# Переключение статуса регистрации
@app.route("/event/toggle/<event_name>", methods=['POST'])
def toggle_registration(event_name):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    if user.role < 1:
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    event_path = f"activities/{event_name}.json"
    if not os.path.exists(event_path):
        return jsonify({'status': 'error', 'message': 'Event not found'}), 404

    try:
        with open(event_path, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data['Registration is open'] = not data['Registration is open']
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

        return redirect(url_for('manage_event', event_name=event_name))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Удаление участника
@app.route("/event/remove/<event_name>/<participant_id>", methods=['POST'])
def remove_participant(event_name, participant_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    if user.role < 1:
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    event_path = f"activities/{event_name}.json"
    if not os.path.exists(event_path):
        return jsonify({'status': 'error', 'message': 'Event not found'}), 404

    try:
        with open(event_path, 'r+', encoding='utf-8') as f:
            data = json.load(f)

            if participant_id not in data:
                return jsonify({'status': 'error', 'message': 'Participant not found'}), 404

            # Удаляем участника
            del data[participant_id]
            data['Number of participants'] = len([k for k in data.keys() if k.isdigit()])

            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

        return redirect(url_for('manage_event', event_name=event_name))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Добавление участника по ID
@app.route("/event/add/<event_name>", methods=['POST'])
def add_participant(event_name):
    return jsonify({'status': 'error', 'message': 'Функция не готова'}), 401
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    if user.role < 1:
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    user_id = request.form.get('user_id')
    if not user_id:
        flash('Введите ID пользователя', 'error')
        return redirect(url_for('manage_event', event_name=event_name))

    event_path = f"activities/{event_name}.json"
    if not os.path.exists(event_path):
        return jsonify({'status': 'error', 'message': 'Event not found'}), 404

    try:
        # Проверяем существование пользователя
        participant = User.query.get(user_id)
        if not participant:
            flash('Пользователь не найден', 'error')
            return redirect(url_for('manage_event', event_name=event_name))

        with open(event_path, 'r+', encoding='utf-8') as f:
            data = json.load(f)

            if user_id in data:
                flash('Пользователь уже зарегистрирован', 'error')
                return redirect(url_for('manage_event', event_name=event_name))

            # Создаем запись участника
            data[user_id] = {
                "ФИО участника": participant.get_full_name(),
                "date": str(date.today()),
                "rank": "participant",
                "E-mail участника": participant.email,
                "Регион участника": participant.department
            }

            data['Number of participants'] = len([k for k in data.keys() if k.isdigit()])

            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

        flash('Участник успешно добавлен', 'success')
        return redirect(url_for('manage_event', event_name=event_name))
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('manage_event', event_name=event_name))

# Маршрут для изменения формы регистрации
@app.route("/event/edit-form/<event_name>")
def edit_registration_form(event_name):
    # Реализация страницы редактирования формы
    # (может быть аналогична странице создания формы)
    return "Страница редактирования формы"


def change_user_role(uid, new_role):
    if new_role not in (0, 1, 2):
        return False
    try:
        # Поиск пользователя
        user = User.query.get(uid)

        if not user:
            return False  # Пользователь не найден

        # Обновление роли
        user.role = new_role
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при изменении роли: {str(e)}")
        return False


@app.route('/admin/change_role', methods=['POST'])
def admin_change_role():
    if 'user_id' not in session:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('login_page'))

    # Проверка прав текущего пользователя (только админы)
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role < 2:
        flash("Недостаточно прав", "error")
        return redirect(url_for('admin_panel'))

    try:
        user_id = int(request.form.get('user_id'))
        new_role = int(request.form.get('new_role'))
    except (ValueError, TypeError):
        flash('Некорректные данные', 'error')
        return redirect(url_for('admin_panel'))

    # Проверка допустимости роли
    if new_role not in (0, 1, 2):
        flash('Недопустимая роль', 'error')
        return redirect(url_for('admin_panel'))

    # Изменение роли
    user = User.query.get(user_id)
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('admin_panel'))

    user.role = new_role
    try:
        db.session.commit()
        flash(f'Роль пользователя {user.get_full_name()} успешно изменена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при изменении роли: {str(e)}', 'error')

    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
