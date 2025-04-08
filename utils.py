import os

# from dotenv import load_dotenv


# def load_environment_variables():
#     """.env 파일에서 환경 변수를 로드합니다."""
#     load_dotenv()


def get_api_key():
    """환경 변수에서 API 키를 가져옵니다."""
    return os.environ.get("GEMINI_API_KEY")
