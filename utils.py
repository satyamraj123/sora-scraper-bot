import requests
import constants

#function to send a message to user from bot
def send_message_to_user(TELEGRAM_API, chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text})
    return resp.json()

#function to classify the link into sora, youtube etc..
def classify_link(text):
    if "https://sora.chatgpt.com/" in text:
        return "sora"
    return None

def classify_command(text):
    if text[0]=="/":
        if text in constants.commands_and_descriptions.keys():
            return constants.commands_and_descriptions[text]
        else:
            return "Invalid Command 😬. Type `/help` to see all the commands."
    else:
        None
