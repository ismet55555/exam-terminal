
#!/usr/bin/env python3

from exam_terminal.ExamTerminal import ExamTerminal


def exam_terminal() -> int:
    """Code here"""

    exam = ExamTerminal()
    menu_result = exam.show_menu()
    if menu_result:
        exam.begin_exam()

        exam.show_result()

        exam.export_results_to_pdf()

    return 0
