        results[index] = {
            "label": "Incorrect:",
            "text": f"{100 - self.exam_contents['exam']['evaluation_percent']:3.1f}% ({self.exam_contents['exam']['exam_questions_count'] - self.questions_correct} of {self.exam_contents['exam']['exam_questions_count']})",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        answer_distribution = ""
        for question in self.exam_contents['questions']:
            if question['answered']:
                if question['answered_correctly']:
                    answer_distribution += ' +'
                else:
                    answer_distribution += ' -'
        results[index] = {
            "label": "Answers Per Question:",
            "text": f"[First]{answer_distribution} [Last]",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 2
        }
        index += 1