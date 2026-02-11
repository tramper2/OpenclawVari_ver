@echo off
setlocal EnableExtensions

REM 이 배치 파일이 있는 폴더
set "BASE=%~dp0"
set "ROOT=%BASE%"
set "LOG=%BASE%variant_task.log"
set "LOCKFILE=%ROOT%variant_autoexecutor.lock"
set "AGENT_SCRIPT=%ROOT%universal_agent.py"

echo ===== %date% %time% =====>> "%LOG%"
echo START CWD=%CD%>> "%LOG%"
echo ROOT=%ROOT%>> "%LOG%"

REM ========================================
REM 프로세스 중복 실행 방지
REM ========================================

REM 1. Agent 프로세스 먼저 확인!
wmic process where "name='python.exe'" get commandline 2>NUL | find /I "universal_agent.py" >NUL
if not errorlevel 1 (
    echo [BLOCKED] Variant Agent already running.>> "%LOG%"
    exit /b 98
)

REM 2. Lock 파일 확인
if not exist "%LOCKFILE%" goto LOCK_OK
echo [RECOVERY] Lock file exists but no process running - recovering from error.>> "%LOG%"
del "%LOCKFILE%" 2>NUL
echo [INFO] Stale lock removed.>> "%LOG%"
:LOCK_OK

REM 3. 빠른 메시지 확인 (Python으로 먼저 확인 - 새 메시지 없으면 실행 안 함!)
echo [QUICK_CHECK] Checking for new messages...>> "%LOG%"
pushd "%ROOT%" >NUL 2>&1
python quick_check.py >> "%LOG%" 2>&1
set "CHECK_RESULT=%ERRORLEVEL%"
popd >NUL 2>&1

if %CHECK_RESULT% EQU 0 (
    echo [NO_MESSAGE] No new messages. Exiting.>> "%LOG%"
    echo.>> "%LOG%"
    exit /b 0
)

echo [NEW_MESSAGE] New messages found. Starting Variant Agent...>> "%LOG%"

REM 4. Lock 파일 생성
echo %date% %time%> "%LOCKFILE%"
echo Lock file created: %LOCKFILE%>> "%LOG%"

pushd "%ROOT%" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERROR] pushd failed.>> "%LOG%"
  exit /b 1
)

echo BEFORE AGENT CWD=%CD%>> "%LOG%"

REM Run Universal Agent
echo [INFO] Starting Variant Agent...>> "%LOG%"
python "%AGENT_SCRIPT%" >> "%LOG%" 2>&1
set "EC=%ERRORLEVEL%"

echo EXITCODE=%EC%>> "%LOG%"
echo.>> "%LOG%"

REM Lock 파일 삭제
if exist "%LOCKFILE%" (
    del "%LOCKFILE%" 2>NUL
    echo Lock file deleted: %LOCKFILE%>> "%LOG%"
)

popd
exit /b %EC%
