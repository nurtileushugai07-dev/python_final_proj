#  Quiz & Test Prep Platform

A web-based quiz application built with Flask and Python OOP for the Introduction to Programming 2 final project at Astana IT University.

---

##  Project Description

Quiz & Test Prep Platform is a multi-page web application that allows users to take topic-based quizzes, receive instant feedback on their answers, and track their performance history over time. The platform supports two question types - Multiple Choice and True/False - and stores all data in local files (no database required).

---

##  Features

-  **Multiple quizzes** on different topics (Python Basics, Web Development, Data Structures)
-  **Two question types**: Multiple Choice and True/False
-  **Instant results** with a per-question answer review
-  **Dashboard** - full history of all attempts loaded from CSV
-  **Top-5 Leaderboard** - sorted by score using Python's built-in `sorted()`
-  **Exam timer** - countdown per quiz, auto-submits when time runs out
-  **Category filter** - quizzes grouped and filtered by topic on the home page
-  **Admin Panel** - create new quizzes and delete existing ones directly from the browser
-  **File-based persistence** - questions in JSON, results in CSV
-  **Robust error handling** - app never crashes on missing/corrupt files
-  **Clean OOP architecture** - abstract base class + polymorphism

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Flask 2.3+ | Web framework / routing |
| Jinja2 | HTML templating with inheritance |
| JSON | Storing quiz questions |
| CSV | Storing attempt history |
| unittest | Unit testing |
| HTML / CSS | Frontend (custom dark theme, no Bootstrap) |

---

##  Project Structure

```
quiz_platform/
├── app.py                  # Backend: OOP classes + Flask routes
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── data/
│   ├── questions.json      # All quizzes and questions
│   └── results.csv         # History of all attempts (auto-created)
│
├── templates/
│   ├── base.html           # Base template (Jinja2 blocks)
│   ├── index.html          # / - Home page, quiz catalogue
│   ├── quiz.html           # /quiz/<id> - Question form + timer
│   ├── result.html         # /result - Score + detailed answer review
│   ├── dashboard.html      # /dashboard - Leaderboard + attempt history
│   ├── admin.html          # /admin - Admin panel (create/delete quizzes)
│   └── 404.html            # Error page
│
└── tests/
    └── test_quiz.py        # 8 unit tests (unittest)
```

---

##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/nurtileushugai07-dev/python_final_proj
cd python_final_proj
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

##  How to Run

```bash
python app.py
```

Then open your browser and go to: **http://127.0.0.1:5000**

---

##  Running Tests

```bash
python test/test_quiz.py -v
```

Expected output: **8 tests, 0 failures.**

---

##  Application Routes

| Route | Method | Description                                          |
|---|---|------------------------------------------------------|
| `/` | GET | Home page - list of quizzes with category filter     |
| `/quiz/<quiz_id>` | GET / POST | Quiz page - question form with countdown timer       |
| `/result` | GET | Result page - score, grade, detailed answer review   |
| `/dashboard` | GET | Dashboard - Top-5 leaderboard + full history from CSV |
| `/admin` | GET | Admin panel- view all quizzes, create or delete      |
| `/admin/save` | POST | Saves a new quiz to questions.json                   |
| `/admin/delete/<id>` | POST | Deletes a quiz from questions.json                   |

---

## OOP Architecture

```
Question (ABC -
 Abstract Base Class)
├── MultipleChoiceQuestion
│   └── check_answer() - case-insensitive exact match
└── TrueFalseQuestion
    └── check_answer() - normalises True/False/yes/no/1/0

QuizManager
├── load_all_quizzes()   - reads questions.json
├── get_quiz_by_id()     - finds one quiz by ID
├── build_questions()    - factory: creates Question objects
└── calculate_score()    - calls check_answer() polymorphically
```

---

##  Adin Panel

The Admin Panel at `/admin` allows you to manage quizzes directly from the browser without editing any files manually:

- **View** all existing quizzes with question count and timer
- **Create** a new quiz - fill in title, description, category, icon, timer, and add questions dynamically
- **Choose** question type per question (Multiple Choice or True/False)
- **Delete** any existing quiz with one click
- All changes are saved instantly to `data/questions.json`

---

##  Screenshots

![](screen/img.png)

![](screen/img_1.png)
![](screen/img_2.png)
![](screen/img_3.png)
---
---

##  Team Members

| Name | Role |
|---|---|
| Shugay Nurtileu | Full-stack development, OOP design, testing |

---

##  License

This project was created for educational purposes at **Astana IT University**, Department of Software Engineering, ITP2 Final Project 2024.



