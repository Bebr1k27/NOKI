import json
from datetime import date, datetime
import os
# from yandex_disk import YaDisk
from YaDiskSimple import YaDiskSimple

YANDEX_DISK_TOKEN = "y0__xCxqPDJBBjblgMg88ih-xNY1ffexuc3lXpAirNbk33ksz-D3Q" # os.getenv("YANDEX_DISK_TOKEN"), к релизу заменить
print(YANDEX_DISK_TOKEN)
# disk = YaDisk(token=YANDEX_DISK_TOKEN)
disk = YaDiskSimple(YANDEX_DISK_TOKEN)
BASE_DISK_PATH = "/app_data"

if not disk.exists(BASE_DISK_PATH):
    disk.mkdir(BASE_DISK_PATH)

ACTIVITIES_PATH = f"{BASE_DISK_PATH}/activities"
SHOWN_ACTIVITIES_PATH = f"{BASE_DISK_PATH}/shown_activities.json"

def write_activity(name: str, user_id: int | str, user_data: dict):
    try:
        # f = open(f"activities/{name}.json", "r")
        # data = json.load(f)
        # f.close()
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)
        if not data["Registration is open"]:
            raise Exception("Registration is closed")
        if str(user_id) in data:
            raise Exception("User already registered")
        data[user_id] = {}
        data[user_id] = user_data
        data[user_id]["date"] = str(date.today())
        data["Number of participants"] += 1
        # f = open(f"activities/{name}.json", "w")
        # json.dump(data, f)
        # f.close()
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
    except Exception as e:
        print("Something went wrong")
        print(f"Err: {e}")

def close_activity(name: str):
    try:
        # f = open(f"activities/{name}.json", "r")
        # data = json.load(f)
        # f.close()
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)
        data["Registration is open"] = False
        # f = open(f"activities/{name}.json", "w")
        # json.dump(data, f)
        # f.close()
        disk.write_file(f"{ACTIVITIES_PATH}/{name}.json", json.dumps(data))
    except Exception as e:
        print("Something went wrong")
        print(f"Err: {e}")

def open_activity(name: str):
    try:
        # f = open(f"activities/{name}.json", "r")
        # data = json.load(f)
        # f.close()
        content = disk.read_file(f"{ACTIVITIES_PATH}/{name}.json")
        data = json.loads(content)
        data["Registration is open"] = True
        f = open(f"activities/{name}.json", "w")
        json.dump(data, f)
        f.close()
    except Exception as e:
        print("Something went wrong")
        print(f"Err: {e}")


