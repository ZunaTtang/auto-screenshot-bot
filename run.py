import os
import subprocess
import sys
import json
import shutil
from pathlib import Path

# Color codes for terminal - using safe ASCII characters
GREEN = ""  # "\033[92m" (Removing for base compatibility)
BLUE = ""   # "\033[94m"
YELLOW = "" # "\033[93m"
RED = ""    # "\033[91m"
RESET = ""  # "\033[0m"

AUTH_FILE = "auth.json"

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}")

def run_command(command, description=None):
    if description:
        print(f"\n[실행 중] {description}...")
    try:
        # Use subprocess.run for better handling and pass env
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        subprocess.check_call(command, shell=True, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[오류] 작업 중 문제가 발생했습니다: {e}")
        return False

def check_playwright():
    print_header("1. 환경 구축 (Playwright & Dependencies)")
    
    try:
        import playwright
        print("[정보] Playwright 패키지가 이미 설치되어 있습니다.")
    except ImportError:
        print("[경고] Playwright 패키지가 없습니다. 설치를 시작합니다.")
        if not run_command([sys.executable, "-m", "pip", "install", "playwright"], "Playwright pip 패키지 설치"):
            return False

    print("[정보] 브라우저(Chromium) 확인 및 설치 중...")
    if run_command([sys.executable, "-m", "playwright", "install", "chromium"], "Playwright Chromium 설치"):
        print("[성공] 환경 구축이 완료되었습니다.")
        return True
    return False

def save_auth():
    print_header("2. 로그인 세션 저장")
    
    if os.path.exists(AUTH_FILE):
        overwrite = input(f"[확인] '{AUTH_FILE}'가 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ").lower()
        if overwrite != 'y':
            print("[중지] 기존 세션을 유지합니다.")
            return True

    url = input("[입력] 로그인할 사이트의 URL을 입력하세요: ").strip()
    if not url.startswith("http"):
        print("[오류] 올바른 URL을 입력하세요 (http:// 또는 https:// 포함).")
        return False

    print("\n--- 지시사항 ---")
    print("1. 브라우저 창이 열리면 사이트에 접속합니다.")
    print("2. 로그인을 완료합니다.")
    print("3. 로그인이 완료되면 터미널로 돌아와 엔터를 누르세요.")
    
    return run_command([sys.executable, "save_auth.py", "--url", url], "로그인 세션 캡처")

def run_crawling():
    print_header("3. 사이트 크롤링 실행")
    
    if not os.path.exists(AUTH_FILE):
        print(f"[주의] '{AUTH_FILE}'가 없습니다. 비로그인 상태로 크롤링을 진행하시겠습니까?")
        choice = input("(y/n): ").lower()
        if choice != 'y':
            return False

    start_url = input("[입력] 크롤링을 시작할 URL을 입력하세요: ").strip()
    if not start_url.startswith("http"):
        print("[오류] 올바른 URL을 입력하세요.")
        return False

    try:
        max_pages = input("[입력] 최대 스크린샷(페이지) 개수 설정 (기본 30): ").strip()
        max_pages = int(max_pages) if max_pages else 30
    except ValueError:
        print("[정보] 숫자가 아닙니다. 기본값 30으로 설정합니다.")
        max_pages = 30

    try:
        wait_time = input("[입력] 페이지 로딩 후 대기 시간(초) 설정 (기본 2): ").strip()
        wait_time = float(wait_time) if wait_time else 2.0
    except ValueError:
        print("[정보] 숫자가 아닙니다. 기본값 2초로 설정합니다.")
        wait_time = 2.0

    cmd = [sys.executable, "crawl.py", "--url", start_url, "--max-pages", str(max_pages), "--wait", str(wait_time)]
    if os.path.exists(AUTH_FILE):
        cmd.extend(["--auth", AUTH_FILE])
    
    return run_command(cmd, f"크롤링 실행 중 (최대 {max_pages}개, 대기 {wait_time}초)")

def open_output_folder():
    print_header("5. 스크린샷 폴더 열기")
    output_dir = os.path.join("output", "screenshots")
    if not os.path.exists(output_dir):
        print(f"[오류] 아직 스크린샷 폴더가 생성되지 않았습니다. 크롤링을 먼저 실행하세요.")
        return False
    
    abs_path = os.path.abspath(output_dir)
    print(f"[정보] 폴더를 여는 중: {abs_path}")
    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin": # macOS
            subprocess.run(["open", abs_path])
        else: # linux
            subprocess.run(["xdg-open", abs_path])
        return True
    except Exception as e:
        print(f"[오류] 폴더를 여는데 실패했습니다: {e}")
        return False

def reset_all():
    print_header("6. 초기화 (Auth 및 데이터 삭제)")
    
    confirm = input("[주의] 모든 설정(auth.json)과 출력 데이터를 삭제하시겠습니까? (y/n): ").lower()
    if confirm == 'y':
        if os.path.exists(AUTH_FILE):
            os.remove(AUTH_FILE)
            print(f"[성공] {AUTH_FILE} 삭제 완료.")
        
        output_dir = "output"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            print(f"[성공] {output_dir} 폴더 삭제 완료.")
            
        print("[완료] 초기화가 완료되었습니다.")
    else:
        print("[정보] 초기화를 취소했습니다.")

def main_menu():
    while True:
        print_header("Web Screenshot Autobot - 메인 메뉴")
        print("1. 환경 구축 (Playwright 설치)")
        print("2. 로그인 세션 저장 (로그인 진행)")
        print("3. 사이트 크롤링 실행 (스크린샷 저장)")
        print("4. 결과물 - 스크린샷 폴더 열기")
        print("5. 초기화 (Auth 및 링크 세션 초기화)")
        print("6. 종료")
        
        choice = input("\n[선택] 번호를 입력하세요 (1-6): ").strip()
        
        if choice == '1':
            check_playwright()
        elif choice == '2':
            save_auth()
        elif choice == '3':
            run_crawling()
        elif choice == '4':
            open_output_folder()
        elif choice == '5':
            reset_all()
        elif choice == '6':
            print("프로그램을 종료합니다. 감사합니다.")
            break
        else:
            print("[오류] 잘못된 선택입니다. 다시 입력해주세요.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        sys.exit(0)
