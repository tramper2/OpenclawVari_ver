# 🤖 소놀봇 (Variant Version) - Multi-Provider

이 버전은 **사용자가 원하는 AI(LLM)를 선택**하여 사용할 수 있는 확장판입니다.
하나의 봇으로 OpenAI(ChatGPT), Moonshot(Kimi), DeepSeek, Zhipu(GLM), Google Gemini 등을 모두 구동할 수 있습니다.

## 📌 지원하는 AI
설정 단계에서 번호를 선택하여 간편하게 전환할 수 있습니다.

| 번호 | 구분 | 지원 서비스 예시 | 비고 |
|---|---|---|---|
| **1** | **OpenAI 호환** | ChatGPT, **Kimi(Moonshot)**, **DeepSeek**, LocalLLM (Ollama 등) | Base URL 변경 가능 |
| **2** | **Zhipu AI** | ChatGLM (GLM-4 등) | 전용 SDK 사용 |
| **3** | **Google** | Gemini 2.0 Flash / Pro | 전용 SDK 사용 |

---

## 🚀 설치 및 실행 방법

### 1단계: API 키 준비
사용하고자 하는 서비스의 API 키를 미리 준비해주세요.
*   **Kimi (Moonshot)**: [platform.moonshot.cn](https://platform.moonshot.cn/)
*   **DeepSeek**: [platform.deepseek.com](https://platform.deepseek.com/)
*   **Zhipu AI**: [open.bigmodel.cn](https://open.bigmodel.cn/)
*   **Gemini**: [aistudio.google.com](https://aistudio.google.com/)

### 2단계: 자동 설정 (setup.bat)
1.  `setup.bat` 파일을 실행합니다.
2.  안내에 따라 **텔레그램 설정**을 입력합니다.
3.  **AI 제공자 선택** 화면이 나오면 번호를 입력합니다.
4.  해당 AI의 **API Key**와 **모델명**을 입력합니다.
    *   Kimi 예시: 모델명 `moonshot-v1-8k`, Base URL `https://api.moonshot.cn/v1`
    *   DeepSeek 예시: 모델명 `deepseek-chat`, Base URL `https://api.deepseek.com`
    *   Zhipu 예시: 모델명 `glm-4`
    *   Gemini 예시: 모델명 `gemini-2.0-flash-exp`

### 3단계: 실행 테스트
1.  `variant_autoexecutor.bat`를 실행하여 오류 없이 시작되는지 확인합니다.
2.  텔레그램으로 말을 걸어 응답을 확인합니다.

### 4단계: 자동 실행 등록
1.  `register_scheduler.bat`를 **관리자 권한으로 실행**합니다.
2.  1분마다 봇이 자동으로 확인 및 실행됩니다.

---

## ⚙️ 설정 변경 방법
설정이 완료된 후 AI를 바꾸고 싶다면 `.env` 파일을 메모장으로 열어 직접 수정하면 됩니다.

```env
# 예: Kimi 사용 시
AI_PROVIDER=openai
AI_API_KEY=sk-xxxxxxxxxxxxxx
AI_MODEL_NAME=moonshot-v1-8k
AI_BASE_URL=https://api.moonshot.cn/v1
```

```env
# 예: GLM 사용 시
AI_PROVIDER=zhipu
AI_API_KEY=xxxxxxxx.xxxxxxxx
AI_MODEL_NAME=glm-4
```

## 📂 파일 구조
- `universal_agent.py`: 통합 AI 에이전트 실행 스크립트.
- `ai_providers.py`: 각 AI 서비스별 연결 로직이 담긴 파일.
- `config.py`: 환경 변수 설정 로드.
- `variant_autoexecutor.bat`: 자동 실행 스크립트.
