# Finnish Language Learning App - Project Plan

## Phase 1: Core Layout & Translation Mode ✅
- [x] Create Material Design 3 base layout with app bar, navigation drawer, and main content area
- [x] Implement translation learning mode UI with sentence display, input field, and feedback system
- [x] Build state management for tracking user translations and error patterns
- [x] Add progress indicators and level assessment display
- [x] Design and implement error analysis system to identify weak areas

---

## Phase 2: Question Answering Mode & Vocabulary Builder ✅
- [x] Create question-answering interface with Finnish questions and user response capture
- [x] Implement vocabulary learning mode with word cards showing Finnish words, translations, and example sentences
- [x] Build vocabulary database with categorized words and difficulty levels
- [x] Add spaced repetition system for vocabulary review
- [x] Create user vocabulary progress tracking and statistics

---

## Phase 3: Grammar Practice & Adaptive Flashcard System ✅
- [x] Implement grammar practice mode focusing on word endings, cases, and conjugations
- [x] Build adaptive flashcard generation based on user error patterns from translations and questions
- [x] Create level assessment algorithm analyzing user performance across all modes
- [x] Add comprehensive progress dashboard showing strengths, weaknesses, and recommended focus areas
- [x] Implement session history and detailed analytics for each learning mode

---

## Phase 4: Enhanced Verb Conjugation & Lookup Tool ✅
- [x] Add verb type classification (Type 1-6) to grammar exercises
- [x] Display verb type information in grammar practice interface
- [x] Create verb lookup tool where users can search any Finnish verb
- [x] Show complete conjugation table for all persons (minä, sinä, hän, me, te, he)
- [x] Display example sentences for each verb form
- [x] Add "Add to Flashcards" button to save verbs to personal vocabulary collection
- [x] Build comprehensive verb database with types and conjugation patterns

---

## Phase 5: Comprehensive Verb Database ✅
- [x] Expand verb database to 35+ common Finnish verbs
- [x] Include verbs across all 6 verb types (Type 1-6)
- [x] Add complete conjugations for all 6 persons for each verb
- [x] Include realistic Finnish example sentences for each conjugated form
- [x] Verify verb search functionality works correctly
- [x] Test flashcard integration with verb data

---

## Phase 6: External API Integration ✅
- [x] Integrate MyMemory Translation API for dynamic sentence generation
- [x] Add "Generate New Sentence" button in Translation Practice mode
- [x] Implement loading states and error handling for API calls
- [x] Add Wiktionary external links in Verb Conjugator for dictionary lookups
- [x] Add Tatoeba external links for real sentence examples
- [x] Add "Look up definition" button in Vocabulary Builder
- [x] Create API helper module with translation and lookup functions
- [x] Add "Powered by MyMemory" attribution
- [x] Implement duplicate sentence prevention
- [x] Add request timeouts and user-friendly error messages

---

## Phase 7: 10K Most Common Finnish Words Integration ✅
- [x] Download and integrate the 10,000 most common Finnish words frequency list
- [x] Create word loading system that fetches Finnish words from external source (GitHub)
- [x] Build caching layer to store words locally for offline access (JSON file)
- [x] Implement frequency-based word selection (first 200 words loaded initially)
- [x] Add progress tracking: "1 / 200" displayed in vocabulary navigator
- [x] Create dynamic VocabWord entries with rank and difficulty classification
- [x] Replace hardcoded vocabulary list with words from 10K dataset
- [x] Add loading states with progress messages
- [x] Implement definition fetching on word navigation using MyMemory API
- [x] Add example sentence fetching from Tatoeba API

---

## Phase 8: Enhanced Vocabulary Features & Polish ✅
- [x] Fix "Cannot directly call background task" error on page load
- [x] **FIX DYNAMIC VERB CONJUGATION - Wiktionary Scraping** ✅
  - [x] Fix verb conjugator to work for ANY Finnish verb (not just hardcoded database)
  - [x] Implement Wiktionary HTML scraping with BeautifulSoup
  - [x] Parse conjugation tables from Wiktionary pages
  - [x] Extract Kotus verb types (52, 61, 67, 70, etc.)
  - [x] Extract all 6 present tense conjugations (minä, sinä, hän, me, te, he)
  - [x] Handle complex type notation like "61*B/sallia"
  - [x] Cache fetched verbs in verb_database for faster subsequent lookups
  - [x] Add loading states and error handling
  - [x] Test with various verbs: juosta, oppia, olla, puhua, syödä, tulla, haluta
