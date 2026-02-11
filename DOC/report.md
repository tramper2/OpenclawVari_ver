# 프로그램 분석 및 개인화 가이드 (Code Analysis & Personalization Report)

## 1. 프로그램 구조 (Program Structure)

이 프로젝트는 **텔레그램 봇**과 **Claude Code(AI 에이전트)** 를 연동하여 자율 작업을 수행하는 시스템입니다.

### 📁 주요 파일 및 역할
| 파일명 | 역할 | 비고 |
|---|---|---|
| `telegram_listener.py` | **수신 담당**: 텔레그램 서버를 주기적으로 확인(Polling)하여 새 메시지를 `telegram_messages.json`에 저장 | 상시 실행 필요 없음 (자동 실행 시) |
| `telegram_bot.py` | **두뇌/로직**: 메시지 확인, 작업 잠금(`working.json`) 관리, 작업 합산, 결과 보고 등 핵심 로직 포함 | Claude Code가 주로 호출하여 사용 |
| `telegram_sender.py` | **발신 담당**: 텔레그램으로 텍스트 메시지 및 파일을 전송 | 동기/비동기 전송 지원 |
| `mybot_autoexecutor.bat` | **총괄 실행**: 전체 프로세스를 조율하는 스크립트. 새 메시지가 있을 때만 Claude Code를 실행하여 리소스 절약 | 윈도우 스케줄러에 등록되어 1분마다 실행 |
| `quick_check.py` | **고속 확인**: Claude Code를 띄우기 전, Python으로 가볍게 새 메시지 유무만 0.1초 만에 확인 | 배터리/리소스 절약 핵심 |

## 2. 동작 방법 (Workflow)

1.  **메시지 수신**: 사용자가 텔레그램으로 명령(예: "오늘 뉴스 요약해줘")을 보냄.
2.  **주기적 확인**: 윈도우 스케줄러가 1분마다 `mybot_autoexecutor.bat` 실행.
3.  **1차 필터링**: 배치 파일이 `quick_check.py`를 실행.
    - 새 메시지 없으면 → **즉시 종료** (Claude Code 실행 X)
    - 새 메시지 있으면 → 다음 단계 진행
4.  **AI 에이전트 기동**: `claude -p -c ...` 명령어로 Claude Code 실행.
    - 이때 `CLAUDE.md`의 시스템 프롬프트가 적용됨.
5.  **작업 수행**: Claude Code가 `telegram_bot.py`의 함수들을 호출하여:
    - 메시지 읽기 (`check_telegram`)
    - 작업 수행 (파일 생성, 웹 검색 등)
    - 중간 보고 (`send_message_sync`)
6.  **결과 전송**: 작업 완료 후 결과 파일 및 텍스트 전송 (`report_telegram`).
7.  **종료**: Claude Code 세션 종료 및 대기 모드 전환.

## 3. 중요 클래스 및 함수 (Key Classes & Methods)

개인화나 기능 수정을 위해 눈여겨봐야 할 핵심 함수들입니다.

### `telegram_bot.py`
- **`check_telegram()`**: 새 메시지를 가져오고 작업 잠금을 확인하는 가장 중요한 함수.
- **`combine_tasks(pending_tasks)`**: 여러 개의 메시지가 쌓여있을 때 하나로 합쳐서 처리하는 로직. (예: 메시지 3개를 한 번에 작업)
- **`report_telegram(...)`**: 작업 결과를 정리해서 최종적으로 사용자에게 보내고, 메모리에 기록하는 함수.

### `telegram_sender.py`
- **`send_message_sync(chat_id, text)`**: 가장 많이 쓰이는 메시지 전송 함수. 중간 경과 보고에 사용됨.

## 4. 개인화(Personalization) 수정 가이드

이 봇을 **나만의 비서**로 만들기 위해 수정할 수 있는 부분입니다.

### A. 봇의 성격 및 말투 변경 (가장 추천)
- **파일**: `CLAUDE.md` (또는 `mybot_autoexecutor.bat`의 프롬프트 영역)
- **방법**: 이 파일은 Claude Code에게 "너는 누구고 어떻게 행동해야 해"라고 알려주는 **시스템 프롬프트**입니다.
- **수정 예시**:
    - *"너는 친절한 비서야"* -> *"너는 냉철한 데이터 분석가야. 결론부터 말해."*
    - *"존댓말을 써"* -> *"반말 모드로 친구처럼 대화해"*

### B. 허용 사용자 추가/변경
- **파일**: `.env`
- **항목**: `TELEGRAM_ALLOWED_USERS`
- **방법**: 가족이나 동료의 텔레그램 ID(숫자)를 콤마(`,`)로 구분하여 추가하면 그들도 봇을 쓸 수 있습니다.
    - 예: `TELEGRAM_ALLOWED_USERS=12345678,98765432`

### C. 봇 응답 속도 조절 (Polling Interval)
- **파일**: `.env`
- **항목**: `TELEGRAM_POLLING_INTERVAL`
- **방법**: 기본 10초로 설정되어 있습니다. 서버 부하를 줄이려면 60초 등으로 늘릴 수 있습니다.

### D. 자동 실행 주기 변경
- **도구**: 윈도우 작업 스케줄러 (`taskschd.msc`)
- **방법**: `Claude_AutoBot_...` 작업을 찾아 '트리거' 탭에서 '1분마다'를 '5분마다' 또는 '1시간마다'로 변경 가능.

### E. 기능 확장 (고급)
- **파일**: `telegram_bot.py`
- **아이디어**:
    - 특정 키워드("알람", "주식")가 들어오면 Claude Code를 거치지 않고 Python이 즉시 처리하도록 `check_telegram` 내부 로직 수정 가능.
    - `combine_tasks` 로직을 수정하여 메시지 합산 규칙 변경 가능.
