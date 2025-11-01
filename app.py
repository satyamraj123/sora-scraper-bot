import os
from flask import Flask, request, jsonify
from handle_sora_videos import handle_sora_video
from utils import send_message_to_user, classify_link, classify_command
import asyncio
import traceback
import threading

#fetch bot_token set on Render and telegram API for the bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
app = Flask(__name__)

#if bot_token is not present, then dont deploy
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is required")

#handle user messages
async def handle_user_chat(update):
    #extract message and chatID
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text","(no text)")

        #classify command
        command_result = classify_command(text)

        #if its not a command then classify the text further
        if not command_result:
            #classify if its sora link or not
            service=classify_link(text)
            #if its not sora link then inform user
            if not service:
                send_message_to_user(TELEGRAM_API, chat_id, f"Invalid sora video link ❌\n Please send only sora video link which should look like this: https://sora.chatgpt.com/p/abcdxyz")
            else:
                #scrape the website and get the video link without watermark
                send_message_to_user(TELEGRAM_API, chat_id, "Removing watermark from your video 🔄 \nPlease wait 10 seconds ⏱️")
                downloadable_link= await handle_sora_video(text)
                #check if we got any error while scraping
                if downloadable_link=="ERROR":
                    send_message_to_user(TELEGRAM_API, chat_id, "I'm really sorry 😞. Either the link is not correct or my services are not working. Please contact Admin.")
                else:
                    #send user the link
                    send_message_to_user(TELEGRAM_API, chat_id, "Watermark Removed ✔️ \nOpen this link in any browser 👇")
                    send_message_to_user(TELEGRAM_API, chat_id, downloadable_link)
                    send_message_to_user(TELEGRAM_API, chat_id, "Share this bot with your friends and family if you liked it ✨ \nHave a Good Day 🌞")
        else:
            send_message_to_user(TELEGRAM_API, chat_id, command_result)
    else:
        raise Exception("message was not present in user response.")
    return ""

#will be triggered when you send message to bot
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    
    threading.Thread(target=asyncio.run, args=(handle_user_chat(update),)).start()

    return jsonify({"ok": True})

#its for testing
@app.route("/healthz")
def health():
    return "This render web service is working fine."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

