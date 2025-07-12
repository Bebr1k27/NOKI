import json
from datetime import date, datetime
import os

def write_activity(name: str, user_id: int | str, user_data: dict):
    try:
        f = open(f"activities/{name}.json", "r")
        data = json.load(f)
        f.close()
        if not data["Registration is open"]:
            raise Exception("Registration is closed")
        if str(user_id) in data:
            raise Exception("User already registered")
        data[user_id] = {}
        data[user_id] = user_data
        data[user_id]["date"] = str(date.today())
        data["Number of participants"] += 1
        f = open(f"activities/{name}.json", "w")
        json.dump(data, f)
        f.close()
    except Exception as e:
        print("Something went wrong")
        print(f"Err: {e}")

def close_activity(name: str):
    try:
        f = open(f"activities/{name}.json", "r")
        data = json.load(f)
        f.close()
        data["Registration is open"] = False
        f = open(f"activities/{name}.json", "w")
        json.dump(data, f)
        f.close()
    except Exception as e:
        print("Something went wrong")
        print(f"Err: {e}")

def open_activity(name: str):
    try:
        f = open(f"activities/{name}.json", "r")
        data = json.load(f)
        f.close()
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
                with open(filepath, 'r', encoding='utf-8') as f:
                    event_data = json.load(f)

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
                            'work_name': event_data[user_key]['work name'],
                            'status': status  # Добавляем статус
                        }
                        activities.append(activity)
            except Exception as e:
                # app.logger.error(f"Error reading {filename}: {str(e)}")
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
    pass
