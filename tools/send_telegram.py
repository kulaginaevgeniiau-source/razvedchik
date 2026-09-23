"""Отправляет текст (HTML-разметка Telegram) из файла всем получателям.
Ключ и список чатов — в переменных окружения TELEGRAM_TOKEN и TELEGRAM_CHAT_ID
(несколько чатов через запятую). Сбой у одного получателя не мешает остальным.
Запуск: TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=... python3 tools/send_telegram.py message.txt"""
import json, os, sys, urllib.request, urllib.error

text = open(sys.argv[1], encoding="utf-8").read().strip()
token = os.environ["TELEGRAM_TOKEN"]
chats = [c.strip() for c in os.environ["TELEGRAM_CHAT_ID"].split(",") if c.strip()]
sent, failed = 0, []
for chat in chats:
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat, "text": text, "parse_mode": "HTML",
                         "disable_web_page_preview": True}).encode(),
        headers={"Content-Type": "application/json"})
    try:
        if json.load(urllib.request.urlopen(req)).get("ok"):
            sent += 1
        else:
            failed.append(chat)
    except Exception as e:
        failed.append(f"{chat} ({e})")
print(f"отправлено: {sent} из {len(chats)}")
if failed:
    print("не дошло:", ", ".join(failed))
    sys.exit(1)
