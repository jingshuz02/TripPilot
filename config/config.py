import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # DeepSeek Configuration
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-08493e83ce83432ea0d142f39b794ddf')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    # Travel APIs
    BOOKING_API_KEY = os.getenv('BOOKING_API_KEY')
    SKYSCANNER_API_KEY = os.getenv('SKYSCANNER_API_KEY')
    TRIPADVISOR_API_KEY = os.getenv('TRIPADVISOR_API_KEY')

    # Map APIs
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    GAODE_API_KEY = os.getenv('GAODE_API_KEY')

    # Search API
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database/trippilot.db')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    @classmethod
    def get_deepseek_client(cls):
        """Return configured DeepSeek client"""
        from openai import OpenAI
        return OpenAI(
            api_key=cls.DEEPSEEK_API_KEY,
            base_url=cls.DEEPSEEK_BASE_URL
        )