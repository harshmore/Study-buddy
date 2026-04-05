import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from src.generator.question_generator import QuestionGenerator

USAGE_FILE = "usage.json"


def rerun():
    st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)


class QuizManager:

    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []

    def generate_questions(
        self,
        generator: QuestionGenerator,
        context: str,
        question_type: str,
        difficulty: str,
        num_questions: int,
    ):
        self.questions = []
        self.user_answers = []
        self.results = []

        try:
            for _ in range(num_questions):
                if question_type == "Single Choice":
                    question = generator.generate_mcq(
                        context=context, difficulty=difficulty
                    )
                    self.questions.append(
                        {
                            "type": "MCQ",
                            "question": question.question,
                            "options": question.options,
                            "correct_answer": question.correct_answer,
                        }
                    )
                elif question_type == "Multiple Choice":
                    question = generator.generate_multiple_answer(
                        context=context, difficulty=difficulty
                    )
                    self.questions.append(
                        {
                            "type": "Multiple Answer",
                            "question": question.question,
                            "options": question.options,
                            "correct_answer": question.correct_answers,
                        }
                    )
                else:
                    question = generator.generate_fill_blank(
                        context=context, difficulty=difficulty
                    )
                    self.questions.append(
                        {
                            "type": "Fill in the Blank",
                            "question": question.question,
                            "correct_answer": question.answer,
                        }
                    )

        except Exception as e:
            st.error(f"Error generating question {e}")
            return False

        return True

    def attempt_quiz(self):

        if "user_answers" not in st.session_state:
            st.session_state.user_answers = [None] * len(self.questions)

        if "submitted" not in st.session_state:
            st.session_state.submitted = [False] * len(self.questions)

        for i, q in enumerate(self.questions):
            st.markdown(f"**Question {i+1}: {q['question']}**")

            user_answer = None

            if q["type"] == "MCQ":
                user_answer = st.radio(
                    f"Select and answer for Question {i+1}",
                    q["options"],
                    key=f"mcq_{i+1}",
                    index=None,
                )

            elif q["type"] == "Multiple Answer":
                user_answer = st.multiselect(
                    f"Select one or more answers for Question {i+1}",
                    q["options"],
                    key=f"multi_{i+1}",
                )

            else:
                user_answer = st.text_input(
                    f"Fill in the blank for Question {i+1}", key=f"fill_blank_{i}"
                )

            # Disable submit button if already submitted
            if st.session_state.submitted[i]:
                st.success("Answer submitted.")
                st.write(f"Your answer: {st.session_state.user_answers[i]}")
                continue  # Skip showing the submit button again

            submit_button = st.button(
                f"Submit Answer for Question {i+1}", key=f"submit_{i+1}"
            )

            if submit_button:
                st.session_state.user_answers[i] = user_answer
                st.session_state.submitted[i] = True
                st.success("Answer submitted.")

    def evaluate_quiz(self):

        self.results = []
        user_answers = st.session_state.get("user_answers", [])
        if not user_answers or len(user_answers) < len(self.questions):
            st.warning("Please answer all questions before submitting.")
            return

        for i, (q, user_ans) in enumerate(zip(self.questions, user_answers)):
            result_dict = {
                "question_number": i + 1,
                "question": q["question"],
                "question_type": q["type"],
                "user_answer": user_ans,
                "correct_answer": q["correct_answer"],
                "is_correct": False,
            }

            if q["type"] == "MCQ":
                result_dict["options"] = q["options"]
                result_dict["is_correct"] = user_ans == q["correct_answer"]

            elif q["type"] == "Multiple Answer":
                result_dict["options"] = q["options"]
                correct_set = set(q["correct_answer"])
                user_set = set(user_ans)
                result_dict["is_correct"] = user_set == correct_set

            else:
                result_dict["options"] = []
                result_dict["is_correct"] = (
                    user_ans.strip().lower() == q["correct_answer"].strip().lower()
                )

            self.results.append(result_dict)
        if "user_answers" in st.session_state:
            del st.session_state["user_answers"]

        if "submitted" in st.session_state:
            del st.session_state["submitted"]

    def generate_result_dataframe(self):

        if not self.results:
            return pd.DataFrame()

        return pd.DataFrame(self.results)

    def chat_to_context(self, messages):
        lines = []
        for m in messages:
            if m["role"] != "system":
                role = "User" if m["role"] == "user" else "Assistant"
                lines.append(f"{role}: {m['content']}")
        return "\n".join(lines)

    def has_meaningful_chat(self, messages):
        roles = {msg["role"] for msg in messages}
        return "user" in roles and "assistant" in roles

    def save_to_csv(self, filename_prefix="quiz_results"):

        if not self.results:
            st.warning("No results to save!!")
            return None

        df = self.generate_result_dataframe()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{filename_prefix}_{timestamp}.csv"

        os.makedirs("results", exist_ok=True)
        full_path = os.path.join("results", unique_filename)

        try:
            df.to_csv(full_path, index=False)
            st.success("Results saved sucesfully....")
            return full_path

        except Exception as e:
            st.error(f"Failed to save results {e}")
            return None


def check_daily_quota(user_id, has_api_key, limit=5):
    if has_api_key:
        return True

    data = load_usage()
    today = str(datetime.now().date())

    if user_id not in data:
        data[user_id] = {"date": today, "count": 0}

    if data[user_id]["date"] != today:
        data[user_id] = {"date": today, "count": 0}

    if data[user_id]["count"] >= limit:
        return False

    return True


def increment_quota(user_id):
    data = load_usage()
    today = str(datetime.now().date())

    if user_id not in data:
        data[user_id] = {"date": today, "count": 0}

    data[user_id]["count"] += 1

    save_usage(data)


def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {}

    with open(USAGE_FILE, "r") as f:
        return json.load(f)


def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)
