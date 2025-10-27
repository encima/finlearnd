import reflex as rx
from app.states.state import TranslationState


def vocab_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                ~TranslationState.vocab_card_flipped,
                rx.el.div(
                    rx.el.p(
                        TranslationState.current_vocab_word["category"],
                        class_name="text-sm font-medium text-violet-600 uppercase tracking-wider",
                    ),
                    rx.el.h2(
                        TranslationState.current_vocab_word["finnish"],
                        class_name="text-5xl font-bold text-gray-800 my-8",
                    ),
                    rx.el.p("Click to flip", class_name="text-gray-500"),
                    class_name="flex flex-col items-center justify-center text-center p-6 h-full [backface-visibility:hidden]",
                ),
                rx.el.div(
                    rx.el.h3(
                        TranslationState.current_vocab_word["english"],
                        class_name="text-3xl font-bold text-gray-800",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Example (Finnish):",
                            class_name="text-sm font-semibold text-gray-600 mt-6 mb-1",
                        ),
                        rx.el.p(
                            f'''"{TranslationState.current_vocab_word["example_finnish"]}"''',
                            class_name="italic text-gray-700",
                        ),
                        rx.el.p(
                            "Example (English):",
                            class_name="text-sm font-semibold text-gray-600 mt-4 mb-1",
                        ),
                        rx.el.p(
                            f'''"{TranslationState.current_vocab_word["example_english"]}"''',
                            class_name="italic text-gray-700",
                        ),
                        class_name="w-full text-left",
                    ),
                    class_name="flex flex-col items-center justify-center p-6 h-full text-center [transform:rotateY(180deg)] [backface-visibility:hidden]",
                ),
            ),
            class_name="relative w-full h-72 bg-white rounded-lg shadow-lg border border-gray-200 cursor-pointer transition-transform duration-500",
            style={
                "transformStyle": "preserve-3d",
                "transform": rx.cond(
                    TranslationState.vocab_card_flipped,
                    "rotateY(180deg)",
                    "rotateY(0deg)",
                ),
            },
            on_click=TranslationState.flip_vocab_card,
        ),
        class_name="w-full max-w-lg mx-auto",
        style={"perspective": "1000px"},
    )


def vocabulary_builder_view() -> rx.Component:
    return rx.el.div(
        vocab_card(),
        rx.el.div(
            rx.el.a(
                rx.icon("search", class_name="h-4 w-4 mr-2"),
                "Look up definition",
                href=f"https://en.wiktionary.org/wiki/{TranslationState.current_vocab_word['finnish']}#Finnish",
                is_external=True,
                class_name="flex items-center py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-all duration-200 text-sm",
            ),
            class_name="flex justify-center mt-4",
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
            class_name="flex items-center justify-between mt-8 w-full max-w-lg mx-auto",
        ),
        class_name="p-4 sm:p-6 md:p-8",
    )