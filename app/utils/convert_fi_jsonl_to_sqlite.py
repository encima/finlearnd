#!/usr/bin/env python3
"""Convert Finnish JSONL lexicon entries into a structured SQLite database.

The input file is expected to contain one JSON object per line following the
Wiktionary export structure present in ``fi.jsonl``. Only lemma entries with
``pos`` of ``noun`` or ``verb`` are imported. The resulting database tracks the
core information requested by the user:

* original word (lemma)
* translations (sense glosses)
* part of speech (noun or verb)
* conjugation/declension forms
* derived terms
* related terms
* additional sense-level metadata such as synonyms, antonyms, examples, etc.

The script streams the input file to keep memory usage low and can optionally
limit the number of processed entries for testing.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional


TARGET_PARTS_OF_SPEECH = {"noun", "verb"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_path",
        type=Path,
        nargs="?",
        default=Path("fi.jsonl"),
        help="Path to the source fi.jsonl file.",
    )
    parser.add_argument(
        "output_path",
        type=Path,
        nargs="?",
        default=Path("fi_words.sqlite"),
        help="Destination SQLite database path (will be created/overwritten).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of lemma entries processed (useful for testing).",
    )
    return parser.parse_args()


def init_database(connection: sqlite3.Connection) -> None:
    """Initialise schema required for the lexical data."""

    drop_statements = [
        "DROP TABLE IF EXISTS antonyms",
        "DROP TABLE IF EXISTS synonyms",
        "DROP TABLE IF EXISTS related_terms",
        "DROP TABLE IF EXISTS derived_terms",
        "DROP TABLE IF EXISTS forms",
        "DROP TABLE IF EXISTS senses",
        "DROP TABLE IF EXISTS entries",
    ]

    create_statements = [
        """
        CREATE TABLE entries (
            id INTEGER PRIMARY KEY,
            word TEXT NOT NULL,
            pos TEXT NOT NULL,
            primary_translation TEXT,
            etymology TEXT
        )
        """,
        """
        CREATE TABLE senses (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
            sense_identifier TEXT,
            gloss TEXT,
            glosses_json TEXT,
            raw_glosses_json TEXT,
            tags_json TEXT,
            topics_json TEXT,
            links_json TEXT,
            categories_json TEXT,
            examples_json TEXT,
            form_of_json TEXT
        )
        """,
        """
        CREATE TABLE forms (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
            form TEXT NOT NULL,
            tags_json TEXT,
            source TEXT
        )
        """,
        """
        CREATE TABLE derived_terms (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
            term TEXT NOT NULL,
            source_sense_identifier TEXT,
            extra_json TEXT
        )
        """,
        """
        CREATE TABLE related_terms (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
            term TEXT NOT NULL,
            source_sense_identifier TEXT,
            tags_json TEXT,
            extra_json TEXT
        )
        """,
        """
        CREATE TABLE synonyms (
            id INTEGER PRIMARY KEY,
            sense_id INTEGER NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
            term TEXT NOT NULL,
            tags_json TEXT,
            extra_json TEXT
        )
        """,
        """
        CREATE TABLE antonyms (
            id INTEGER PRIMARY KEY,
            sense_id INTEGER NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
            term TEXT NOT NULL,
            tags_json TEXT,
            extra_json TEXT
        )
        """,
        "CREATE INDEX idx_entries_word ON entries(word)",
        "CREATE INDEX idx_entries_pos ON entries(pos)",
        "CREATE INDEX idx_senses_entry ON senses(entry_id)",
        "CREATE INDEX idx_forms_entry ON forms(entry_id)",
        "CREATE INDEX idx_derived_entry ON derived_terms(entry_id)",
        "CREATE INDEX idx_related_entry ON related_terms(entry_id)",
    ]

    with connection:
        for statement in drop_statements:
            connection.execute(statement)
        for statement in create_statements:
            connection.execute(statement)


def json_or_none(payload: Any) -> Optional[str]:
    if not payload:
        return None
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def normalise_term(candidate: Any) -> Optional[str]:
    if isinstance(candidate, str):
        return candidate.strip() or None
    if isinstance(candidate, dict):
        for key in ("word", "term", "text", "english", "translation"):
            value = candidate.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc


def process_entries(
    source_path: Path,
    connection: sqlite3.Connection,
    limit: Optional[int] = None,
) -> tuple[int, int]:
    cursor = connection.cursor()

    processed = 0
    inserted = 0
    for entry in iter_jsonl(source_path):
        if limit is not None and processed >= limit:
            break

        processed += 1

        if entry.get("pos") not in TARGET_PARTS_OF_SPEECH:
            continue

        word = entry.get("word")
        if not word:
            continue

        primary_translation = None
        senses_payload = entry.get("senses") or []
        for sense in senses_payload:
            glosses = sense.get("glosses") or sense.get("raw_glosses") or []
            if glosses:
                primary_translation = glosses[0]
                break

        cursor.execute(
            """
            INSERT INTO entries (word, pos, primary_translation, etymology)
            VALUES (?, ?, ?, ?)
            """,
            (
                word,
                entry.get("pos"),
                primary_translation,
                entry.get("etymology_text"),
            ),
        )
        entry_id = cursor.lastrowid
        inserted += 1

        insert_senses(cursor, entry_id, senses_payload)
        insert_forms(cursor, entry_id, entry.get("forms") or [])
        insert_terms_collection(
            cursor,
            table="derived_terms",
            entry_id=entry_id,
            items=entry.get("derived"),
        )
        insert_terms_collection(
            cursor,
            table="related_terms",
            entry_id=entry_id,
            items=entry.get("related"),
        )

    connection.commit()
    return processed, inserted


def insert_senses(
    cursor: sqlite3.Cursor,
    entry_id: int,
    senses: Iterable[dict[str, Any]],
) -> None:
    for sense in senses:
        sense_identifier = sense.get("id")
        glosses = sense.get("glosses")
        raw_glosses = sense.get("raw_glosses")
        gloss = None
        if glosses:
            gloss = glosses[0]
        elif raw_glosses:
            gloss = raw_glosses[0]

        cursor.execute(
            """
            INSERT INTO senses (
                entry_id,
                sense_identifier,
                gloss,
                glosses_json,
                raw_glosses_json,
                tags_json,
                topics_json,
                links_json,
                categories_json,
                examples_json,
                form_of_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                sense_identifier,
                gloss,
                json_or_none(glosses),
                json_or_none(raw_glosses),
                json_or_none(sense.get("tags")),
                json_or_none(sense.get("topics")),
                json_or_none(sense.get("links")),
                json_or_none(sense.get("categories")),
                json_or_none(sense.get("examples")),
                json_or_none(sense.get("form_of")),
            ),
        )
        sense_id = cursor.lastrowid

        insert_terms_collection(
            cursor,
            table="derived_terms",
            entry_id=entry_id,
            items=sense.get("derived"),
            sense_identifier=sense_identifier,
        )
        insert_terms_collection(
            cursor,
            table="related_terms",
            entry_id=entry_id,
            items=sense.get("related"),
            sense_identifier=sense_identifier,
        )

        insert_syn_ant_collection(
            cursor, table="synonyms", sense_id=sense_id, items=sense.get("synonyms")
        )
        insert_syn_ant_collection(
            cursor,
            table="antonyms",
            sense_id=sense_id,
            items=sense.get("antonyms"),
        )


