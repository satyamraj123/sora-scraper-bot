# app.py
import os
import requests
from flask import Flask, request, jsonify

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set on Render
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is required")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text})
    return resp.json()

def handle_update(update):
    """
    Put your scraper/downloader logic here.
    Example:
      - parse update for chat_id and user command
      - run your downloader (make sure it's allowed)
      - upload/send result (or reply with a link)
    For demo we just echo the message text.
    """
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text","(no text)")
        # demo reply
        send_message(chat_id, f"Got: {text}")
    return

@app.route("/healthz")
def health():
    return "ok"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    return jsonify({"ok": True})
    update = request.get_json(force=True)
    # process update in background ideally — keep webhook fast
    try:
        handle_update(update)
    except Exception as e:
        # log in real app
        print("handler error:", e)
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