- [x] **GENERALIZE WORD LOOKUP - Add Noun Declensions** ✅
  - [x] Rename "Verb Conjugator" to "Word Lookup" in sidebar and UI
  - [x] Update state variables: verb_search_query → word_search_query
  - [x] Add TypedDict for Noun type with word and declensions fields
  - [x] Create WiktionaryResult union type (Verb | Noun)
  - [x] Implement parse_noun function to extract declension tables
  - [x] Parse all 15 Finnish noun cases with singular and plural forms
  - [x] Update UI to show conjugation_table for verbs and declension_table for nouns
  - [x] Add green "Noun" badge for nouns (vs orange "Verb Type X" for verbs)
  - [x] Display 3-column declension table: CASE | SINGULAR | PLURAL
  - [x] Update search placeholder: "E.g., 'puhua', 'talo', 'kissa'..."
  - [x] Update description: "Look up conjugations for verbs or declensions for nouns"
  - [x] Test with multiple nouns: talo, kissa, auto
  - [x] Verify "Add to Flashcards" works for both verbs and nouns

---

## Phase 9: Kaikki.org Local Dictionary Database ✅
- [x] **CREATE DICTIONARY DOWNLOADER TOOL** ✅
  - [x] Build command-line tool: `python -m app.utils.dictionary_downloader`
  - [x] Support `download` command to fetch Kaikki.org JSONL (246MB)
  - [x] Support `import` command to parse and load into SQLite
  - [x] Parse JSONL entries with proper field extraction
  - [x] Extract verb conjugations from forms array (present tense, 6 persons)
  - [x] Extract noun declensions from forms array (all 15 Finnish cases)
  - [x] Extract verb types from inflection templates (Kotus types)
  - [x] Extract English definitions from senses/glosses
  - [x] Filter to only Finnish words (lang_code == 'fi')
  - [x] Filter to only verbs and nouns
  - [x] Show download progress with file size and percentage
  - [x] Show import progress with entry count and estimated time
  
- [x] **CREATE SQLITE DATABASE SCHEMA** ✅
  - [x] Create normalized relational schema
  - [x] Table: `words` (id, word, pos, definition, etymology, frequency)
  - [x] Table: `verb_conjugations` (word_id, person, form)
  - [x] Table: `noun_declensions` (word_id, case_name, singular, plural)
  - [x] Table: `pronunciations` (word_id, ipa)
  - [x] Add indexes on word and pos columns for fast lookups
  - [x] Store database at `.web/finnish_dictionary.db`
  
- [x] **CREATE DATABASE HELPER MODULE** ✅
  - [x] Implement `get_word_details(word)` in app/utils/db_helper.py
  - [x] Query SQLite for verb conjugations
  - [x] Query SQLite for noun declensions
  - [x] Return same TypedDict format (Verb | Noun) for compatibility
  - [x] Handle case-insensitive lookups
  - [x] Return None if word not found
  
- [x] **UPDATE APP TO USE LOCAL DATABASE** ✅
  - [x] Update TranslationState.lookup_word_from_db to use db_helper
  - [x] Replace Wiktionary scraping with local database queries
  - [x] Add fallback to Wiktionary if word not in local database
  - [x] Maintain same UI and TypedDict structure
  - [x] Add toast messages indicating local vs external lookup
  - [x] Test with verbs: puhua, olla, tulla
  - [x] Test with nouns: talo, kissa, auto

---

## Phase 10: Spaced Repetition & Advanced Features
- [ ] Implement spaced repetition algorithm based on user performance
- [ ] Add "confidence rating" after each flashcard: Easy/Good/Hard/Again
- [ ] Schedule word reviews based on forgetting curve
- [ ] Create "Review Due" section showing words that need practice
- [ ] Add daily vocabulary goals and streak tracking
- [ ] Implement word mastery levels: Learning → Familiar → Mastered
- [ ] Add vocabulary quiz mode with multiple choice from learned words
- [ ] Show word frequency rank on flashcards (e.g., "#15 most common")

---

## Additional Notes
- Material Design 3 with violet primary color and gray secondary
- Lato font family throughout
- Elevation system for cards and interactive elements
- Ripple effects on all buttons and interactive components
- Responsive layout adapting to different screen sizes
- User level tracking: Beginner (A1-A2), Intermediate (B1-B2), Advanced (C1-C2)

