import reflex as rx
from app.states.state import TranslationState


def feedback_card() -> rx.Component:
    def render_word(word: str, index: int) -> rx.Component:
        is_correct = (index < TranslationState.user_translation_words.length()) & (
            word.lower() == TranslationState.user_translation_words[index].lower()
        )
        return rx.el.span(
            word,
            class_name=rx.cond(
                is_correct,
                "text-green-600 font-semibold",
                "text-red-600 font-semibold line-through",
            ),
        )

    return rx.el.div(
        rx.el.h3(
            TranslationState.feedback_message,
            class_name=rx.cond(
                TranslationState.is_correct,
                "text-lg font-bold text-green-700",
                "text-lg font-bold text-red-700",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Your Answer:", class_name="text-sm font-medium text-gray-500 mb-1"
                ),
                rx.el.div(
                    rx.foreach(
                        TranslationState.user_translation_words,
                        lambda word: rx.el.span(word, class_name="mr-1.5"),
                    ),
                    class_name="p-3 bg-gray-50 rounded-md text-gray-800 text-lg",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.p(
                    "Correct Answer:",
                    class_name="text-sm font-medium text-gray-500 mb-1",
                ),
                rx.el.div(
                    rx.foreach(TranslationState.correct_translation_words, render_word),
                    class_name="p-3 bg-green-50 rounded-md text-lg flex flex-wrap gap-1.5",
                ),
            ),
            class_name="mt-4",
        ),
        rx.el.button(
            "Next Sentence",
            rx.icon("arrow-right", class_name="ml-2"),
            on_click=TranslationState.next_sentence,
            class_name="mt-6 w-full flex justify-center items-center py-3 px-4 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-opacity-75 transition-all duration-200",
        ),
        class_name="p-6 bg-white rounded-lg shadow-[0_1px_3px_rgba(0,0,0,0.12)] hover:shadow-[0_8px_16px_rgba(0,0,0,0.2)] transition-shadow duration-300",
    )


def progress_indicator(label: str, value: rx.Var, icon_name: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon_name, class_name="h-6 w-6 text-violet-500"),
            class_name="p-3 bg-violet-100 rounded-lg",
        ),
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value, class_name="text-2xl font-bold text-gray-800"),
        ),
        class_name="flex items-center gap-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200",
    )


def error_analysis_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.h3(
            "Error Analysis",
            class_name="text-lg font-bold text-gray-800 border-b pb-2 mb-4",
        ),
        rx.foreach(
            TranslationState.error_patterns.keys(),
            lambda key: rx.el.div(
                rx.el.span(key, class_name="text-sm font-medium text-gray-600"),
                rx.el.span(
                    TranslationState.error_patterns[key],
                    class_name="text-sm font-bold text-violet-600 bg-violet-100 px-2 py-0.5 rounded-full",
                ),
                class_name="flex justify-between items-center mb-2",
            ),
        ),
        class_name="w-full lg:w-72 bg-white p-4 rounded-lg shadow-[0_1px_3px_rgba(0,0,0,0.12)] h-fit",
    )


def translation_practice_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            progress_indicator("Level", TranslationState.proficiency_level, "award"),
            progress_indicator(
                "Completed", TranslationState.completed_count.to_string(), "check-check"
            ),
            progress_indicator(
                "Accuracy", f"{TranslationState.accuracy}%", "crosshair"
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6",
        ),
        rx.el.div(
            rx.el.button(
                rx.cond(
                    TranslationState.is_generating_sentence,
                    rx.spinner(class_name="h-5 w-5 mr-2"),
                    rx.icon("sparkles", class_name="h-5 w-5 mr-2"),
                ),
                "Generate New Sentence",
                on_click=TranslationState.generate_new_sentence,
                disabled=TranslationState.is_generating_sentence,
                class_name="flex items-center justify-center py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 disabled:bg-blue-300 transition-all duration-200",
            ),
            rx.el.p("Powered by MyMemory", class_name="text-xs text-gray-400"),
            class_name="flex items-center justify-between my-4",
        ),
        rx.el.div(
            rx.el.p(
                f"Level {TranslationState.proficiency_level} Progress",
                class_name="text-sm font-medium text-gray-600 mb-2",
            ),
            rx.el.div(
                rx.el.div(
                    style={"width": f"{TranslationState.level_progress}%"},
                    class_name="bg-violet-600 h-2.5 rounded-full transition-all duration-500",
                ),
                class_name="w-full bg-gray-200 rounded-full h-2.5",
            ),
            class_name="my-6 p-4 bg-white rounded-lg shadow-sm border border-gray-100",
        ),
        rx.el.div(
            rx.el.div(
                rx.cond(
                    ~TranslationState.show_feedback,
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Translate this sentence into Finnish:",
                                class_name="text-md font-medium text-gray-600 mb-4",
                            ),
                            rx.el.p(
                                f'''"{TranslationState.current_sentence["english"]}"''',
                                class_name="text-2xl font-semibold text-gray-800 italic",
                            ),
                            class_name="p-8 bg-white rounded-lg shadow-md border border-gray-100 hover:shadow-lg transition-shadow duration-300 mb-6",
                        ),
                        rx.el.textarea(
                            placeholder="Kirjoita käännöksesi tähän...",
                            on_change=TranslationState.set_user_translation,
                            default_value=TranslationState.user_translation,
                            class_name="w-full p-4 text-lg border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-colors duration-200 min-h-[120px] shadow-sm",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Skip",
                                on_click=TranslationState.skip_sentence,
                                class_name="py-3 px-6 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-all duration-200",
                            ),
                            rx.el.button(
                                "Submit",
                                on_click=TranslationState.submit_translation,
                                class_name="py-3 px-8 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 disabled:opacity-50 transition-all duration-200",
                                disabled=TranslationState.user_translation == "",
                            ),
                            class_name="flex justify-end gap-4 mt-4",
                        ),
                        class_name="w-full",
                    ),
                    feedback_card(),
                ),
                class_name="flex-1 min-w-0",
            ),
            error_analysis_sidebar(),
            class_name="flex flex-col lg:flex-row gap-8",
        ),
        class_name="w-full",
    )