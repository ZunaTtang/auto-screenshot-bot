@echo off
chcp 65001 > nul
title Web Screenshot Autobot

:: Python 설치 여부 확인
where python > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo  [오류] Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    echo  https://www.python.org/ 에서 Python을 설치해주세요.
    echo  설치 시 "Add Python to PATH" 옵션을 반드시 체크하세요.
    echo.
    pause
    exit /b 1
)

:: 스크립트 위치로 이동 (어디서 실행해도 동작하게)
cd /d "%~dp0"

echo.
echo  Web Screenshot Autobot 시작 중...
echo.

python run.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo  [오류] 프로그램 실행 중 문제가 발생했습니다. (종료 코드: %ERRORLEVEL%)
)

echo.
pause