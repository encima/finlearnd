import reflex as rx
import httpx
import json
import sqlite3
import logging
import argparse
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
DOWNLOAD_URL = (
    "https://kaikki.org/dictionary/Finnish/kaikki.org-dictionary-Finnish.jsonl"
)
DATA_DIR = Path(".web")
DB_FILE = DATA_DIR / "finnish_dictionary.db"
JSONL_FILE = DATA_DIR / "kaikki.org-dictionary-Finnish.jsonl"


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            pos TEXT NOT NULL,
            definition TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verb_conjugations (
            word_id INTEGER,
            person TEXT NOT NULL,
            form TEXT NOT NULL,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noun_declensions (
            word_id INTEGER,
            case_name TEXT NOT NULL,
            singular TEXT,
            plural TEXT,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_word ON words (word);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pos ON words (pos);")
    conn.commit()
    conn.close()


def download_dictionary():
    logging.info(f"Starting download from {DOWNLOAD_URL}")
    DATA_DIR.mkdir(exist_ok=True)
    try:
        with httpx.stream("GET", DOWNLOAD_URL, timeout=None) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0
            start_time = time.time()
            with open(JSONL_FILE, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 1:
                        progress = (
                            downloaded_size / total_size * 100 if total_size > 0 else 0
                        )
                        speed = downloaded_size / elapsed_time / (1024 * 1024)
                        print(
                            f"\rDownloading: {downloaded_size / 1024 / 1024:.2f}MB / {total_size / 1024 / 1024:.2f}MB ({progress:.1f}%) at {speed:.2f} MB/s",
                            end="",
                        )
            print("""
Download complete.""")
    except httpx.RequestError as e:
        logging.exception(f"Download failed: {e}")


def import_to_sqlite():
    if not JSONL_FILE.exists():
        logging.error(
            f"{JSONL_FILE} not found. Please download it first with 'python -m app.utils.dictionary_downloader download'"
        )
        return
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    total_lines = sum((1 for _ in open(JSONL_FILE, "r", encoding="utf-8")))
    logging.info(f"Starting import of {total_lines} entries into {DB_FILE}")
    with open(JSONL_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if (i + 1) % 1000 == 0:
                progress = (i + 1) / total_lines * 100
                print(
                    f"\rImporting: {i + 1} / {total_lines} ({progress:.1f}%) entries processed",
                    end="",
                )
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                logging.exception(f"Failed to decode JSON line: {line}")
                continue
            if entry.get("lang_code") != "fi" or entry.get("pos") not in [
                "verb",
                "noun",
            ]:
                continue
            word = entry.get("word")
            pos = entry.get("pos")
            definition = entry.get("senses", [{}])[0].get("glosses", ["-"])[0]
            cursor.execute(
                "INSERT INTO words (word, pos, definition) VALUES (?, ?, ?)",
                (word, pos, definition),
            )
            word_id = cursor.lastrowid
            forms = entry.get("forms", [])
            if pos == "verb":
                conjugations = _parse_verb_forms(forms)
                for person, form in conjugations.items():
                    cursor.execute(
                        "INSERT INTO verb_conjugations (word_id, person, form) VALUES (?, ?, ?)",
                        (word_id, person, form),
                    )
            elif pos == "noun":
                declensions = _parse_noun_forms(forms)
                for case, numbers in declensions.items():
                    cursor.execute(
                        "INSERT INTO noun_declensions (word_id, case_name, singular, plural) VALUES (?, ?, ?, ?)",
                        (word_id, case, numbers.get("singular"), numbers.get("plural")),
                    )
    conn.commit()
    conn.close()
    print("""
Import complete.""")


def _parse_verb_forms(forms):
    conjugations = {}
    person_map = {
        ("first-person", "singular"): "minä",
        ("second-person", "singular"): "sinä",
        ("third-person", "singular"): "hän",
        ("first-person", "plural"): "me",
        ("second-person", "plural"): "te",
        ("third-person", "plural"): "he",
    }
    for form_entry in forms:
        tags = set(form_entry.get("tags", []))
        if "present" in tags and "indicative" in tags and ("negative" not in tags):
            for tag_combo, person in person_map.items():
                if all((t in tags for t in tag_combo)):
                    conjugations[person] = form_entry.get("form")
                    break
    return conjugations


def _parse_noun_forms(forms):
    declensions = {}
    case_names = [
        "nominative",
        "genitive",
        "partitive",
        "inessive",
        "elative",
        "illative",
        "adessive",
        "ablative",
        "allative",
        "essive",
        "translative",
        "instructive",
        "abessive",
        "comitative",
    ]
    for form_entry in forms:
        tags = set(form_entry.get("tags", []))
        for case in case_names:
            if case in tags:
                number = "plural" if "plural" in tags else "singular"
                if case not in declensions:
                    declensions[case] = {}
                declensions[case][number] = form_entry.get("form")
                break
    return declensions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Finnish Dictionary Downloader and Importer."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    download_parser = subparsers.add_parser(
        "download", help="Download the dictionary file."
    )
    import_parser = subparsers.add_parser(
        "import", help="Import the dictionary into SQLite."
    )
    args = parser.parse_args()
    if args.command == "download":
        download_dictionary()
    elif args.command == "import":
        import_to_sqlite()