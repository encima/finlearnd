import sqlite3
from pathlib import Path
from typing import Optional
from app.states.state import Verb, Noun, WiktionaryResult

DATA_DIR = Path(".web")
DB_FILE = DATA_DIR / "finnish_dictionary.db"


def get_word_details(word: str) -> Optional[WiktionaryResult]:
    if not DB_FILE.exists():
        return None
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words WHERE word = ?", (word,))
    word_entry = cursor.fetchone()
    if not word_entry:
        conn.close()
        return None
    word_id = word_entry["id"]
    pos = word_entry["pos"]
    if pos == "verb":
        cursor.execute(
            "SELECT person, form FROM verb_conjugations WHERE word_id = ?", (word_id,)
        )
        conjugations = {row["person"]: row["form"] for row in cursor.fetchall()}
        conn.close()
        return Verb(
            type="verb", infinitive=word, verb_type=0, conjugations=conjugations
        )
    elif pos == "noun":
        cursor.execute(
            "SELECT case_name, singular, plural FROM noun_declensions WHERE word_id = ?",
            (word_id,),
        )
        declensions = {
            row["case_name"]: {"singular": row["singular"], "plural": row["plural"]}
            for row in cursor.fetchall()
        }
        conn.close()
        return Noun(type="noun", word=word, declensions=declensions)
    conn.close()
    return None