@echo off
chcp 65001 >NUL
setlocal EnableExtensions EnableDelayedExpansion

echo ========================================
echo 소놀봇 (Variant Version) 자동 설정
echo ========================================
echo.
echo 이 버전은 다양한 AI (OpenAI, Kimi, GLM, Gemini 등)를 지원합니다.
echo.

set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

REM Python 확인
python --version >NUL 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다!
    pause
    exit /b 1
)

REM 패키지 설치
echo [1/3] Python 패키지 설치 중...
pip install -r "%PROJECT_DIR%\requirements.txt"
if errorlevel 1 (
    echo [오류] 패키지 설치 실패!
    pause
    exit /b 1
)
echo       ✅ 패키지 설치 완료!
echo.

REM .env 파일 생성
if not exist "%PROJECT_DIR%\.env" (
    echo [2/3] 설정 파일(.env) 생성
    echo.
    echo === 텔레그램 설정 ===
    set /p BOT_TOKEN="텔레그램 봇 토큰: "
    set /p USER_ID="허용할 사용자 ID (쉼표 구분): "
    echo.
    
    echo === AI 제공자 선택 ===
    echo 1. OpenAI 호환 (ChatGPT, Kimi, DeepSeek 등)
    echo 2. Zhipu AI (ChatGLM)
    echo 3. Google Gemini
    echo.
    set /p PROVIDER_CHOICE="번호를 선택하세요 (1/2/3): "
    
    set PROVIDER=openai
    set MODEL_NAME=gpt-3.5-turbo
    set BASE_URL=
    
    if "!PROVIDER_CHOICE!"=="1" (
        set PROVIDER=openai
        echo.
        echo [OpenAI 호환 설정]
        set /p API_KEY="API Key (sk-...): "
        set /p MODEL_NAME="모델명 (예: moonshot-v1-8k, gpt-4o): "
        set /p BASE_URL="Base URL (선택, 엔터치면 기본값): "
    )
    if "!PROVIDER_CHOICE!"=="2" (
        set PROVIDER=zhipu
        echo.
        echo [Zhipu AI 설정]
        set /p API_KEY="API Key: "
        set /p MODEL_NAME="모델명 (예: glm-4): "
    )
    if "!PROVIDER_CHOICE!"=="3" (
        set PROVIDER=gemini
        echo.
        echo [Google Gemini 설정]
        set /p API_KEY="API Key: "
        set MODEL_NAME=gemini-2.0-flash-exp
    )

    (
        echo TELEGRAM_BOT_TOKEN=!BOT_TOKEN!
        echo TELEGRAM_ALLOWED_USERS=!USER_ID!
        echo TELEGRAM_POLLING_INTERVAL=10
        echo.
        echo AI_PROVIDER=!PROVIDER!
        echo AI_API_KEY=!API_KEY!
        echo AI_MODEL_NAME=!MODEL_NAME!
        if not "!BASE_URL!"=="" echo AI_BASE_URL=!BASE_URL!
    ) > "%PROJECT_DIR%\.env"

    echo       ✅ .env 파일 생성 완료!
) else (
    echo [2/3] .env 파일이 이미 존재합니다.
)

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo register_scheduler.bat 를 관리자 권한으로 실행하여 자동 실행을 등록하세요.
echo.
pause
