from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Инициализация Flask-приложения
app = Flask(__name__)

# Конфигурация базы данных (SQLite)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Определение модели данных
class User(db.Model):
    # id = db.Column(db.Integer)
    username = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Integer)
    departament = db.Column(db.Integer)
    password_hash = db.Column(db.Integer)

    def __init__(self, username, email, first_name, last_name, hash: int, role: int = 2, departament: int = -1):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.departament = departament
        self.password_hash = hash

    def __repr__(self):
        return f'<User {self.username}>'

# Создание таблиц в базе данных
with app.app_context():
    db.create_all()

# Тестовый маршрут для проверки
@app.route('/')
def home():
    return "База данных успешно создана! Проверьте файл app.db"


with app.app_context():
    # Удаление всех существующих записей (опционально)
    # db.session.query(User).delete()

    # Создание новых пользователей
    user1 = User('alice', 'alice@example.com', 'Alice', 'Gaylord', 0)
    user2 = User('bob', 'bob@example.com', 'Alice', 'Gaylord', 0)

    # Добавление в сессию
    db.session.add(user1)
    db.session.add(user2)

    # Сохранение в БД
    db.session.commit()

    # Проверка данных
    users = User.query.all()
    print("Пользователи в базе:", users)

if __name__ == '__main__':
    app.run(debug=True)
