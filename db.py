import json, os
DB_FILE="chats.json"

def load_chats():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE,"r") as f: return json.load(f)

def save_chats(chats):
    with open(DB_FILE,"w") as f: json.dump(chats,f)
