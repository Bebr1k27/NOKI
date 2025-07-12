from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import pymysql

# Параметры подключения
USER = 'sql7786215'
PASSWORD = 'IpTbSb9SNX'
HOST = 'sql7.freesqldatabase.com'  # Если локально - 'localhost' или '127.0.0.1'
PORT = 3306
DATABASE = 'sql7786215'

# Используем PyMySQL
connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"

try:
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,  # Проверка соединения перед использованием
        connect_args={
            'connect_timeout': 10,
            'read_timeout': 20
        }
    )

    # Тестовый запрос
    with engine.connect() as conn:
        print("Успешное подключение к MySQL!")

        # Простой запрос для проверки
        result = conn.execute(text("SELECT 1+1 AS test"))
        print("Результат теста:", result.scalar())

        # Получение версии MySQL
        result = conn.execute(text("SELECT VERSION()"))
        print("Версия MySQL:", result.scalar())

        print("Создаём пользователя")
        result = conn.execute(text("INSERT INTO user_data (login, FIO, email, link, departament, role) VALUES ('zxc_Volodya', 'Владимир Петрович *', 'olegMongol@kmspokuni.ru', 't.me/динаху.олег', 4, 2);"))
        print(f"Result: {result}")

except OperationalError as oe:
    print(f"Ошибка подключения к базе данных: {oe}")
    print("Проверьте:")
    print(f"- Доступность сервера {HOST}:{PORT}")
    print("- Правильность имени пользователя и пароля")
    print("- Настройки брандмауэра на сервере")
    print("- Параметры bind-address в конфиге MySQL")

except SQLAlchemyError as se:
    print(f"Общая ошибка SQLAlchemy: {se}")

except pymysql.Error as pe:
    print(f"Ошибка PyMySQL: {pe}")

finally:
    if 'engine' in locals():
        engine.dispose()
    print("Завершение работы")
