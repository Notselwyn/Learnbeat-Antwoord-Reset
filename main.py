import requests
import time


def requestReset(s: requests.Session, user_id: int, task_id: int, activity_id: int, unixtime: int, text=None) -> None:
    body = {"task_id": task_id,
            "user_id": user_id,
            "activity_id": activity_id,
            "json_answer": text,
            "client_time_created": unixtime,
            "sync": True}

    s.post("https://inloggen.learnbeat.nl/responses/add.json", data=body)


learnbeatsession_cookie = input("Enter your LearnBeat session cookie: ")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"})
session.cookies.set("LearnbeatSession", learnbeatsession_cookie)

user_info = session.get("https://inloggen.learnbeat.nl/users/get.json").json()
if "User" not in user_info:
    print("Invalid LearnBeat session cookie.")
    exit()

user_id = user_info["User"]["id"]
timestamp_ms = int(time.time()) * 1000

for group in user_info["Groups"]:
    print("UID:", user_id, "GID:", group["id"])
    if "n" not in input(f"{group['name']} resetten? [Y/n]: ").lower():
        for chapter in group["Chapter"]:
            print(f"Onderdeel {chapter['name']}")
            for section in chapter["Section"]:
                for activity in section["Activity"]:
                    if not activity["name"].startswith("[DO NOT SHOW] ") and activity["name"] not in ["Begrippenlijst", "Trainen"]:
                        print(f"{chapter['name']}: {section['name']}: {activity['name']}")
                        r = session.get(f"https://inloggen.learnbeat.nl/activities/backbone_backend/{activity['id']}.json").json()
                        if r["status"] != "error":
                            for taskgroup in r["TaskGroup"]:
                                for task in taskgroup["Element"]:
                                    if 'is_public' not in task.keys() or task['is_public'] != 0:
                                        requestReset(session, user_id, task["id"], activity["id"], timestamp_ms)