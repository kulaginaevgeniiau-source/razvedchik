"""Пересобирает index.html: копия самого свежего выпуска из issues/ + архив всех выпусков.
Архив также вписывается в каждый выпуск. Запуск из корня репозитория: python3 tools/build_index.py"""
import re, glob, os
MONTHS = "января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split()
issues = sorted(glob.glob("issues/*.html"), reverse=True)
def label(p):
    y, m, d = os.path.basename(p)[:-5].split("-")
    return f"{int(d)} {MONTHS[int(m)-1]}"
def archive(current, prefix):
    items = ""
    for p in issues:
        href = prefix + os.path.basename(p) if prefix else os.path.basename(p)
        cur = ' aria-current="page"' if p == current else ""
        items += f'<li><a href="{href}"{cur}>{label(p)}</a></li>'
    return f'<nav aria-label="Архив выпусков"><ul class="archive">{items}</ul></nav>'
BLOCK = re.compile(r"<!--ARCHIVE-->.*?<!--/ARCHIVE-->", re.S)
for p in issues:
    s = open(p, encoding="utf-8").read()
    s = BLOCK.sub(f"<!--ARCHIVE-->{archive(p, '')}<!--/ARCHIVE-->", s)
    open(p, "w", encoding="utf-8").write(s)
latest = open(issues[0], encoding="utf-8").read()
latest = latest.replace('href="../style.css"', 'href="style.css"')
latest = BLOCK.sub(f"<!--ARCHIVE-->{archive(issues[0], 'issues/')}<!--/ARCHIVE-->", latest)
open("index.html", "w", encoding="utf-8").write(latest)
print(f"index.html ← {issues[0]}, в архиве {len(issues)}")
