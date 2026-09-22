"""Собирает кандидатов за последние N часов из RSS-лент и Google News.
Запуск: python3 tools/collect.py [часы=26] > /tmp/candidates.txt
Вывод: источник | время UTC | заголовок | ссылка"""
import re, sys, html, urllib.request, urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor

HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 26
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"}

FEEDS = {
    "Adweek": "https://www.adweek.com/feed/",
    "Digiday": "https://digiday.com/feed/",
    "Muse by Clios": "https://musebyclios.com/feed/",
    "Campaign US": "https://www.campaignlive.com/rss/news",
    "Marketing Week": "https://www.marketingweek.com/feed/",
    "Creative Review": "https://www.creativereview.co.uk/feed/",
    "Social Media Today": "https://www.socialmediatoday.com/feeds/news/",
    "Tubefilter": "https://www.tubefilter.com/feed/",
    "Search Engine Journal": "https://www.searchenginejournal.com/feed/",
    "Buffer": "https://buffer.com/resources/rss/",
    "Hootsuite": "https://blog.hootsuite.com/feed/",
    "Cossa": "https://www.cossa.ru/rss/",
    "RB.ru": "https://rb.ru/feeds/all/",
    "Texterra": "https://texterra.ru/blog/rss/",
}
QUERIES_EN = [
    "marketing campaign results", "campaign case study brand", "ad campaign viral",
    "TikTok brand campaign views", "Instagram Reels brand", "creator economy brand deal",
    "edtech marketing growth", "mental health app marketing", "wellness brand campaign",
    "YouTube creators new feature", "Instagram new feature", "AI marketing tool launch",
    "Effie award winner", "Cannes Lions case", "brand campaign sales increase",
]
QUERIES_RU = [
    "кейс маркетинг", "рекламная кампания результаты", "онлайн-школа запуск",
    "Telegram реклама", "маркетинг кейс рост продаж", "спецпроект бренда",
    "Казахстан маркетинг кейс",
]

def gnews(q, ru):
    hl, gl, ceid = ("ru", "RU", "RU:ru") if ru else ("en-US", "US", "US:en")
    return f"https://news.google.com/rss/search?q={urllib.parse.quote(q + ' when:1d')}&hl={hl}&gl={gl}&ceid={ceid}"

def fetch(item):
    name, url = item
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            return name, r.read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"# не открылся: {name} ({e})", file=sys.stderr)
        return name, ""

def tag(block, t):
    m = re.search(rf"<{t}[^>]*>(.*?)</{t}>", block, re.S)
    return html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", m.group(1))).strip() if m else ""

jobs = list(FEEDS.items()) + [(f"GN: {q}", gnews(q, False)) for q in QUERIES_EN] + [(f"GN: {q}", gnews(q, True)) for q in QUERIES_RU]
now = datetime.now(timezone.utc)
seen, rows = set(), []
with ThreadPoolExecutor(12) as ex:
    for name, body in ex.map(fetch, jobs):
        for it in re.findall(r"<item[\s>].*?</item>", body, re.S):
            title, link = tag(it, "title"), tag(it, "link")
            try:
                dt = parsedate_to_datetime(tag(it, "pubDate"))
            except Exception:
                continue
            key = title.lower()[:80]
            if now - dt > timedelta(hours=HOURS) or key in seen:
                continue
            seen.add(key)
            rows.append((dt, name, title, link))
rows.sort(reverse=True)
print(f"# всего кандидатов: {len(rows)} за {HOURS} ч, сейчас {now:%Y-%m-%d %H:%M} UTC")
for dt, name, title, link in rows:
    print(f"{name} | {dt:%d.%m %H:%M} | {title} | {link}")
