
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import (
    MultipleChoiceQuestion,
    TrueFalseQuestion,
    QuizManager,
    QUESTIONS_FILE,
)

class TestMultipleChoiceQuestion(unittest.TestCase):

    def setUp(self):
        self.q = MultipleChoiceQuestion(
            question_id    = 1,
            text           = "What is 2 + 2?",
            options        = ["3", "4", "5", "6"],
            correct_answer = "4"
        )

    def test_correct_exact_match(self):
        self.assertTrue(self.q.check_answer("4"))

    def test_correct_case_insensitive(self):
        q2 = MultipleChoiceQuestion(
            question_id    = 2,
            text           = "Best language?",
            options        = ["Python", "Java"],
            correct_answer = "Python"
        )
        self.assertTrue(q2.check_answer("python"))
        self.assertTrue(q2.check_answer("PYTHON"))
        self.assertTrue(q2.check_answer("Python"))

    def test_correct_strips_whitespace(self):
        self.assertTrue(self.q.check_answer("  4  "))

    def test_wrong_answer_returns_false(self):
        self.assertFalse(self.q.check_answer("3"))
        self.assertFalse(self.q.check_answer("5"))

    def test_empty_answer_returns_false(self):
        self.assertFalse(self.q.check_answer(""))

    def test_get_type_label(self):
        self.assertEqual(self.q.get_type(), "Multiple Choice")

class TestTrueFalseQuestion(unittest.TestCase):

    def setUp(self):
        self.q_true  = TrueFalseQuestion(3, "Python is interpreted.", "True")
        self.q_false = TrueFalseQuestion(4, "Python is compiled.",    "False")

    def test_true_exact(self):
        self.assertTrue(self.q_true.check_answer("True"))

    def test_true_lowercase(self):
        self.assertTrue(self.q_true.check_answer("true"))

    def test_true_short_form(self):
        self.assertTrue(self.q_true.check_answer("t"))
        self.assertTrue(self.q_true.check_answer("yes"))

    def test_false_exact(self):
        self.assertTrue(self.q_false.check_answer("False"))

    def test_false_lowercase(self):
        self.assertTrue(self.q_false.check_answer("false"))

    def test_wrong_answer(self):
        """Submitting 'True' when correct is 'False' must return False."""
        self.assertFalse(self.q_false.check_answer("True"))

    def test_get_type_label(self):
        self.assertEqual(self.q_true.get_type(), "True / False")


class TestQuizManagerScoring(unittest.TestCase):

    def setUp(self):
        self.manager = QuizManager(QUESTIONS_FILE)

        self.quiz_data = {
            "id"       : "test_quiz",
            "title"    : "Test Quiz",
            "questions": [
                {
                    "id"            : 1,
                    "type"          : "multiple_choice",
                    "text"          : "Capital of France?",
                    "options"       : ["Berlin", "Paris", "Rome"],
                    "correct_answer": "Paris"
                },
                {
                    "id"            : 2,
                    "type"          : "true_false",
                    "text"          : "The sky is blue.",
                    "correct_answer": "True"
                },
                {
                    "id"            : 3,
                    "type"          : "multiple_choice",
                    "text"          : "2 + 2 = ?",
                    "options"       : ["3", "4", "5"],
                    "correct_answer": "4"
                }
            ]
        }


    def test_perfect_score(self):
        answers = {"q_1": "Paris", "q_2": "True", "q_3": "4"}
        result  = self.manager.calculate_score(self.quiz_data, answers)

        self.assertEqual(result["score"],      3)
        self.assertEqual(result["total"],      3)
        self.assertEqual(result["percentage"], 100)
        self.assertEqual(result["grade"],      "A")


    def test_zero_score(self):
        answers = {"q_1": "Berlin", "q_2": "False", "q_3": "3"}
        result  = self.manager.calculate_score(self.quiz_data, answers)

        self.assertEqual(result["score"], 0)
        self.assertEqual(result["percentage"], 0)
        self.assertEqual(result["grade"], "F")


    def test_partial_score(self):
        answers = {"q_1": "Paris", "q_2": "False", "q_3": "3"}
        result  = self.manager.calculate_score(self.quiz_data, answers)

        self.assertEqual(result["score"], 1)
        self.assertEqual(result["total"], 3)
        # 1/3 = 33%
        self.assertEqual(result["percentage"], 33)


    def test_missing_answer_counts_as_wrong(self):
        answers = {"q_1": "Paris"}   # q_2 and q_3 not submitted
        result  = self.manager.calculate_score(self.quiz_data, answers)

        self.assertEqual(result["score"], 1)
        self.assertEqual(result["total"], 3)


    def test_result_contains_all_questions(self):
        answers = {"q_1": "Paris", "q_2": "True", "q_3": "4"}
        result  = self.manager.calculate_score(self.quiz_data, answers)

        self.assertEqual(len(result["results"]), 3)

    def test_each_result_has_required_keys(self):
        required_keys = {"id", "text", "type", "user_answer",
                         "correct_answer", "is_correct", "options"}
        answers = {"q_1": "Paris", "q_2": "True", "q_3": "4"}
        result  = self.manager.calculate_score(self.quiz_data, answers)

        for item in result["results"]:
            self.assertTrue(required_keys.issubset(item.keys()),
                            f"Missing keys in result item: {item}")


    def test_grade_boundaries(self):
        g = QuizManager._grade
        self.assertEqual(g(95),  "A")
        self.assertEqual(g(90),  "A")
        self.assertEqual(g(89),  "B")
        self.assertEqual(g(80),  "B")
        self.assertEqual(g(79),  "C")
        self.assertEqual(g(70),  "C")
        self.assertEqual(g(69),  "D")
        self.assertEqual(g(60),  "D")
        self.assertEqual(g(59),  "F")
        self.assertEqual(g(0),   "F")


if __name__ == "__main__":
    unittest.main(verbosity=2)
