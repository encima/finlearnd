import reflex as rx
from app.states.state import TranslationState


def word_lookup_view() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Word Lookup", class_name="text-3xl font-bold text-gray-800 mb-6"),
        rx.el.p(
            "Look up conjugations for verbs or declensions for nouns. Data is fetched live from Wiktionary.",
            class_name="text-center text-gray-600 mb-8 max-w-2xl mx-auto",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.input(
                    name="query",
                    placeholder="E.g., 'puhua', 'talo', 'kissa'...",
                    default_value=TranslationState.word_search_query,
                    class_name="w-full p-4 text-lg border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-colors",
                ),
                rx.el.button(
                    rx.cond(
                        TranslationState.is_searching_word,
                        rx.spinner(class_name="h-5 w-5"),
                        rx.icon("search", class_name="h-5 w-5"),
                    ),
                    type="submit",
                    disabled=TranslationState.is_searching_word,
                    class_name="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-violet-600 text-white rounded-md hover:bg-violet-700 disabled:bg-violet-300",
                ),
                class_name="relative w-full max-w-md mx-auto",
            ),
            on_submit=lambda form_data: TranslationState.search_word(
                form_data.to(dict)["query"]
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.match(
                TranslationState.searched_word_result["type"],
                ("verb", conjugation_table(TranslationState.searched_word_result)),
                ("noun", declension_table(TranslationState.searched_word_result)),
                no_results_found(),
            ),
            class_name="max-w-4xl mx-auto",
        ),
        class_name="p-4 sm:p-6 md:p-8",
    )


def conjugation_table(word: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    word["infinitive"].to(str).capitalize(),
                    class_name="text-2xl font-bold text-gray-800",
                ),
                rx.el.span(
                    f"Verb Type {word['verb_type'].to_string()}",
                    class_name="px-3 py-1 bg-orange-100 text-orange-700 font-semibold rounded-full",
                ),
                class_name="flex items-center gap-4",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add to Flashcards",
                    on_click=lambda: TranslationState.add_word_to_flashcards(word),
                    class_name="flex items-center py-2 px-4 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 transition-all duration-200",
                ),
                rx.el.a(
                    rx.icon("book-open-check", class_name="h-4 w-4 mr-2"),
                    "Wiktionary",
                    href=f"https://en.wiktionary.org/wiki/{word['infinitive'].to_string()}#Finnish",
                    is_external=True,
                    class_name="flex items-center py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-all duration-200",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex justify-between items-center mb-6 p-4 bg-white rounded-lg shadow-sm border",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Person",
                            class_name="py-3 px-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Conjugation",
                            class_name="py-3 px-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider",
                        ),
                        class_name="bg-gray-50 border-b-2 border-gray-200",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        word["conjugations"].keys(),
                        lambda person: rx.el.tr(
                            rx.el.td(
                                person, class_name="py-4 px-4 border-b border-gray-200"
                            ),
                            rx.el.td(
                                word["conjugations"][person],
                                class_name="py-4 px-4 font-mono text-violet-700 border-b border-gray-200",
                            ),
                            class_name="hover:bg-gray-50",
                        ),
                    )
                ),
                class_name="min-w-full bg-white rounded-lg overflow-hidden shadow-sm",
            ),
            class_name="overflow-x-auto",
        ),
    )


def declension_table(word: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    word["word"].to(str).capitalize(),
                    class_name="text-2xl font-bold text-gray-800",
                ),
                rx.el.span(
                    "Noun",
                    class_name="px-3 py-1 bg-green-100 text-green-700 font-semibold rounded-full",
                ),
                class_name="flex items-center gap-4",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add to Flashcards",
                    on_click=lambda: TranslationState.add_word_to_flashcards(word),
                    class_name="flex items-center py-2 px-4 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 transition-all duration-200",
                ),
                rx.el.a(
                    rx.icon("book-open-check", class_name="h-4 w-4 mr-2"),
                    "Wiktionary",
                    href=f"https://en.wiktionary.org/wiki/{word['word'].to_string()}#Finnish",
                    is_external=True,
                    class_name="flex items-center py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-all duration-200",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex justify-between items-center mb-6 p-4 bg-white rounded-lg shadow-sm border",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Case",
                            class_name="py-3 px-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Singular",
                            class_name="py-3 px-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Plural",
                            class_name="py-3 px-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider",
                        ),
                        class_name="bg-gray-50 border-b-2 border-gray-200",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        word["declensions"].keys(),
                        lambda case: rx.el.tr(
                            rx.el.td(
                                case,
                                class_name="py-4 px-4 border-b border-gray-200 capitalize",
                            ),
                            rx.el.td(
                                word["declensions"][case]["singular"],
                                class_name="py-4 px-4 font-mono text-violet-700 border-b border-gray-200",
                            ),
                            rx.el.td(
                                word["declensions"][case]["plural"],
                                class_name="py-4 px-4 font-mono text-violet-700 border-b border-gray-200",
                            ),
                            class_name="hover:bg-gray-50",
                        ),
                    )
                ),
                class_name="min-w-full bg-white rounded-lg overflow-hidden shadow-sm",
            ),
            class_name="overflow-x-auto",
        ),
    )


def no_results_found() -> rx.Component:
    return rx.el.div(
        rx.cond(
            TranslationState.is_searching_word,
            rx.el.div(
                rx.spinner(class_name="h-12 w-12 text-violet-500"),
                rx.el.h3(
                    f'Searching for "{TranslationState.word_search_query}"...',
                    class_name="text-xl font-semibold text-gray-600 mt-4",
                ),
                class_name="text-center p-8 bg-gray-50 rounded-lg border-2 border-dashed",
            ),
            rx.cond(
                TranslationState.word_search_query != "",
                rx.el.div(
                    rx.icon("search-slash", class_name="h-12 w-12 text-gray-400 mb-4"),
                    rx.el.h3(
                        "No Results Found",
                        class_name="text-xl font-semibold text-gray-600",
                    ),
                    rx.el.p(
                        f'Could not find the word "{TranslationState.word_search_query}".',
                        class_name="text-gray-500 mt-1",
                    ),
                    rx.el.p(
                        "Please check the spelling or try another word.",
                        class_name="text-sm text-gray-400 mt-1",
                    ),
                    class_name="text-center p-8 bg-gray-50 rounded-lg border-2 border-dashed",
                ),
                rx.el.div(
                    rx.icon("languages", class_name="h-12 w-12 text-gray-400 mb-4"),
                    rx.el.h3(
                        "Search for a Word",
                        class_name="text-xl font-semibold text-gray-600",
                    ),
                    rx.el.p(
                        "Type a Finnish verb or noun in the search bar.",
                        class_name="text-gray-500 mt-1",
                    ),
                    class_name="text-center p-8 bg-gray-50 rounded-lg border-2 border-dashed",
                ),
            ),
        )
    )