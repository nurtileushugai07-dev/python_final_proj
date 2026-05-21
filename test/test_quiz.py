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

    def test_correct_answer(self):
        self.assertTrue(self.q.check_answer("4"))

    def test_wrong_answer(self):
        self.assertFalse(self.q.check_answer("3"))

    def test_case_insensitive(self):
        q2 = MultipleChoiceQuestion(2, "Best language?", ["Python", "Java"], "Python")
        self.assertTrue(q2.check_answer("python"))


class TestTrueFalseQuestion(unittest.TestCase):

    def setUp(self):
        self.q_true  = TrueFalseQuestion(3, "Python is interpreted.", "True")
        self.q_false = TrueFalseQuestion(4, "Python is compiled.",    "False")

    def test_correct_true(self):
        self.assertTrue(self.q_true.check_answer("True"))

    def test_correct_false(self):
        self.assertTrue(self.q_false.check_answer("False"))


class TestQuizManagerScoring(unittest.TestCase):

    def setUp(self):
        self.manager = QuizManager(QUESTIONS_FILE)
        self.quiz_data = {
            "id"       : "test_quiz",
            "title"    : "Test Quiz",
            "questions": [
                {"id": 1, "type": "multiple_choice", "text": "Capital of France?",
                 "options": ["Berlin", "Paris", "Rome"], "correct_answer": "Paris"},
                {"id": 2, "type": "true_false", "text": "The sky is blue.",
                 "correct_answer": "True"},
                {"id": 3, "type": "multiple_choice", "text": "2 + 2 = ?",
                 "options": ["3", "4", "5"], "correct_answer": "4"},
            ]
        }

    def test_perfect_score(self):
        answers = {"q_1": "Paris", "q_2": "True", "q_3": "4"}
        result  = self.manager.calculate_score(self.quiz_data, answers)
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["grade"], "A")

    def test_zero_score(self):
        answers = {"q_1": "Berlin", "q_2": "False", "q_3": "3"}
        result  = self.manager.calculate_score(self.quiz_data, answers)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["grade"], "F")

    def test_grade_boundaries(self):
        g = QuizManager._grade
        self.assertEqual(g(90), "A")
        self.assertEqual(g(80), "B")
        self.assertEqual(g(70), "C")
        self.assertEqual(g(59), "F")


if __name__ == "__main__":
    unittest.main(verbosity=2)
