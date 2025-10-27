import reflex as rx
from app.states.state import TranslationState


def nav_item(icon: str, text: str, is_active: bool) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-5 w-5 mr-3"),
        rx.el.span(text),
        on_click=lambda: TranslationState.set_page(text),
        class_name=rx.cond(
            is_active,
            "w-full flex items-center p-3 rounded-lg text-sm font-semibold bg-violet-100 text-violet-700 transition-colors duration-200",
            "w-full flex items-center p-3 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200",
        ),
    )


def sidebar() -> rx.Component:
    nav_items = [
        {"icon": "file-text", "text": "Translation Practice"},
        {"icon": "help-circle", "text": "Question Mode"},
        {"icon": "book-open", "text": "Vocabulary Builder"},
        {"icon": "spell-check", "text": "Grammar Practice"},
        {"icon": "copy", "text": "Flashcards"},
        {"icon": "bar-chart-2", "text": "Progress Dashboard"},
        {"icon": "search", "text": "Word Lookup"},
    ]
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("languages", class_name="h-6 w-6 text-violet-600"),
                rx.el.span("SuomiLearn", class_name="text-lg font-bold text-gray-800"),
                class_name="flex items-center gap-3 h-16 px-4 border-b border-gray-200",
            ),
            rx.el.nav(
                rx.foreach(
                    nav_items,
                    lambda item: nav_item(
                        item["icon"],
                        item["text"],
                        TranslationState.current_page == item["text"],
                    ),
                ),
                class_name="flex flex-col gap-2 p-4",
            ),
            class_name="flex flex-col h-full bg-white border-r border-gray-200",
        ),
        class_name=rx.cond(
            TranslationState.drawer_open,
            "fixed inset-y-0 left-0 z-20 w-64 transform-none transition-transform duration-300 ease-in-out md:relative",
            "fixed inset-y-0 left-0 z-20 w-64 -translate-x-full transition-transform duration-300 ease-in-out md:relative md:translate-x-0",
        ),
    )