## Current Focus
🎯 **Phase 9: Kaikki.org Local Dictionary Database - Ready for testing**

## How to Use the Dictionary Downloader

### Step 1: Download the dictionary (246 MB)
```bash
python -m app.utils.dictionary_downloader download
```

### Step 2: Import into SQLite database (takes 5-10 minutes)
```bash
python -m app.utils.dictionary_downloader import
```

### Step 3: The app will automatically use the local database
- Word lookups will be instant (no network requests)
- Works offline after initial download
- Contains 100,000+ Finnish words with full conjugations/declensions

## Technical Implementation Notes

### Kaikki.org Dictionary Integration
- **Source**: https://kaikki.org/dictionary/Finnish/kaikki.org-dictionary-Finnish.jsonl
- **Format**: JSONL (JSON Lines) - one entry per line
- **Size**: 246 MB (uncompressed), ~100,000 entries
- **Data Structure**: 
  - Entry contains: word, pos, senses (definitions), forms (inflections), etymology
  - Forms array has 50-200+ entries per word with grammatical tags
  - Tags indicate person, number, case, tense, mood, etc.
  
### Verb Conjugation Extraction
- Filter forms by tags: `['present', 'indicative', 'first-person', 'singular']` → minä form
- Skip negative forms (tags containing 'negative')
- Extract all 6 persons: minä, sinä, hän, me, te, he
- Extract verb type from inflection_templates or class tag (e.g., '52/sanoa')

### Noun Declension Extraction
- Filter forms by case tags: nominative, genitive, partitive, etc.
- Determine singular/plural by checking for 'singular' or 'plural' in tags
- Store both forms for all 15 Finnish noun cases
- Handle special cases like comitative and instructive

### Database Structure
```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    pos TEXT NOT NULL,  -- 'verb' or 'noun'
    definition TEXT
);

CREATE TABLE verb_conjugations (
    word_id INTEGER,
    person TEXT NOT NULL,  -- 'minä', 'sinä', 'hän', 'me', 'te', 'he'
    form TEXT NOT NULL,
    FOREIGN KEY(word_id) REFERENCES words(id)
);

CREATE TABLE noun_declensions (
    word_id INTEGER,
    case_name TEXT NOT NULL,  -- 'nominative', 'genitive', etc.
    singular TEXT,
    plural TEXT,
    FOREIGN KEY(word_id) REFERENCES words(id)
);
```

### Performance Optimization
- Indexed lookups on word column: O(log n) query time
- Single SQL query retrieves all conjugations/declensions
- No network requests after initial database creation
- ~10 MB database file size after compression

## Completed Features
✅ Translation Practice with error tracking
✅ Question Mode with multiple choice
✅ Vocabulary Builder with flashcards
✅ Grammar Practice with verb conjugation
✅ Progress Dashboard with statistics and charts
✅ Adaptive learning based on user performance
✅ Proficiency level assessment (Beginner → A1 → A2)
✅ Verb type classification system
✅ Dynamic verb lookup and conjugation tool (Wiktionary scraping)
✅ Dynamic noun lookup and declension tool (Wiktionary scraping)
✅ Unified Word Lookup interface supporting both verbs and nouns
✅ Add to flashcards functionality
✅ Comprehensive verb database with 35+ Finnish verbs
✅ Complete conjugations and examples for all verb types (1-6)
✅ External API integration for translations and lookups
✅ MyMemory Translation API for generating new practice sentences
✅ Wiktionary & Tatoeba integration for external resources
✅ Dynamic sentence generation with loading states
✅ 10,000 Finnish words loaded from GitHub
✅ Dynamic definition and example fetching via APIs
✅ Rank-based difficulty classification (Beginner/Intermediate/Advanced/Expert)
✅ Word caching system for offline access
✅ Progress counter showing current position in word list (1/200)
✅ Background task error fixed - page loads without errors
✅ Word Lookup generalized to support both verbs and nouns with automatic type detection
✅ **Kaikki.org dictionary downloader and SQLite importer** 🆕
✅ **Local database with 100,000+ Finnish words** 🆕
✅ **Offline word lookup with instant query speed** 🆕
✅ **Command-line tool for dictionary management** 🆕