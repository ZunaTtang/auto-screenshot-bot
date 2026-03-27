#!/bin/bash

# Move to the directory where this script is located
cd "$(dirname "$0")"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "오류: python3가 설치되어 있지 않습니다."
    echo "https://www.python.org/ 에서 파이썬을 설치해주세요."
    exit 1
fi

# Run the main script
python3 run.py

# Keep terminal open after execution
echo ""
echo "완료되었습니다. 터미널을 닫으려면 아무 키나 누르세요."
read -n 1 -s
