import json
import csv
import os
from abc import ABC, abstractmethod
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR       = os.path.join(BASE_DIR, "data")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
RESULTS_FILE   = os.path.join(DATA_DIR, "results.csv")
CSV_HEADERS    = ["username", "quiz_id", "quiz_title",
                  "score", "total", "percentage", "date"]

app = Flask(__name__)
app.secret_key = "quiz_platform_secret_key_2024"  # Needed for session


class Question(ABC):

    def __init__(self, question_id: int, text: str, correct_answer: str):
        self.id             = question_id
        self.text           = text
        self.correct_answer = correct_answer

    @abstractmethod
    def check_answer(self, user_answer: str) -> bool:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class MultipleChoiceQuestion(Question):

    def __init__(self, question_id: int, text: str,
                 options: list, correct_answer: str):
        super().__init__(question_id, text, correct_answer)
        self.options = options

    def check_answer(self, user_answer: str) -> bool:
        return user_answer.strip().lower() == self.correct_answer.strip().lower()

    def get_type(self) -> str:
        return "Multiple Choice"


class TrueFalseQuestion(Question):

    TRUTHY  = {"true",  "yes", "1", "t", "y"}
    FALSY   = {"false", "no",  "0", "f", "n"}

    def check_answer(self, user_answer: str) -> bool:
        user_norm    = user_answer.strip().lower()
        correct_norm = self.correct_answer.strip().lower()

        user_bool    = user_norm    in self.TRUTHY
        correct_bool = correct_norm in self.TRUTHY
        return user_bool == correct_bool

    def get_type(self) -> str:
        return "True / False"


class QuizManager:

    def __init__(self, questions_file: str):
        self.questions_file = questions_file

    def load_all_quizzes(self) -> list:
        try:
            with open(self.questions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("quizzes", [])
        except FileNotFoundError:
            print(f"[QuizManager] ERROR: {self.questions_file} not found.")
            return []
        except json.JSONDecodeError as e:
            print(f"[QuizManager] ERROR: Malformed JSON — {e}")
            return []

    def get_quiz_by_id(self, quiz_id: str) -> dict | None:
        for quiz in self.load_all_quizzes():
            if quiz["id"] == quiz_id:
                return quiz
        return None

    def build_questions(self, quiz_data: dict) -> list:
        objects = []
        for q in quiz_data.get("questions", []):
            q_type = q.get("type", "multiple_choice")
            if q_type == "true_false":
                obj = TrueFalseQuestion(
                    question_id    = q["id"],
                    text           = q["text"],
                    correct_answer = q["correct_answer"]
                )
            else:
                obj = MultipleChoiceQuestion(
                    question_id    = q["id"],
                    text           = q["text"],
                    options        = q.get("options", []),
                    correct_answer = q["correct_answer"]
                )
            objects.append(obj)
        return objects

    def calculate_score(self, quiz_data: dict,
                        user_answers: dict) -> dict:
        questions   = self.build_questions(quiz_data)
        results     = []
        correct_cnt = 0

        for q in questions:
            key         = f"q_{q.id}"
            user_ans    = user_answers.get(key, "").strip()
            is_correct  = q.check_answer(user_ans) if user_ans else False

            if is_correct:
                correct_cnt += 1

            results.append({
                "id"             : q.id,
                "text"           : q.text,
                "type"           : q.get_type(),
                "user_answer"    : user_ans if user_ans else "(no answer)",
                "correct_answer" : q.correct_answer,
                "is_correct"     : is_correct,
                "options"        : getattr(q, "options", [])
            })

        total      = len(questions)
        percentage = round((correct_cnt / total) * 100) if total else 0

        return {
            "score"      : correct_cnt,
            "total"      : total,
            "percentage" : percentage,
            "results"    : results,
            "grade"      : self._grade(percentage)
        }

    @staticmethod
    def _grade(percentage: int) -> str:
        if percentage >= 90: return "A"
        if percentage >= 80: return "B"
        if percentage >= 70: return "C"
        if percentage >= 60: return "D"
        return "F"

def save_result_to_csv(username: str, quiz_id: str,
                       quiz_title: str, score: int,
                       total: int, percentage: int) -> None:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        file_exists = os.path.isfile(RESULTS_FILE)

        with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "username"  : username,
                "quiz_id"   : quiz_id,
                "quiz_title": quiz_title,
                "score"     : score,
                "total"     : total,
                "percentage": percentage,
                "date"      : datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    except PermissionError:
        print("[save_result] ERROR: No write permission for results.csv")
    except OSError as e:
        print(f"[save_result] ERROR: {e}")


def load_results_from_csv() -> list:
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            reader  = csv.DictReader(f)
            results = list(reader)
        return results
    except FileNotFoundError:
        return []
    except csv.Error as e:
        print(f"[load_results] ERROR: Corrupt CSV — {e}")
        return []

manager = QuizManager(QUESTIONS_FILE)


@app.route("/")
def index():
    quizzes = manager.load_all_quizzes()
    return render_template("index.html", quizzes=quizzes)


@app.route("/quiz/<quiz_id>", methods=["GET", "POST"])
def quiz(quiz_id):
    quiz_data = manager.get_quiz_by_id(quiz_id)
    if not quiz_data:
        return render_template("404.html"), 404

    if request.method == "POST":
        session["user_answers"] = dict(request.form)
        session["quiz_id"]      = quiz_id
        return redirect(url_for("result"))

    questions = manager.build_questions(quiz_data)
    return render_template("quiz.html", quiz=quiz_data, questions=questions)


@app.route("/result", methods=["GET", "POST"])
def result():
    quiz_id      = session.get("quiz_id")
    user_answers = session.get("user_answers", {})

    if not quiz_id:
        return redirect(url_for("index"))

    quiz_data = manager.get_quiz_by_id(quiz_id)
    if not quiz_data:
        return redirect(url_for("index"))

    flat_answers = {k: (v[0] if isinstance(v, list) else v)
                    for k, v in user_answers.items()}

    username = flat_answers.pop("username", "Anonymous")
    score_data = manager.calculate_score(quiz_data, flat_answers)

    # Persist to CSV
    save_result_to_csv(
        username   = username,
        quiz_id    = quiz_id,
        quiz_title = quiz_data["title"],
        score      = score_data["score"],
        total      = score_data["total"],
        percentage = score_data["percentage"]
    )

    # Clear session after use
    session.pop("user_answers", None)
    session.pop("quiz_id", None)

    return render_template(
        "result.html",
        quiz       = quiz_data,
        username   = username,
        score_data = score_data
    )

@app.route("/dashboard")
def dashboard():
    all_results = load_results_from_csv()

    leaderboard = sorted(
        all_results,
        key=lambda r: (int(r.get("percentage", 0)), int(r.get("score", 0))),
        reverse=True
    )[:5]

    history = list(reversed(all_results))

    return render_template("dashboard.html", results=history, leaderboard=leaderboard)

if __name__ == "__main__":
    app.run(debug=True)
