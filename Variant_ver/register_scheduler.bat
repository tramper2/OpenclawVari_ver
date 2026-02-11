@echo off
chcp 65001 >NUL
setlocal EnableExtensions

echo ========================================
echo Windows 작업 스케줄러 등록 (Variant Version)
echo ========================================

set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
set "BAT_FILE=%PROJECT_DIR%\variant_autoexecutor.bat"

for %%I in ("%PROJECT_DIR%") do set "FOLDER_NAME=%%~nxI"
set "TASK_NAME=Variant_AutoBot_%FOLDER_NAME%"

echo 작업 이름: %TASK_NAME%
echo 실행 파일: %BAT_FILE%

net session >NUL 2>&1
if errorlevel 1 (
    echo [오류] 관리자 권한이 필요합니다!
    pause
    exit /b 1
)

schtasks /Delete /TN "%TASK_NAME%" /F >NUL 2>&1
schtasks /Create /TN "%TASK_NAME%" /TR "wscript.exe \"%PROJECT_DIR%\run_hidden.vbs\" \"%BAT_FILE%\"" /SC MINUTE /MO 1 /F

echo.
echo ✅ 등록 완료!
pause
