#!/bin/bash
# Web Screenshot Autobot — macOS 실행 스크립트

# 이 스크립트가 있는 폴더로 이동 (어디서 실행해도 안전)
cd "$(dirname "$0")" || exit 1

# python3 또는 python 탐색
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo ""
    echo " [오류] Python이 설치되어 있지 않습니다."
    echo " https://www.python.org/ 에서 Python 3를 설치해주세요."
    echo ""
    read -rn 1 -p "아무 키나 누르면 종료됩니다..."
    exit 1
fi

echo ""
echo " Web Screenshot Autobot 시작 중..."
echo ""

$PYTHON run.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo " [오류] 프로그램이 비정상 종료되었습니다. (종료 코드: $EXIT_CODE)"
fi

echo ""
read -rn 1 -p "아무 키나 누르면 터미널을 닫습니다..."
echo ""
