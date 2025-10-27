import reflex as rx
import requests
import logging
import httpx
from typing import Optional
from bs4 import BeautifulSoup

MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"


async def translate_text(
    text: str, source: str = "en", target: str = "fi"
) -> str | None:
    """Translate text using the MyMemory API."""
    try:
        params = {"q": text, "langpair": f"{source}|{target}"}
        response = requests.get(MYMEMORY_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["responseStatus"] == 200:
            return data["responseData"]["translatedText"]
        else:
            logging.warning(
                f"MyMemory API returned status {data['responseStatus']}: {data.get('responseDetails')}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error calling MyMemory API: {e}")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred during translation: {e}")
        return None


async def get_example_sentences(word: str) -> list[dict[str, str]]:
    """Fetch example sentences for a word from Tatoeba."""
    try:
        params = {"from": "fin", "query": word, "trans_to": "eng"}
        response = requests.get(
            "https://tatoeba.org/en/api_v0/search", params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            sentences = []
            for result in data["results"]:
                finnish_text = result.get("text", "")
                if result.get("translations") and result["translations"][0]:
                    english_text = result["translations"][0][0].get("text", "")
                    if finnish_text and english_text:
                        sentences.append(
                            {"finnish": finnish_text, "english": english_text}
                        )
            return sentences
        return []
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error calling Tatoeba API: {e}")
        return []
    except Exception as e:
        logging.exception(f"An unexpected error occurred during sentence fetch: {e}")
        return []


async def fetch_wiktionary_data(word: str) -> Optional[dict]:
    """Scrape Wiktionary for Finnish verb or noun data."""
    url = f"https://en.wiktionary.org/wiki/{word}#Finnish"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10)
            response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        finnish_header = soup.find(id="Finnish")
        if not finnish_header:
            logging.warning(f"No 'Finnish' section found for word '{word}'.")
            return None
        finnish_content = []
        current = finnish_header.parent
        while current:
            current = current.find_next_sibling()
            if not current or (
                current.name == "h2" and current.find(class_="mw-headline")
            ):
                break
            finnish_content.append(current)
        for element in finnish_content:
            tables = element.find_all("table", class_="inflection-table")
            for table in tables:
                first_row = table.find("tr")
                if first_row and "Possessive forms" in first_row.get_text():
                    continue
                verb_data = await parse_verb(word, table)
                if verb_data:
                    return verb_data
                noun_data = await parse_noun(word, table)
                if noun_data:
                    return noun_data
        logging.warning(f"No valid verb or noun inflection table found for '{word}'.")
        return None
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logging.warning(f"Wiktionary page not found for word '{word}': {url}")
        else:
            logging.exception(f"HTTP error fetching word '{word}': {e}")
        return None
    except Exception as e:
        logging.exception(f"Error parsing data for '{word}': {e}")
        return None


async def parse_verb(verb: str, table) -> Optional[dict]:
    """Parse verb conjugation from a given BeautifulSoup table element."""
    verb_type = 0
    first_row = table.find("tr")
    if first_row and "Kotus type" in first_row.get_text():
        parts = first_row.get_text().split()
        for i, part in enumerate(parts):
            if part == "type" and i + 1 < len(parts):
                type_str = "".join(filter(str.isdigit, parts[i + 1].split("/")[0]))
                if type_str:
                    verb_type = int(type_str)
                    break
    conjugations = {}
    person_map = {
        "1st\xa0sing.": "minä",
        "2nd\xa0sing.": "sinä",
        "3rd\xa0sing.": "hän",
        "1st\xa0plur.": "me",
        "2nd\xa0plur.": "te",
        "3rd\xa0plur.": "he",
    }
    for row in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        if len(cells) >= 2 and cells[0] in person_map:
            person_key = person_map[cells[0]]
            if person_key not in conjugations:
                conjugations[person_key] = cells[1]
    if len(conjugations) < 6:
        return None
    return {
        "type": "verb",
        "infinitive": verb,
        "verb_type": verb_type,
        "conjugations": conjugations,
    }


async def parse_noun(noun: str, table) -> Optional[dict]:
    """Parse noun declension from a given BeautifulSoup table element."""
    declensions = {}
    case_map = [
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
    rows = table.find_all("tr")
    header_row = rows[0].get_text().lower()
    if "singular" not in header_row and "plural" not in header_row:
        potential_header = rows[1].get_text().lower()
        if "singular" not in potential_header and "plural" not in potential_header:
            pass
        else:
            rows = rows[1:]
    for row in rows:
        cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        if not cells:
            continue
        case_name = cells[0].lower()
        if any((case in case_name for case in case_map)):
            found_case = next((case for case in case_map if case in case_name), None)
            if found_case and len(cells) > 2:
                singular_form = cells[1].split("/")[0].strip()
                plural_form = cells[2].split("/")[0].strip()
                if found_case not in declensions:
                    declensions[found_case] = {
                        "singular": singular_form,
                        "plural": plural_form,
                    }
            elif found_case and len(cells) > 1:
                if found_case not in declensions:
                    declensions[found_case] = {"singular": cells[1], "plural": "-"}
    if len(declensions) < 3:
        return None
    return {"type": "noun", "word": noun, "declensions": declensions}