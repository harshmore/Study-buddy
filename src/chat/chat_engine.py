from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from src.llms.llm_client import get_groq_llm, get_openai_llm


class ChatEngine:

    def __init__(self, llm: str):
        self.llm = get_openai_llm(llm) if llm.startswith("gpt") else get_groq_llm(llm)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Conversation started")

    def respond(self, messages):
        """
        messages: [{role, content}]
        """

        try:
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            self.logger.error("Failed to generate chat response")
            raise CustomException("Chat engine failed", e)
