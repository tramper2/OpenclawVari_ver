
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USERS = os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",")
TELEGRAM_POLLING_INTERVAL = int(os.getenv("TELEGRAM_POLLING_INTERVAL", 10))

# AI Provider 설정
# 예: openai, zhipu, gemini
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

# 공통 AI API Key
AI_API_KEY = os.getenv("AI_API_KEY")

# 모델 명 (Provider별 상이)
# OpenAI: gpt-4o, gpt-3.5-turbo
# Moonshot(Kimi): moonshot-v1-8k
# Zhipu: glm-4
# Gemini: gemini-2.0-flash-exp
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gpt-3.5-turbo")

# OpenAI 호환 API Base URL (선택사항)
# Kimi 예시: https://api.moonshot.cn/v1
AI_BASE_URL = os.getenv("AI_BASE_URL")

def validate_config():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return False
    if not AI_API_KEY:
        print("Error: AI_API_KEY not found in .env")
        return False
    return True
