import reflex as rx
from app.states.state import TranslationState


def grammar_practice_view() -> rx.Component:
    exercise = TranslationState.current_grammar_exercise
    return rx.el.div(
        rx.el.h2(
            "Grammar Practice: Verb Conjugation",
            class_name="text-2xl font-bold text-gray-800 mb-6",
        ),
        rx.el.div(
            rx.cond(
                ~TranslationState.show_grammar_feedback,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Verb:", class_name="text-sm font-medium text-gray-500"
                            ),
                            rx.el.span(
                                exercise["verb"],
                                class_name="px-3 py-1 bg-violet-100 text-violet-700 font-semibold rounded-full",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Type:", class_name="text-sm font-medium text-gray-500"
                            ),
                            rx.el.span(
                                f"Verb Type {exercise['verb_type'].to_string()}",
                                class_name="px-3 py-1 bg-orange-100 text-orange-700 font-semibold rounded-full",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Person:",
                                class_name="text-sm font-medium text-gray-500",
                            ),
                            rx.el.span(
                                exercise["person"],
                                class_name="px-3 py-1 bg-blue-100 text-blue-700 font-semibold rounded-full",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        class_name="flex flex-wrap items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg",
                    ),
                    rx.el.p(
                        exercise["prompt"],
                        class_name="text-2xl font-medium text-center text-gray-700 p-8 bg-white rounded-lg shadow-sm border",
                    ),
                    rx.el.input(
                        placeholder="Type the correct verb form...",
                        on_change=TranslationState.set_user_grammar_answer,
                        default_value=TranslationState.user_grammar_answer,
                        class_name="w-full mt-6 p-4 text-lg border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-colors",
                    ),
                    rx.el.button(
                        "Check Answer",
                        on_click=TranslationState.submit_grammar,
                        class_name="mt-4 w-full py-3 px-8 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200",
                        disabled=TranslationState.user_grammar_answer == "",
                    ),
                    class_name="w-full",
                ),
                rx.el.div(
                    rx.el.h3(
                        rx.cond(
                            TranslationState.grammar_is_correct,
                            "Correct!",
                            "Incorrect!",
                        ),
                        class_name=rx.cond(
                            TranslationState.grammar_is_correct,
                            "text-3xl font-bold text-green-600",
                            "text-3xl font-bold text-red-600",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p("Your answer:", class_name="font-semibold"),
                        rx.el.p(
                            f'"{TranslationState.user_grammar_answer}"',
                            class_name="italic",
                        ),
                        rx.el.p("Correct answer:", class_name="font-semibold mt-2"),
                        rx.el.p(
                            f'''"{exercise["answer"]}"''',
                            class_name="italic text-green-700 font-bold",
                        ),
                        class_name="mt-4 p-4 bg-gray-100 rounded-lg text-center",
                    ),
                    rx.el.button(
                        "Next Exercise",
                        on_click=TranslationState.next_grammar_exercise,
                        class_name="mt-6 w-full py-3 px-6 bg-violet-600 text-white font-semibold rounded-lg shadow-md hover:bg-violet-700 transition-all duration-200",
                    ),
                    class_name="text-center p-8 bg-white rounded-lg shadow-lg w-full",
                ),
            ),
            class_name="max-w-xl mx-auto",
        ),
        class_name="p-4 sm:p-6 md:p-8",
    )