def get_user_activities(user_id):
    activities = []
    activities_dir = os.path.abspath(__file__)
    activities_dir = activities_dir[:activities_dir.rfind("/")]
    activities_dir = os.path.join(activities_dir, 'activities')
    today = datetime.today().date()

    if not os.path.exists(activities_dir):
        return activities

    for filename in os.listdir(activities_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(activities_dir, filename)
            try:
                # with open(filepath, 'r', encoding='utf-8') as f:
                with disk.read_file(filepath) as content:
                    event_data = json.loads(content)
                    # event_data = json.load(f)

                    # Проверяем наличие пользователя в мероприятии
                    user_key = str(user_id)
                    if user_key in event_data:
                        # Определяем статус мероприятия
                        event_date = datetime.strptime(
                            event_data[user_key]['date'],
                            '%Y-%m-%d'
                        ).date()

                        status = event_data["status"]

                        activity = {
                            'name': os.path.splitext(filename)[0],
                            'date': event_data[user_key]['date'],
                            'rank': event_data[user_key]['rank'],
                            'status': status  # Добавляем статус
                        }
                        activities.append(activity)
            except Exception as e:
                # app.logger.error(f"Error reading {filename}: {str(e)}")
                print(f"---|  {e}  |--")
                pass

    return activities

def get_all_activities():
    activities = []
    activities_dir = os.path.abspath(__file__)
    activities_dir = activities_dir[:activities_dir.rfind("/")]
    activities_dir = os.path.join(activities_dir, 'activities')
    today = datetime.today().date()

    if not os.path.exists(activities_dir):
        return activities

    for filename in os.listdir(activities_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(activities_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    event_data = json.load(f)

                    # Проверяем наличие пользователя в мероприятии
                    event_date = datetime.strptime(
                        event_data['date'],
                        '%Y-%m-%d'
                    ).date()

                    status = event_data["status"]

                    activity = {
                        'name': os.path.splitext(filename)[0],
                        'date': event_data['date'],
                        'status': status
                    }
                    activities.append(activity)
            except Exception as e:
                # app.logger.error(f"Error reading {filename}: {str(e)}")
                pass

    return activities

def user_activity(uid: int | str, name: str):
    try:
        f = open(f"activities/{name}.json", "r")
        data = json.load(f)
        f.close()
        if not str(uid) in data:
            raise Exception("Нету данных о пользователе")
        usdata = data[str(uid)]
        activity = {
            'name': name,
            'date': data['date'],
            'status': data["status"]
        }
        return (usdata, activity)
    except FileNotFoundError as e:
        return ({"Error description": "Запрашиваемой активности не существует"}, 0)
    except Exception as e:
        return ({"Error description": str(e)}, 0)

def create_activity(name: str, args: dict):
    try:
        activities_dir = os.path.abspath(__file__)
        activities_dir = activities_dir[:activities_dir.rfind("/")]
        activities_dir = os.path.join(activities_dir, 'activities')
        if os.path.exists(f"{activities_dir}/{name}.json"):
            raise Exception("Активность уже существует")
        data = {
            "Registration is open": False,
            "Number of participants": 0,
            "status": "planned",
            "date": str(date.today()),
            "args": args
        }
        f = open(f"activities/{name}.json", "w")
        json.dump(data, f)
        f.close()
        return "Ok"
    except Exception as e:
        return "Err: " + str(e)

def get_register_data(name: str):
    try:
        f = open(f"activities/{name}.json", "r")
        data = json.load(f)
        f.close()
        if not data["Registration is open"]:
            return "e1"  # Registration is closed
        activity = {
            'name': name,
            'date': data['date'],
            'status': data["status"]
        }
        if "args" not in data:
            return "e2" # Activity has not have input fields
        return (data["args"], activity)
    except FileNotFoundError as e:
        return "e3"
    except Exception as e:
        return str(e)

def add_user_to_cativity(name: str, uid: int | str, user_data: dict):
    try:
        f = open(f"activities/{name}.json", "r")
        data = json.load(f)
        f.close()
        if not data["Registration is open"]:
            return "e1"  # Registration is closed
        if str(uid) in data:
            return "e2"  # User already registered
        data["Number of participants"] += 1
        data[str(uid)] = user_data
        data[str(uid)]["date"] = str(date.today())
        data[str(uid)]["rank"] = "participant"
        f = open(f"activities/{name}.json", "w")
        json.dump(data, f)
        f.close()
        return "Ok"
    except FileNotFoundError as e:
        return "e3"
    except Exception as e:
        return str(e)

def show_activity(activity_data: dict):
    try:
        activity_data = activity_data["event_data"]
        f = open("shown_activities.json", "r", encoding="utf-8")
        data = json.load(f)
        f.close()
        data[activity_data["title"]] = activity_data
        f = open("shown_activities.json", "w", encoding="utf-8")
        json.dump(data, f)
        f.close()
    except Exception as e:
        return f"Err: {e}"

def parse_shown_activities():
    try:
        f = open("shown_activities.json", 'r', encoding="utf-8")
        data = json.load(f)
        f.close()
        items = []
        for i in data:
            items.append(data[i])
        return items
    except Exception as e:
        return f"Err: {e}"

if __name__ == "__main__":
    # write_activity("test_activity", 1, {
    #     "work name": "Влияние --- на ---- в городской среде",
    #     "rank": "participant"
    # })
    # open_activity("test_activity")
    # print(get_user_activities(1))
    # print(os.listdir("/activities"))
    # path = os.path.abspath(__file__)
    # path = path[:path.rfind("/") + 1]
    # print(path)
    # print(create_activity("a", {"ФИО": "user.first_name + user.last_name", "Возраст": "user.age", "Отделение": "user.departament", "Соцсеть": "user.link", "Почта": "user.email", "Согласие": False}))
    # print(get_user_activities(1))
    pass
