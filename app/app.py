import reflex as rx
from app.states.state import TranslationState
from app.components.sidebar import sidebar
from app.components.translation import translation_practice_view
from app.components.question import question_view
from app.components.vocabulary import vocabulary_builder_view
from app.components.flashcards import flashcards_view
from app.components.grammar import grammar_practice_view
from app.components.dashboard import progress_dashboard_view
from app.components.word_lookup import word_lookup_view


def main_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.button(
                    rx.icon("menu", class_name="h-6 w-6"),
                    on_click=TranslationState.toggle_drawer,
                    class_name="md:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100",
                ),
                rx.el.h1(
                    "Finnish Learning", class_name="text-2xl font-bold text-gray-800"
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="sticky top-0 z-10 flex items-center justify-between h-16 px-6 bg-white/80 backdrop-blur-sm border-b",
        ),
        rx.el.div(
            rx.match(
                TranslationState.current_page,
                ("Translation Practice", translation_practice_view()),
                ("Question Mode", question_view()),
                ("Vocabulary Builder", vocabulary_builder_view()),
                ("Grammar Practice", grammar_practice_view()),
                ("Flashcards", flashcards_view()),
                ("Progress Dashboard", progress_dashboard_view()),
                ("Word Lookup", word_lookup_view()),
                rx.el.div("Select a mode to begin."),
            ),
            class_name="p-4 sm:p-6 md:p-8 w-full",
        ),
        class_name="flex-1 flex flex-col h-screen overflow-y-auto",
    )


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            main_content(),
            class_name=rx.cond(
                TranslationState.drawer_open,
                "transition-all duration-300 md:ml-64 flex-1",
                "transition-all duration-300 flex-1 w-full",
            ),
        ),
        class_name="flex min-h-screen w-full bg-gray-50 font-['Lato']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=TranslationState.on_load)