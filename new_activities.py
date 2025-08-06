import json
from datetime import date, datetime
import os
from YaDiskSimple import YaDiskSimple

YANDEX_DISK_TOKEN = "y0__xCxqPDJBBjblgMg88ih-xNY1ffexuc3lXpAirNbk33ksz-D3Q"  # Замените на получение из переменных окружения перед релизом
disk = YaDiskSimple(YANDEX_DISK_TOKEN)
BASE_DISK_PATH = "/app_data"

# Создаем базовые директории при необходимости
if not disk.exists(BASE_DISK_PATH):
    disk.mkdir(BASE_DISK_PATH)

ACTIVITIES_PATH = f"{BASE_DISK_PATH}/activities"
SHOWN_ACTIVITIES_PATH = f"{BASE_DISK_PATH}/shown_activities.json"

# Создаем директорию для мероприятий
if not disk.exists(ACTIVITIES_PATH):
    disk.mkdir(ACTIVITIES_PATH)


def write_activity(name: str, user_id: int | str, user_data: dict):
    try:
        # Чтение файла с Яндекс.Диска
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)

        # Проверка возможности регистрации
        if not data["Registration is open"]:
            raise Exception("Registration is closed")
        if str(user_id) in data:
            raise Exception("User already registered")

        # Обновление данных
        data[user_id] = user_data
        data[user_id]["date"] = str(date.today())
        data["Number of participants"] += 1

        # Сохранение обратно на Яндекс.Диск
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
    except Exception as e:
        print(f"Error in write_activity: {e}")


def close_activity(name: str):
    try:
        # Чтение файла с Яндекс.Диска
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)

        # Закрытие регистрации
        data["Registration is open"] = False

        # Сохранение обратно на Яндекс.Диск
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
    except Exception as e:
        print(f"Error in close_activity: {e}")


def open_activity(name: str):
    try:
        # Чтение файла с Яндекс.Диска
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)

        # Открытие регистрации
        data["Registration is open"] = True

        # Сохранение обратно на Яндекс.Диск
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
    except Exception as e:
        print(f"Error in open_activity: {e}")


def get_user_activities(user_id):
    activities = []
    today = datetime.today().date()

    try:
        # Получаем список файлов мероприятий
        filenames = disk.listdir(ACTIVITIES_PATH)

        for filename in filenames:
            if filename.endswith('.json'):
                try:
                    # Чтение файла мероприятия
                    content = disk.read_file(f"{ACTIVITIES_PATH}/{filename}")
                    event_data = json.loads(content)

                    # Проверка участия пользователя
                    user_key = str(user_id)
                    if user_key in event_data:
                        # Парсинг даты
                        event_date = datetime.strptime(
                            event_data[user_key]['date'],
                            '%Y-%m-%d'
                        ).date()

                        # Формируем данные активности
                        activity = {
                            'name': filename.replace('.json', ''),
                            'date': event_data[user_key]['date'],
                            'rank': event_data[user_key].get('rank', 'participant'),
                            'status': event_data.get("status", "unknown")
                        }
                        activities.append(activity)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    except Exception as e:
        print(f"Error listing activities: {e}")

    return activities


def get_all_activities():
    activities = []
    try:
        # Получаем список файлов мероприятий
        filenames = disk.listdir(ACTIVITIES_PATH)

        for filename in filenames:
            if filename.endswith('.json'):
                try:
                    # Чтение файла мероприятия
                    content = disk.read_file(f"{ACTIVITIES_PATH}/{filename}")
                    event_data = json.loads(content)

                    # Формируем данные активности
                    activity = {
                        'name': filename.replace('.json', ''),
                        'date': event_data.get('date', 'unknown'),
                        'status': event_data.get("status", "unknown")
                    }
                    activities.append(activity)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    except Exception as e:
        print(f"Error listing activities: {e}")

    return activities


def user_activity(uid: int | str, name: str):
    try:
        # Чтение файла мероприятия
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)

        # Проверка наличия пользователя
        if str(uid) not in data:
            return ({"Error description": "User not registered for this activity"}, None)

        # Формирование данных
        usdata = data[str(uid)]
        activity = {
            'name': name,
            'date': data.get('date', 'unknown'),
            'status': data.get("status", "unknown")
        }
        return (usdata, activity)
    except Exception as e:
        return ({"Error description": str(e)}, None)


def create_activity(name: str, args: dict):
    try:
        # Проверка существования мероприятия
        if disk.exists(f"{ACTIVITIES_PATH}/{name}.json"):
            raise Exception("Activity already exists")

        # Создание структуры данных
        data = {
            "Registration is open": False,
            "Number of participants": 0,
            "status": "planned",
            "date": str(date.today()),
            "args": args
        }

        # Сохранение на Яндекс.Диск
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
        return "Ok"
    except Exception as e:
        return f"Err: {str(e)}"


def get_register_data(name: str):
    try:
        # Чтение файла мероприятия
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)

        # Проверка возможности регистрации
        if not data.get("Registration is open", False):
            return "e1"  # Registration is closed

        # Проверка наличия полей для регистрации
        if "args" not in data:
            return "e2"  # Activity has no input fields

        # Формирование данных активности
        activity = {
            'name': name,
            'date': data.get('date', 'unknown'),
            'status': data.get("status", "unknown")
        }
        return (data["args"], activity)
    except Exception as e:
        return f"e3: {str(e)}"  # Activity not found or other error


def add_user_to_activity(name: str, uid: int | str, user_data: dict):
    try:
        # Чтение файла мероприятия
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)

        # Проверка возможности регистрации
        if not data.get("Registration is open", False):
            return "e1"  # Registration is closed
        if str(uid) in data:
            return "e2"  # User already registered

        # Обновление данных
        data["Number of participants"] = data.get("Number of participants", 0) + 1
        data[str(uid)] = user_data
        data[str(uid)]["date"] = str(date.today())
        data[str(uid)]["rank"] = "participant"

        # Сохранение обратно на Яндекс.Диск
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
        return "Ok"
    except Exception as e:
        return f"e3: {str(e)}"  # Activity not found or other error


def show_activity(activity_data: dict):
    try:
        activity_data = activity_data["event_data"]

        # Чтение существующих данных
        if disk.exists(SHOWN_ACTIVITIES_PATH):
            content = disk.read_file(SHOWN_ACTIVITIES_PATH)
            data = json.loads(content)
        else:
            data = {}

        # Обновление данных
        data[activity_data["title"]] = activity_data

        # Сохранение обратно на Яндекс.Диск
        disk.write_file(SHOWN_ACTIVITIES_PATH, json.dumps(data))
        return "Ok"
    except Exception as e:
        return f"Err: {e}"


def parse_shown_activities():
    try:
        # Проверка существования файла
        if not disk.exists(SHOWN_ACTIVITIES_PATH):
            return []

        # Чтение данных
        content = disk.read_file(SHOWN_ACTIVITIES_PATH)
        data = json.loads(content)

        # Формирование списка
        items = []
        for key in data:
            items.append(data[key])
        return items
    except Exception as e:
        print(f"Error parsing shown activities: {e}")
        return []


if __name__ == "__main__":
    path = "/app_data/activities"

    if not disk.exists(path):
        print(f"Path {path} does not exist")
    elif not disk.is_dir(path):
        print(f"Path {path} is not a directory")
        # Если это файл, можно удалить его и создать директорию
        disk.delete(path)
        disk.mkdir(path)
    else:
        files = disk.listdir(path)
        print("Files:", files)
    pass