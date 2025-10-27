import reflex as rx
import random
import httpx
import logging
import json
from typing import TypedDict, Literal, Optional

FINNISH_WORDS_URL = (
    "https://raw.githubusercontent.com/Trimpsuz/finnish-words/main/words.txt"
)
WORD_CACHE_FILE = ".web/word_cache.json"


class Sentence(TypedDict):
    english: str
    finnish: str


class Question(TypedDict):
    question: str
    options: list[str]
    answer: str


class VocabWord(TypedDict):
    finnish: str
    english: str
    category: str
    difficulty: str
    example_finnish: str
    example_english: str
    rank: int


class GrammarExercise(TypedDict):
    verb: str
    person: str
    prompt: str
    answer: str
    verb_type: int


class Verb(TypedDict):
    type: Literal["verb"]
    infinitive: str
    verb_type: int
    conjugations: dict[str, str]


class Noun(TypedDict):
    type: Literal["noun"]
    word: str
    declensions: dict[str, dict[str, str]]


WiktionaryResult = Verb | Noun
LearningMode = Literal[
    "Translation Practice",
    "Question Mode",
    "Vocabulary Builder",
    "Grammar Practice",
    "Flashcards",
    "Progress Dashboard",
    "Word Lookup",
]


def get_difficulty(rank: int) -> str:
    if rank <= 1000:
        return "Beginner"
    if rank <= 3000:
        return "Intermediate"
    if rank <= 6000:
        return "Advanced"
    return "Expert"


