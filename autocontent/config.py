"""환경설정 로더. .env 파일과 OS 환경변수를 읽어 한 곳에서 제공한다."""
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv 미설치 시에도 OS 환경변수로 동작
    pass


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.tech/v1").rstrip("/")
    WRITER_MODEL = os.getenv("WRITER_MODEL", "gpt-4o-mini")
    TTS_VOICE = os.getenv("TTS_VOICE", "ko-KR-SunHiNeural")
    OUTPUT_LANG = os.getenv("OUTPUT_LANG", "한국어")

    # 키 없이 동작하는 무료 서비스 엔드포인트
    JINA_SEARCH = "https://s.jina.ai/"
    JINA_READER = "https://r.jina.ai/"
    POLLINATIONS = "https://image.pollinations.ai/prompt/"

    @classmethod
    def require_llm(cls):
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY.startswith("여기에"):
            raise SystemExit(
                "OPENAI_API_KEY가 설정되지 않았습니다.\n"
                "  1) cp .env.example .env\n"
                "  2) https://api.chatanywhere.tech/v1/oauth/free/render 에서 무료 키 발급\n"
                "  3) .env 의 OPENAI_API_KEY 에 붙여넣기"
            )