def insert_forms(
    cursor: sqlite3.Cursor,
    entry_id: int,
    forms: Iterable[dict[str, Any]],
) -> None:
    for form_payload in forms:
        form = form_payload.get("form")
        if not form:
            continue
        cursor.execute(
            """
            INSERT INTO forms (entry_id, form, tags_json, source)
            VALUES (?, ?, ?, ?)
            """,
            (
                entry_id,
                form,
                json_or_none(form_payload.get("tags")),
                form_payload.get("source"),
            ),
        )


def insert_terms_collection(
    cursor: sqlite3.Cursor,
    *,
    table: str,
    entry_id: int,
    items: Optional[Iterable[Any]],
    sense_identifier: Optional[str] = None,
) -> None:
    if not items:
        return

    for item in items:
        term = normalise_term(item)
        if not term:
            continue

        extra_json = None
        tags_json = None
        if isinstance(item, dict):
            metadata = {
                k: v
                for k, v in item.items()
                if k not in {"word", "term", "text", "english", "translation"}
            }
            if metadata:
                if table == "related_terms":
                    tags = metadata.pop("tags", None)
                    tags_json = json_or_none(tags)
                extra_json = json_or_none(metadata)

        if table == "derived_terms":
            cursor.execute(
                """
                INSERT INTO derived_terms (entry_id, term, source_sense_identifier, extra_json)
                VALUES (?, ?, ?, ?)
                """,
                (entry_id, term, sense_identifier, extra_json),
            )
        elif table == "related_terms":
            cursor.execute(
                """
                INSERT INTO related_terms (
                    entry_id,
                    term,
                    source_sense_identifier,
                    tags_json,
                    extra_json
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (entry_id, term, sense_identifier, tags_json, extra_json),
            )
        else:  # pragma: no cover - guarded by caller
            raise ValueError(f"Unsupported table for term insertion: {table}")


def insert_syn_ant_collection(
    cursor: sqlite3.Cursor,
    *,
    table: str,
    sense_id: int,
    items: Optional[Iterable[Any]],
) -> None:
    if not items:
        return

    for item in items:
        term = normalise_term(item)
        if not term:
            continue

        tags_json = None
        extra_json = None
        if isinstance(item, dict):
            tags_json = json_or_none(item.get("tags"))
            metadata = {
                k: v
                for k, v in item.items()
                if k not in {"word", "term", "text", "english", "translation", "tags"}
            }
            extra_json = json_or_none(metadata)

        cursor.execute(
            f"""
            INSERT INTO {table} (sense_id, term, tags_json, extra_json)
            VALUES (?, ?, ?, ?)
            """,
            (sense_id, term, tags_json, extra_json),
        )


def main() -> None:
    args = parse_args()

    if not args.input_path.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_path}")

    connection = sqlite3.connect(args.output_path)
    try:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        init_database(connection)
        processed, inserted = process_entries(args.input_path, connection, args.limit)
    finally:
        connection.close()

    print(
        "Completed. Processed {processed} JSON objects, inserted {inserted} noun/verb entries into {output}.".format(
            processed=processed,
            inserted=inserted,
            output=args.output_path,
        )
    )


if __name__ == "__main__":
    main()
