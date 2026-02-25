"""
Fetch the complete NET Bible from labs.bible.org and save as net_bible.json.

Format matches the existing psalms.json:
  [{"bookname": "...", "chapter": "...", "verse": "...", "text": "..."}, ...]

Personal non-commercial use only.
Attribution: Scripture quoted by permission. Quotations designated (NET) are from the
NET Bible® copyright ©1996, 2019 by Biblical Studies Press, L.L.C.
"""

import json
import time
from pathlib import Path

import requests

# 66 canonical books with chapter counts
BOOKS = [
    # Old Testament
    ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
    ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
    ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
    ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
    ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31),
    ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66),
    ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
    ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3),
    ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
    # New Testament
    ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
    ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
    ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
    ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6),
    ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13),
    ("James", 5), ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5),
    ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22),
]

BASE_URL = "https://labs.bible.org/api/"
OUT_FILE = Path(__file__).parent / "net_bible.json"
DELAY = 2  # seconds between requests — polite rate limiting

total_chapters = sum(c for _, c in BOOKS)
all_verses: list[dict] = []
fetched = 0
errors: list[str] = []

print(f"Fetching {total_chapters} chapters from labs.bible.org ...")
print(f"Estimated time: ~{total_chapters * DELAY // 60} minutes\n")

for book, num_chapters in BOOKS:
    for chapter in range(1, num_chapters + 1):
        passage = f"{book} {chapter}"
        try:
            resp = requests.get(
                BASE_URL,
                params={"passage": passage, "type": "json", "formatting": "plain"},
                timeout=30,
            )
            resp.raise_for_status()
            verses = resp.json()
            if isinstance(verses, list) and verses:
                all_verses.extend(verses)
                fetched += 1
                print(f"[{fetched}/{total_chapters}] {passage}: {len(verses)} verses")
            else:
                msg = f"WARNING: unexpected response for {passage}: {verses}"
                print(msg)
                errors.append(msg)
        except Exception as e:
            msg = f"ERROR fetching {passage}: {e}"
            print(msg)
            errors.append(msg)
        time.sleep(DELAY)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_verses, f, ensure_ascii=False, indent=2)

print(f"\nDone. {len(all_verses)} total verses saved to {OUT_FILE}")
if errors:
    print(f"\n{len(errors)} error(s):")
    for e in errors:
        print(f"  {e}")
