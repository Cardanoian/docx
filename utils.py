import os


def get_api_key():
    """환경 변수에서 API 키를 가져옵니다."""
    return os.environ.get("GEMINI_API_KEY")
