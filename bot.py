import os
import json
import requests

TOKEN = os.getenv("BOT_TOKEN")

BOT_USERNAME = "JoinLoCoBot"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"
OFFSET_FILE = "offset.txt"


def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


users = load_json(USERS_FILE, {})
messages = load_json(MESSAGES_FILE, [])

try:
    with open(OFFSET_FILE, "r") as f:
        offset = int(f.read().strip())
except:
    offset = 0


def send_message(chat_id, text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )


updates = requests.get(
    f"{BASE_URL}/getUpdates?offset={offset}"
).json()

for update in updates.get("result", []):

    offset = update["update_id"] + 1

    if "message" not in update:
        continue

    msg = update["message"]

    chat_id = str(msg["chat"]["id"])
    text = msg.get("text", "")

    if chat_id not in users:
        users[chat_id] = {
            "waiting_for": None
        }

    if text.startswith("/start"):

        parts = text.split()

        if len(parts) > 1:

            target = parts[1]

            if target != chat_id:

                users[chat_id]["waiting_for"] = target

                send_message(
                    chat_id,
                    "📩 Send your anonymous message now."
                )

            continue

        my_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"

        send_message(
            chat_id,
            f"""🎉 Welcome

Your anonymous link:

{my_link}

Share this link and receive anonymous messages."""
        )

        continue

    waiting = users[chat_id].get("waiting_for")

    if waiting:

        send_message(
            waiting,
            f"📩 New Anonymous Message:\n\n{text}"
        )

        send_message(
            chat_id,
            "✅ Anonymous message delivered."
        )

        users[chat_id]["waiting_for"] = None

save_json(USERS_FILE, users)
save_json(MESSAGES_FILE, messages)

with open(OFFSET_FILE, "w") as f:
    f.write(str(offset))