class TranslationState(rx.State):
    drawer_open: bool = True
    current_page: LearningMode = "Translation Practice"
    is_generating_sentence: bool = False
    sentences: list[Sentence] = [
        {
            "english": "The house is big and beautiful.",
            "finnish": "Talo on suuri ja kaunis.",
        },
        {
            "english": "I am learning the Finnish language.",
            "finnish": "Minä opiskelen suomen kieltä.",
        },
        {
            "english": "Where is the nearest train station?",
            "finnish": "Missä on lähin rautatieasema?",
        },
        {"english": "It is cold outside today.", "finnish": "Tänään ulkona on kylmä."},
        {
            "english": "She reads a book in the library.",
            "finnish": "Hän lukee kirjaa kirjastossa.",
        },
    ]
    current_sentence_index: int = 0
    user_translation: str = ""
    feedback_message: str = ""
    show_feedback: bool = False
    is_correct: bool = False
    completed_count: int = 0
    correct_count: int = 0
    error_patterns: dict[str, int] = {
        "Word Order": 2,
        "Case Ending": 5,
        "Vocabulary": 3,
    }
    questions: list[Question] = [
        {
            "question": "Mikä on 'kirja' englanniksi?",
            "options": ["House", "Book", "Car", "Tree"],
            "answer": "Book",
        },
        {
            "question": "Täydennä lause: 'Minä ___ kahvia.'",
            "options": ["juon", "syön", "nukun", "luen"],
            "answer": "juon",
        },
    ]
    current_question_index: int = 0
    selected_option: Optional[str] = None
    question_feedback: str = ""
    show_question_feedback: bool = False
    question_correct_count: int = 0
    question_completed_count: int = 0
    all_finnish_words: list[str] = []
    is_loading_words: bool = False
    loading_words_progress: str = ""
    vocab_words: list[VocabWord] = [
        {
            "finnish": "talo",
            "english": "house",
            "category": "places",
            "difficulty": "beginner",
            "example_finnish": "Talo on punainen.",
            "example_english": "The house is red.",
        },
        {
            "finnish": "auto",
            "english": "car",
            "category": "travel",
            "difficulty": "beginner",
            "example_finnish": "Ajan autolla.",
            "example_english": "I drive a car.",
        },
        {
            "finnish": "kirja",
            "english": "book",
            "category": "objects",
            "difficulty": "beginner",
            "example_finnish": "Luen kirjaa.",
            "example_english": "I am reading a book.",
        },
        {
            "finnish": "omena",
            "english": "apple",
            "category": "food",
            "difficulty": "beginner",
            "example_finnish": "Syön omenan.",
            "example_english": "I am eating an apple.",
        },
        {
            "finnish": "ystävä",
            "english": "friend",
            "category": "people",
            "difficulty": "beginner",
            "example_finnish": "Hän on minun ystäväni.",
            "example_english": "He is my friend.",
            "rank": 5,
        },
    ]
    current_vocab_index: int = 0
    vocab_card_flipped: bool = False
    grammar_exercises: list[GrammarExercise] = [
        {
            "verb": "olla",
            "person": "minä",
            "prompt": "Minä ___ opiskelija.",
            "answer": "olen",
            "verb_type": 3,
        },
        {
            "verb": "syödä",
            "person": "sinä",
            "prompt": "Sinä ___ omenaa.",
            "answer": "syöt",
            "verb_type": 2,
        },
        {
            "verb": "puhua",
            "person": "hän",
            "prompt": "Hän ___ suomea.",
            "answer": "puhuu",
            "verb_type": 1,
        },
        {
            "verb": "asua",
            "person": "me",
            "prompt": "Me ___ Helsingissä.",
            "answer": "asumme",
            "verb_type": 1,
        },
        {
            "verb": "juoda",
            "person": "te",
            "prompt": "Te ___ vettä.",
            "answer": "juotte",
            "verb_type": 2,
        },
        {
            "verb": "nähdä",
            "person": "he",
            "prompt": "He ___ elokuvan.",
            "answer": "näkevät",
            "verb_type": 2,
        },
        {
            "verb": "sanoa",
            "person": "minä",
            "prompt": "Minä ___ totuuden.",
            "answer": "sanon",
            "verb_type": 1,
        },
        {
            "verb": "tehdä",
            "person": "hän",
            "prompt": "Hän ___ työnsä hyvin.",
            "answer": "tekee",
            "verb_type": 2,
        },
        {
            "verb": "tulla",
            "person": "me",
            "prompt": "Me ___ kotiin.",
            "answer": "tulemme",
            "verb_type": 3,
        },
        {
            "verb": "mennä",
            "person": "sinä",
            "prompt": "Minne sinä ___?",
            "answer": "menet",
            "verb_type": 3,
        },
        {
            "verb": "haluta",
            "person": "he",
            "prompt": "He ___ matkustaa.",
            "answer": "haluavat",
            "verb_type": 4,
        },
        {
            "verb": "tarvita",
            "person": "minä",
            "prompt": "Minä ___ apua.",
            "answer": "tarvitsen",
            "verb_type": 5,
        },
        {
            "verb": "paeta",
            "person": "hän",
            "prompt": "Vanki ___.",
            "answer": "pakenee",
            "verb_type": 6,
        },
    ]
    current_grammar_index: int = 0
    user_grammar_answer: str = ""
    show_grammar_feedback: bool = False
    grammar_is_correct: bool = False
    is_searching_word: bool = False
    word_search_query: str = ""
    word_database: list[WiktionaryResult] = []
    searched_word_result: Optional[WiktionaryResult] = None

    @rx.var
    def current_sentence(self) -> Sentence:
        if self.current_sentence_index < len(self.sentences):
            return self.sentences[self.current_sentence_index]
        return {"english": "All sentences completed!", "finnish": ""}

    @rx.var
    def accuracy(self) -> int:
        return (
            int(self.correct_count / self.completed_count * 100)
            if self.completed_count > 0
            else 0
        )

    @rx.var
    def proficiency_level(self) -> str:
        if self.accuracy > 90:
            return "A2"
        if self.accuracy > 70:
            return "A1"
        return "Beginner"

    @rx.var
    def level_progress(self) -> int:
        if self.proficiency_level == "A2":
            return (self.accuracy - 90) * 10
        if self.proficiency_level == "A1":
            return (self.accuracy - 70) * 5
        return self.accuracy

    @rx.var
    def user_translation_words(self) -> list[str]:
        return self.user_translation.split()

    @rx.var
    def correct_translation_words(self) -> list[str]:
        return self.current_sentence["finnish"].split()

    @rx.var
    def current_question(self) -> Question:
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return {"question": "All questions completed!", "options": [], "answer": ""}

    @rx.var
    def question_accuracy(self) -> int:
        return (
            int(self.question_correct_count / self.question_completed_count * 100)
            if self.question_completed_count > 0
            else 0
        )

    @rx.var
    def total_sessions(self) -> int:
        return self.completed_count + self.question_completed_count

    @rx.var
    def overall_accuracy(self) -> int:
        total_completed = self.completed_count + self.question_completed_count
        total_correct = self.correct_count + self.question_correct_count
        return int(total_correct / total_completed * 100) if total_completed > 0 else 0

    @rx.var
    def performance_data(self) -> list[dict[str, str | int]]:
        return [
            {"name": "Translation", "accuracy": self.accuracy},
            {"name": "Questions", "accuracy": self.question_accuracy},
        ]

    @rx.var
    def error_patterns_data(self) -> list[dict[str, str | int]]:
        return [{"name": k, "value": v} for k, v in self.error_patterns.items()]

    @rx.var
    def weakest_areas(self) -> list[tuple[str, int]]:
        return sorted(
            self.error_patterns.items(), key=lambda item: item[1], reverse=True
        )[:2]

    @rx.var
    def current_vocab_word(self) -> VocabWord:
        return self.vocab_words[self.current_vocab_index]

    @rx.var
    def current_grammar_exercise(self) -> GrammarExercise:
        if self.current_grammar_index < len(self.grammar_exercises):
            return self.grammar_exercises[self.current_grammar_index]
        return {
            "verb": "",
            "person": "",
            "prompt": "All exercises completed!",
            "answer": "",
            "verb_type": 0,
        }

    @rx.event
    def on_load(self):
        return TranslationState.load_word_list

    @rx.event
    def toggle_drawer(self):
        self.drawer_open = not self.drawer_open

    @rx.event
    def set_page(self, page_name: LearningMode):
        self.current_page = page_name
        self.drawer_open = False
        self.show_feedback = False
        self.show_question_feedback = False
        self.vocab_card_flipped = False
        self.show_grammar_feedback = False
        self.word_search_query = ""

    @rx.event
    def submit_translation(self):
        self.completed_count += 1
        correct_answer = self.current_sentence["finnish"].strip().lower()
        user_answer = self.user_translation.strip().lower()
        if user_answer == correct_answer:
            self.is_correct = True
            self.correct_count += 1
            self.feedback_message = "Oikein! (Correct!)"
        else:
            self.is_correct = False
            self.feedback_message = "Not quite, try again. Here's the correct answer:"
            if len(user_answer.split()) != len(correct_answer.split()):
                self.error_patterns["Word Order"] += 1
            else:
                self.error_patterns["Case Ending"] += 1
        self.show_feedback = True

    @rx.event
    def next_sentence(self):
        self.show_feedback = False
        self.user_translation = ""
        self.current_sentence_index = (self.current_sentence_index + 1) % len(
            self.sentences
        )

    @rx.event
    def skip_sentence(self):
        self.next_sentence()

    @rx.event
    def select_answer(self, option: str):
        self.selected_option = option

    @rx.event
    def submit_question(self):
        if self.selected_option is None:
            return
        self.question_completed_count += 1
        if self.selected_option == self.current_question["answer"]:
            self.question_correct_count += 1
            self.question_feedback = "Correct!"
        else:
            self.question_feedback = (
                f"Incorrect. The correct answer is: {self.current_question['answer']}"
            )
        self.show_question_feedback = True

    @rx.event
    def next_question(self):
        self.show_question_feedback = False
        self.selected_option = None
        self.current_question_index = (self.current_question_index + 1) % len(
            self.questions
        )

    @rx.event
    def flip_vocab_card(self):
        self.vocab_card_flipped = not self.vocab_card_flipped

    @rx.event
    def next_vocab_word(self):
        self.vocab_card_flipped = False
        self.current_vocab_index = (self.current_vocab_index + 1) % len(
            self.vocab_words
        )

    @rx.event
    def prev_vocab_word(self):
        self.vocab_card_flipped = False
        self.current_vocab_index = (
            self.current_vocab_index - 1 + len(self.vocab_words)
        ) % len(self.vocab_words)

    @rx.event
    def submit_grammar(self):
        self.show_grammar_feedback = True
        correct_answer = self.current_grammar_exercise["answer"].strip().lower()
        user_answer = self.user_grammar_answer.strip().lower()
        self.grammar_is_correct = user_answer == correct_answer

    @rx.event
    def next_grammar_exercise(self):
        self.show_grammar_feedback = False
        self.user_grammar_answer = ""
        self.current_grammar_index = (self.current_grammar_index + 1) % len(
            self.grammar_exercises
        )

    @rx.event
    def search_word(self, query: str):
        self.word_search_query = query.strip().lower()
        if not self.word_search_query:
            self.searched_word_result = None
            return
        return TranslationState.lookup_word_from_db

    @rx.event
    def add_word_to_flashcards(self, word: WiktionaryResult):
        word_finnish = word.get("infinitive", word.get("word", ""))
        word_english = f"to {word_finnish}" if word["type"] == "verb" else word_finnish
        new_vocab_word = VocabWord(
            finnish=word_finnish,
            english=word_english,
            category=word["type"],
            difficulty="user-added",
            example_finnish="Example sentence to be added.",
            example_english="Example sentence to be added.",
            rank=9999,
        )
        if not any((v["finnish"] == word_finnish for v in self.vocab_words)):
            self.vocab_words.append(new_vocab_word)
            return rx.toast(f'Added "{word_finnish}" to vocabulary!')
        return rx.toast(f'"{word_finnish}" is already in your vocabulary.')

    @rx.event(background=True)
    async def generate_new_sentence(self):
        async with self:
            if self.is_generating_sentence:
                return
            self.is_generating_sentence = True
        yield
        from app.states.api_helpers import translate_text, get_example_sentences

        english_sentences = [
            "The sun is shining.",
            "I love to read books.",
            "Let's go to the park.",
            "This food is delicious.",
            "What time is it?",
            "My cat is sleeping.",
            "Winter is coming soon.",
        ]
        english_sentence = random.choice(english_sentences)
        finnish_translation = await translate_text(english_sentence)
        async with self:
            if finnish_translation:
                new_sentence = Sentence(
                    english=english_sentence, finnish=finnish_translation
                )
                if new_sentence not in self.sentences:
                    self.sentences.append(new_sentence)
                    yield rx.toast("New sentence added!", duration=3000)
                else:
                    yield rx.toast(
                        "Generated a sentence that already exists.", duration=3000
                    )
            else:
                yield rx.toast(
                    "Could not generate a new sentence. Please try again later.",
                    duration=5000,
                )
            self.is_generating_sentence = False

    @rx.event(background=True)
    async def lookup_word_from_db(self):
        async with self:
            if not self.word_search_query:
                self.searched_word_result = None
                return
            self.is_searching_word = True
            self.searched_word_result = None
        yield
        from app.utils.db_helper import get_word_details

        word_data = get_word_details(self.word_search_query)
        async with self:
            self.is_searching_word = False
            if word_data:
                self.searched_word_result = word_data
                yield rx.toast.success(
                    f'Successfully looked up "{self.word_search_query}" from local DB!'
                )
            else:
                yield rx.toast.error(
                    f'Could not find "{self.word_search_query}" in the local dictionary. Check spelling or import the dictionary first.'
                )

    @rx.event(background=True)
    async def load_word_list(self):
        async with self:
            if self.all_finnish_words:
                if len(self.vocab_words) < 10:
                    async for event in self._update_vocab_from_master_list():
                        yield event
                return
            self.is_loading_words = True
            self.loading_words_progress = "Checking cache..."
        yield
        try:
            with open(WORD_CACHE_FILE, "r") as f:
                words = json.load(f)
            async with self:
                self.all_finnish_words = words
                self.loading_words_progress = "Loaded from cache!"
            yield rx.toast.info(f"Loaded {len(words)} words from cache.")
        except (FileNotFoundError, json.JSONDecodeError):
            async with self:
                self.loading_words_progress = "Fetching from GitHub..."
            yield
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(FINNISH_WORDS_URL, timeout=30)
                    response.raise_for_status()
                words = response.text.strip().split("""
""")
                async with self:
                    self.all_finnish_words = words
                    self.loading_words_progress = "Words fetched!"
                with open(WORD_CACHE_FILE, "w") as f:
                    json.dump(words, f)
                yield rx.toast.success(f"Fetched and cached {len(words)} words.")
            except httpx.RequestError as e:
                async with self:
                    self.loading_words_progress = "Failed to fetch words."
                logging.exception(f"Failed to fetch word list: {e}")
                yield rx.toast.error("Could not fetch word list.")
                return
        async for event in self._update_vocab_from_master_list():
            yield event
        async with self:
            self.is_loading_words = False

    async def _update_vocab_from_master_list(self):
        if not self.all_finnish_words:
            logging.warning(
                "_update_vocab_from_master_list called with no words loaded."
            )
            return
        new_vocab = []
        for i, word in enumerate(self.all_finnish_words[:200]):
            new_vocab.append(
                VocabWord(
                    finnish=word,
                    english="...",
                    category="common words",
                    difficulty=get_difficulty(i + 1),
                    example_finnish="...",
                    example_english="...",
                    rank=i + 1,
                )
            )
        async with self:
            self.vocab_words = new_vocab
            self.current_vocab_index = 0
        yield
        yield TranslationState.fetch_current_vocab_details

    @rx.event(background=True)
    async def fetch_current_vocab_details(self):
        async with self:
            word = self.current_vocab_word
            if word["english"] != "...":
                return
        from app.states.api_helpers import translate_text, get_example_sentences

        translation = await translate_text(word["finnish"], source="fi", target="en")
        examples = await get_example_sentences(word["finnish"])
        async with self:
            idx = self.current_vocab_index
            self.vocab_words[idx]["english"] = translation or "N/A"
            if examples:
                self.vocab_words[idx]["example_finnish"] = examples[0]["finnish"]
                self.vocab_words[idx]["example_english"] = examples[0]["english"]
            else:
                self.vocab_words[idx]["example_finnish"] = "No example found."
                self.vocab_words[idx]["example_english"] = ""
        yield

    @rx.event
    def next_vocab_word(self):
        self.vocab_card_flipped = False
        self.current_vocab_index = (self.current_vocab_index + 1) % len(
            self.vocab_words
        )
        yield TranslationState.fetch_current_vocab_details

    @rx.event
    def prev_vocab_word(self):
        self.vocab_card_flipped = False
        self.current_vocab_index = (
            self.current_vocab_index - 1 + len(self.vocab_words)
        ) % len(self.vocab_words)
        yield TranslationState.fetch_current_vocab_details