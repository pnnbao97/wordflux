from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIClientManager:
    """Quản lý OpenAI API client"""

    def __init__(self, openai_api_key: str, base_url: str = None):
        """
        Khởi tạo OpenAI client
        """

        self.openai_api_key = openai_api_key
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in config. Please check your config.yaml file.")

        self.client = AsyncOpenAI(api_key=self.openai_api_key, base_url=base_url)

    def get_client(self) -> AsyncOpenAI:
        """Trả về OpenAI client"""
        return self.client
