from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from src.models.question_schemas import (
    MCQQuestion,
    FillBlankQuestion,
    MultipleAnswerQuestion,
)
from src.prompts.templates import (
    mcq_prompt_template,
    fill_blank_prompt_template,
    multiple_answer_prompt_template,
)
from src.llms.llm_client import get_groq_llm, get_openai_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:

    def __init__(self, llm: str, api_key: str = ""):
        self.llm = (
            get_openai_llm(llm) if llm.startswith("gpt") else get_groq_llm(llm, api_key)
        )
        self.logger = get_logger(self.__class__.__name__)

    def _retry_and_parse(
        self, prompt: PromptTemplate, parser: PydanticOutputParser, context, difficulty
    ):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question with difficulty {difficulty}")

                response = self.llm.invoke(
                    prompt.format(context=context, difficulty=difficulty)
                )

                parsed = parser.parse(response.content)
                self.logger.info("Sucessfully parsed the question")
                return parsed

            except Exception as e:
                self.logger.error(f"Error coming : {str(e)}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(
                        f"Generation failed after {settings.MAX_RETRIES} attempts", e
                    )

    def generate_mcq(self, context: str, difficulty: str = "medium") -> MCQQuestion:

        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            question = self._retry_and_parse(
                mcq_prompt_template, parser, context, difficulty
            )
            if (
                len(question.options) != 4
                or question.correct_answer not in question.options
            ):
                raise ValueError("Invalid MCQ structure")

            self.logger.info("Generated a valid MCQ Question")
            return question
        except Exception as e:
            self.logger.error("Failed to generate MCQ Question")
            raise CustomException("MCQ generation failed", e)

    def generate_fill_blank(
        self, context: str, difficulty: str = "medium"
    ) -> FillBlankQuestion:

        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(
                fill_blank_prompt_template, parser, context, difficulty
            )

            if "____" not in question.question:
                raise ValueError("Fill in the blank should contain '____' ")

            self.logger.info("Generated a valid fill blank Question")
            return question
        except Exception as e:
            self.logger.error("Failed to generate fill blank Question")
            raise CustomException("Fill blank generation failed", e)

    def generate_multiple_answer(
        self, context: str, difficulty: str = "medium"
    ) -> MultipleAnswerQuestion:

        try:
            parser = PydanticOutputParser(pydantic_object=MultipleAnswerQuestion)

            question = self._retry_and_parse(
                multiple_answer_prompt_template, parser, context, difficulty
            )

            if len(question.options) < 4 or not set(question.correct_answers).issubset(
                set(question.options)
            ):
                raise ValueError("Invalid MCQ structure")

            self.logger.info("Generated a valid MCQ Question")
            return question
        except Exception as e:
            self.logger.error("Failed to generate MCQ Question")
            raise CustomException("MCQ generation failed", e)

    def generate_from_langchain_rag(
        self,
        rag_pipeline,
        num_questions,
        difficulty,
        question_type,
    ):
        query = f"""
        Identify key concepts for {difficulty} level {question_type} quiz questions.
        """

        chunks = rag_pipeline.retrieve(query)

        context = "\n\n".join(chunks)

        return self.generate_questions(
            topic=context,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type=question_type,
        )
