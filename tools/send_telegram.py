"""Отправляет текст (HTML-разметка Telegram) из файла.
Ключ и чат берутся из переменных окружения TELEGRAM_TOKEN и TELEGRAM_CHAT_ID.
Запуск: TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=... python3 tools/send_telegram.py message.txt"""
import json, os, sys, urllib.request
text = open(sys.argv[1], encoding="utf-8").read().strip()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage",
    data=json.dumps({"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text,
                     "parse_mode": "HTML", "disable_web_page_preview": True}).encode(),
    headers={"Content-Type": "application/json"})
resp = json.load(urllib.request.urlopen(req))
print("отправлено" if resp.get("ok") else resp)
