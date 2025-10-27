import reflex as rx
from app.states.state import TranslationState


def option_button(option: str) -> rx.Component:
    is_selected = TranslationState.selected_option == option
    return rx.el.button(
        option,
        on_click=lambda: TranslationState.select_answer(option),
        class_name=rx.cond(
            is_selected,
            "w-full p-4 text-left text-lg font-semibold border-2 border-violet-600 bg-violet-100 text-violet-800 rounded-lg shadow-inner transition-all duration-200",
            "w-full p-4 text-left text-lg font-medium border border-gray-300 bg-white hover:bg-gray-50 rounded-lg transition-all duration-200",
        ),
        disabled=TranslationState.show_question_feedback,
    )


def question_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            progress_indicator(
                "Questions Answered",
                TranslationState.question_completed_count.to_string(),
                "circle_plus",
            ),
            progress_indicator(
                "Question Accuracy", f"{TranslationState.question_accuracy}%", "target"
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8",
        ),
        rx.cond(
            ~TranslationState.show_question_feedback,
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Question:", class_name="text-md font-medium text-gray-600 mb-2"
                    ),
                    rx.el.h2(
                        TranslationState.current_question["question"],
                        class_name="text-3xl font-bold text-gray-800",
                    ),
                    class_name="mb-8 p-6 bg-white rounded-lg shadow-md",
                ),
                rx.el.div(
                    rx.foreach(
                        TranslationState.current_question["options"], option_button
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
                ),
                rx.el.button(
                    "Submit Answer",
                    on_click=TranslationState.submit_question,
                    class_name="mt-8 w-full py-3 px-8 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200",
                    disabled=TranslationState.selected_option.to(bool).__invert__(),
                ),
                class_name="w-full max-w-2xl mx-auto",
            ),
            rx.el.div(
                rx.el.h3(
                    TranslationState.question_feedback,
                    class_name=rx.cond(
                        TranslationState.question_feedback == "Correct!",
                        "text-2xl font-bold text-green-600",
                        "text-2xl font-bold text-red-600",
                    ),
                ),
                rx.el.button(
                    "Next Question",
                    on_click=TranslationState.next_question,
                    class_name="mt-6 py-3 px-6 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 transition-all duration-200",
                ),
                class_name="text-center p-8 bg-white rounded-lg shadow-lg",
            ),
        ),
        class_name="p-4 sm:p-6 md:p-8",
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