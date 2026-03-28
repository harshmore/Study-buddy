import streamlit as st
from src.utils.helper_functions import QuizManager
from src.rag.pipeline import RAGPipeline


def init_session_state():

    defaults = {
        "page": "quiz",
        "quiz_manager": QuizManager(),
        "quiz_generated": False,
        "quiz_submitted": False,
        "quiz_source": "topic",
        "quiz_context": None,
        "rag": RAGPipeline(),
        "last_uploaded_file": None,
        "chat_sessions": {},
        "active_chat_id": None,
        "rerun_trigger": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quiz_state():
    st.session_state.quiz_generated = False
    st.session_state.quiz_submitted = False

    for k in ("user_answers", "submitted"):
        st.session_state.pop(k, None)

    # # Optional: clear previous questions explicitly
    # st.session_state.quiz_manager.clear()
