import reflex as rx
from app.states.state import TranslationState


def flashcard(word: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        word["category"],
                        class_name="px-2 py-1 text-xs font-semibold tracking-wide text-violet-700 bg-violet-100 rounded-full",
                    ),
                    rx.el.span(
                        word["difficulty"],
                        class_name="px-2 py-1 text-xs font-semibold tracking-wide text-amber-700 bg-amber-100 rounded-full",
                    ),
                    class_name="flex gap-2 mb-4",
                ),
                rx.el.h3(
                    word["finnish"], class_name="text-4xl font-bold text-gray-800"
                ),
                rx.el.p("Click to flip", class_name="text-gray-400 mt-4"),
                class_name="absolute inset-0 w-full h-full flex flex-col items-center justify-center bg-white rounded-lg p-6 [backface-visibility:hidden]",
            ),
            rx.el.div(
                rx.el.h4(
                    word["english"], class_name="text-3xl font-bold text-gray-800"
                ),
                rx.el.div(
                    rx.el.p(
                        "Example (Finnish):",
                        class_name="text-sm font-semibold text-gray-600 mt-6 mb-1",
                    ),
                    rx.el.p(
                        f'''"{word["example_finnish"]}"''',
                        class_name="italic text-gray-700 text-center",
                    ),
                    rx.el.p(
                        "Example (English):",
                        class_name="text-sm font-semibold text-gray-600 mt-4 mb-1",
                    ),
                    rx.el.p(
                        f'''"{word["example_english"]}"''',
                        class_name="italic text-gray-700 text-center",
                    ),
                    class_name="w-full text-center",
                ),
                class_name="absolute inset-0 w-full h-full flex flex-col items-center justify-center bg-white rounded-lg p-6 [transform:rotateY(180deg)] [backface-visibility:hidden]",
            ),
            class_name="relative w-full h-full transition-transform duration-500",
            style={
                "transformStyle": "preserve-3d",
                "transform": rx.cond(
                    TranslationState.vocab_card_flipped,
                    "rotateY(180deg)",
                    "rotateY(0deg)",
                ),
            },
        ),
        class_name="w-full h-72 cursor-pointer",
        style={"perspective": "1000px"},
        on_click=TranslationState.flip_vocab_card,
    )


def flashcards_view() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Flashcards", class_name="text-3xl font-bold text-gray-800 mb-6"),
        rx.el.div(
            flashcard(TranslationState.current_vocab_word),
            class_name="max-w-xl mx-auto",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="h-5 w-5"),
                on_click=TranslationState.prev_vocab_word,
                class_name="p-3 bg-white rounded-full shadow-md hover:bg-gray-100 transition-all",
            ),
            rx.el.p(
                f"{TranslationState.current_vocab_index + 1} / {TranslationState.vocab_words.length()}",
                class_name="font-semibold text-gray-700",
            ),
            rx.el.button(
                rx.icon("arrow-right", class_name="h-5 w-5"),
                on_click=TranslationState.next_vocab_word,
                class_name="p-3 bg-white rounded-full shadow-md hover:bg-gray-100 transition-all",
            ),
            class_name="flex items-center justify-between mt-8 w-full max-w-xl mx-auto",
        ),
        class_name="p-4 sm:p-6 md:p-8",
    )