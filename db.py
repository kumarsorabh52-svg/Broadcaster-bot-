import json
import os

DB_FILE = "data.json"


def load_data():

    if not os.path.exists(DB_FILE):

        return {
            "users": {},
            "announcement": "",
            "interval": 0,
            "running": False
        }

    with open(DB_FILE, "r", encoding="utf-8") as f:

        try:
            return json.load(f)

        except:
            return {
                "users": {},
                "announcement": "",
                "interval": 0,
                "running": False
            }


def save_data(data):

    with open(DB_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# =========================
# USER GROUP MANAGEMENT
# =========================

def get_user_chats(user_id):

    data = load_data()

    users = data.get("users", {})

    return users.get(str(user_id), [])


def save_user_chats(user_id, chats):

    data = load_data()

    if "users" not in data:
        data["users"] = {}

    data["users"][str(user_id)] = chats

    save_data(data)


def add_group(user_id, group_id):

    chats = get_user_chats(user_id)

    if group_id not in chats:
        chats.append(group_id)

    save_user_chats(user_id, chats)


def remove_group(user_id, group_id):

    chats = get_user_chats(user_id)

    if group_id in chats:
        chats.remove(group_id)

    save_user_chats(user_id, chats)


# =========================
# ANNOUNCEMENT SETTINGS
# =========================

def set_announcement(message):

    data = load_data()

    data["announcement"] = message

    save_data(data)


def get_announcement():

    data = load_data()

    return data.get(
        "announcement",
        ""
    )


def set_interval(minutes):

    data = load_data()

    data["interval"] = minutes

    save_data(data)


def get_interval():

    data = load_data()

    return data.get(
        "interval",
        0
    )


def set_running(status):

    data = load_data()

    data["running"] = status

    save_data(data)


def is_running():

    data = load_data()

    return data.get(
        "running",
        False
    )
