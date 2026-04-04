from langchain_core.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    input_variables=["context", "difficulty"],
    template=(
        "You are an expert quiz generator.\n\n"
        "Your task is to generate a HIGH-QUALITY {difficulty} multiple-choice question.\n\n"
        "Context (source of truth):\n"
        "{context}\n\n"
        "STRICT INSTRUCTIONS:\n"
        "- Use ONLY the provided context as the knowledge source\n"
        "- Do NOT introduce external facts\n"
        "- If context is limited, use your own knowledge and generalize carefully without hallucinating\n"
        "- Avoid trivial definition-based questions\n"
        "- Prefer deeper reasoning:\n"
        "  • application\n"
        "  • comparison\n"
        "  • cause-effect\n"
        "  • scenario-based reasoning\n"
        "  • misconception detection\n\n"
        "QUALITY RULES:\n"
        "- Exactly 4 options\n"
        "- Only ONE correct answer\n"
        "- Distractors must be plausible\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question'\n"
        "- 'options' (exactly 4)\n"
        "- 'correct_answer'\n\n"
        "Example:\n"
        "{{\n"
        '  "question": "What is the capital of France?",\n'
        '  "options": ["London", "Berlin", "Paris", "Madrid"],\n'
        '  "correct_answer": "Paris"\n'
        "}}\n\n"
        "Your response:"
    ),
)


fill_blank_prompt_template = PromptTemplate(
    input_variables=["context", "difficulty"],
    template=(
        "You are an expert quiz generator.\n\n"
        "Generate a {difficulty} fill-in-the-blank question.\n\n"
        "Context (source of truth):\n"
        "{context}\n\n"
        "RULES:\n"
        "- Use ONLY the context\n"
        "- Use '____' for the blank\n"
        "- Test understanding, not memorization\n"
        "- If context is small, use your own knowledge and infer carefully without hallucinating\n\n"
        "Return ONLY a JSON object with:\n"
        "- 'question'\n"
        "- 'answer'\n\n"
        "Example:\n"
        "{{\n"
        '  "question": "The capital of France is ____.",\n'
        '  "answer": "Paris"\n'
        "}}\n\n"
        "Your response:"
    ),
)

multiple_answer_prompt_template = PromptTemplate(
    input_variables=["context", "difficulty"],
    template=(
        "You are an expert quiz generator.\n\n"
        "Generate a {difficulty} multiple-answer question.\n\n"
        "Context (source of truth):\n"
        "{context}\n\n"
        "RULES:\n"
        "- Use ONLY the context\n"
        "- If context is limited,use your own knowledge and generalize carefully without hallucinating\n"
        "- At least 4 options\n"
        "- One or more correct answers\n"
        "- All correct answers must be in options\n"
        "- Focus on conceptual understanding\n\n"
        "Return ONLY a JSON object with:\n"
        "- 'question'\n"
        "- 'options'\n"
        "- 'correct_answers'\n\n"
        "Example:\n"
        "{{\n"
        '  "question": "Which of the following are programming languages?",\n'
        '  "options": ["Python", "HTML", "JavaScript", "Photoshop"],\n'
        '  "correct_answers": ["Python", "JavaScript"]\n'
        "}}\n\n"
        "Your response:"
    ),
)

chat_prompt_template = PromptTemplate(
    template=(
        "You are a helpful study assistant. Provide answers that are short, precise, and no longer than 2-3 sentences. "
        "Avoid unnecessary elaboration or excessive detail in your responses."
    )
)
