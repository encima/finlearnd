import reflex as rx
from app.states.state import TranslationState


def stat_card(label: str, value: rx.Var, icon: str, color_class: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-6 w-6 {color_class}"),
            class_name=f"p-3 rounded-lg {color_class.replace('text', 'bg').replace('-600', '-100')}",
        ),
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value, class_name="text-2xl font-bold text-gray-800"),
        ),
        class_name="flex items-center gap-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200",
    )


def progress_dashboard_view() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Progress Dashboard", class_name="text-3xl font-bold text-gray-800 mb-6"
        ),
        rx.el.div(
            stat_card(
                "Proficiency Level",
                TranslationState.proficiency_level,
                "award",
                "text-yellow-600",
            ),
            stat_card(
                "Overall Accuracy",
                f"{TranslationState.overall_accuracy}%",
                "target",
                "text-green-600",
            ),
            stat_card(
                "Total Sessions",
                TranslationState.total_sessions.to_string(),
                "activity",
                "text-blue-600",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Performance Breakdown",
                        class_name="text-xl font-semibold text-gray-700 mb-4",
                    ),
                    rx.el.div(
                        rx.recharts.bar_chart(
                            rx.recharts.x_axis(
                                data_key="name",
                                stroke="#888888",
                                font_size=12,
                                tick_line=False,
                                axis_line=False,
                            ),
                            rx.recharts.y_axis(
                                stroke="#888888",
                                font_size=12,
                                tick_line=False,
                                axis_line=False,
                                allow_decimals=False,
                                domain=[0, 100],
                            ),
                            rx.recharts.bar(
                                data_key="accuracy", fill="#8884d8", radius=[4, 4, 0, 0]
                            ),
                            rx.recharts.tooltip(),
                            data=TranslationState.performance_data,
                            height=300,
                            class_name="w-full",
                        ),
                        class_name="p-4 bg-white rounded-lg shadow-sm border",
                    ),
                    class_name="mb-8",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Recommended Focus",
                        class_name="text-xl font-semibold text-gray-700 mb-4",
                    ),
                    rx.el.div(
                        rx.foreach(
                            TranslationState.weakest_areas,
                            lambda area: rx.el.div(
                                rx.icon(
                                    "flag_triangle_right",
                                    class_name="h-5 w-5 text-yellow-500",
                                ),
                                rx.el.p(
                                    f"Focus on {area[0]}", class_name="font-medium"
                                ),
                                rx.el.span(
                                    f"{area[1]} mistakes",
                                    class_name="text-sm text-gray-500",
                                ),
                                class_name="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm border",
                            ),
                        ),
                        class_name="space-y-3",
                    ),
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.h3(
                    "Error Patterns",
                    class_name="text-xl font-semibold text-gray-700 mb-4",
                ),
                rx.el.div(
                    rx.recharts.pie_chart(
                        rx.recharts.pie(
                            data=TranslationState.error_patterns_data,
                            data_key="value",
                            name_key="name",
                            cx="50%",
                            cy="50%",
                            outer_radius=80,
                            fill="#8884d8",
                            label=True,
                            stroke="#fff",
                            stroke_width=2,
                        ),
                        rx.recharts.tooltip(),
                        width="100%",
                        height=280,
                    ),
                    class_name="flex justify-center p-4 bg-white rounded-lg shadow-sm border mb-8",
                ),
                class_name="w-full lg:w-80",
            ),
            class_name="flex flex-col lg:flex-row gap-8",
        ),
        class_name="p-4 sm:p-6 md:p-8",
    )