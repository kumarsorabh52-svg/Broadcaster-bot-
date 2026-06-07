import json
import os

DB_FILE = "data.json"


def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "chats": [],
            "announcement": "",
            "interval": 0,
            "running": False
        }

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)


def load_chats():
    data = load_data()
    return data.get("chats", [])


def save_chats(chats):
    data = load_data()
    data["chats"] = chats
    save_data(data)


def set_announcement(message):
    data = load_data()
    data["announcement"] = message
    save_data(data)


def get_announcement():
    data = load_data()
    return data.get("announcement", "")


def set_interval(minutes):
    data = load_data()
    data["interval"] = minutes
    save_data(data)


def get_interval():
    data = load_data()
    return data.get("interval", 0)


def set_running(status):
    data = load_data()
    data["running"] = status
    save_data(data)


def is_running():
    data = load_data()
    return data.get("running", False)
