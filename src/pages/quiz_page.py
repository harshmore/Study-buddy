import os
import streamlit as st
from src.config.settings import settings
from src.utils.helper_functions import rerun
from src.pages.state import reset_quiz_state
from src.generator.question_generator import QuestionGenerator
from src.rag.pipeline import RAGPipeline


def render_quiz_page():
    st.sidebar.subheader("Quiz Settings")

    prev_mode = st.session_state.quiz_source

    MODE_MAP = {"Topic": "topic", "Chat Conversation": "chat", "File Upload": "file"}

    quiz_mode = st.sidebar.radio(
        "Quiz Source",
        list(MODE_MAP.keys()),
        index=(
            list(MODE_MAP.values()).index(st.session_state.quiz_source)
            if st.session_state.quiz_source in MODE_MAP.values()
            else 0
        ),
    )

    new_mode = MODE_MAP[quiz_mode]

    # new_mode = "chat" if quiz_mode == "Chat Conversation" else "topic"
    if new_mode != prev_mode:
        reset_quiz_state()
        st.session_state.quiz_source = new_mode

    question_type = st.sidebar.selectbox(
        "Select question type",
        ["Single Choice", "Multiple Choice", "Fill in the Blank"],
        index=0,
    )
    if st.session_state.quiz_source == "topic":
        topic = st.sidebar.text_input("Enter topic")

    elif st.session_state.quiz_source == "file":
        uploaded_file = st.sidebar.file_uploader(
            "Upload document", type=["pdf", "txt", "docx"]
        )
        
        if uploaded_file:
            file_id = uploaded_file.name

            if st.session_state.get("last_uploaded_file") != file_id:
                st.session_state.rag.ingest(uploaded_file)
                st.session_state.last_uploaded_file = file_id
                st.success("File processed successfully!")
        

    if st.session_state.quiz_source == "file" and not st.session_state.rag.retriever:
        st.warning("File not processed yet.")
        return

    difficulty = st.sidebar.selectbox(
        "Difficulty level", ["Easy", "Medium", "Hard"], index=1
    )

    num_questions = st.sidebar.number_input(
        "Number of questions", min_value=1, max_value=10, value=5
    )

    llm = st.sidebar.selectbox("Model", settings.MODELS, index=len(settings.MODELS) - 1)

    if st.sidebar.button("Generate Quiz"):
        # st.session_state.quiz_generated = False
        # st.session_state.quiz_submitted = False

        # for k in ("user_answers", "submitted"):
        #     st.session_state.pop(k, None)

        if st.session_state.quiz_source == "topic":
            context = topic

        elif st.session_state.quiz_source == "chat":
            context = st.session_state.quiz_context

        elif st.session_state.quiz_source == "file":
            context = st.session_state.rag.build_quiz_context()

        if st.session_state.quiz_source == "topic" and not topic:
            st.warning("Please enter a topic.")
            return

        if st.session_state.quiz_source == "chat" and not st.session_state.quiz_context:
            st.warning("No chat context available.")
            return

        if st.session_state.quiz_source == "file" and not uploaded_file:
            st.warning("Please upload a file.")
            return

        generator = QuestionGenerator(llm)
        success = st.session_state.quiz_manager.generate_questions(
            generator=generator,
            context=context,
            question_type=question_type,
            difficulty=difficulty,
            num_questions=num_questions,
        )

        st.session_state.quiz_generated = success
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("📋 Quiz")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()

    if st.session_state.quiz_submitted:
        st.header("📊 Results")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = results_df["is_correct"].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100
            st.write(f"Score: {score_percentage}%")

            for _, result in results_df.iterrows():
                question_num = result["question_number"]
                if result["is_correct"]:
                    st.success(f"✅ Question {question_num} : {result['question']}")
                else:
                    st.error(f"❌ Question {question_num} : {result['question']}")
                    st.write(f"Your answer : {result['user_answer']}")
                    st.write(f"Correct answer : {result['correct_answer']}")

                st.markdown("------------")

        if st.button("Save Results"):
            saved_file = st.session_state.quiz_manager.save_to_csv()

            if saved_file:
                with open(saved_file, "rb") as f:
                    st.download_button(
                        label="Downlaod Results",
                        data=f.read(),
                        file_name=os.path.basename(saved_file),
                        mime="text/csv",
                    )
            else:
                st.warning("No results avialble")
