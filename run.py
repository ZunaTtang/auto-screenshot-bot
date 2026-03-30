"""
run.py — Web Screenshot Autobot 메인 CLI
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 프로젝트 루트를 기준으로 경로를 계산한다 (어디서 실행해도 안전)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.resolve()
AUTH_FILE = PROJECT_ROOT / "auth.json"

logger = logging.getLogger("run")


# ---------------------------------------------------------------------------
# 공통 유틸
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


def print_header(text: str) -> None:
    print(f"\n{'=' * 54}")
    print(f"  {text}")
    print(f"{'=' * 54}")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """yes/no 질문. 기본값을 대괄호로 표시한다."""
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        raw = input(f"{prompt} {hint}: ").strip().lower()
        if raw in ("", "y", "yes"):
            return True if raw == "" and default else raw in ("y", "yes") or (raw == "" and default)
        if raw in ("n", "no"):
            return False
        print("  'y' 또는 'n' 을 입력하세요.")


def run_script(args: list[str], description: str) -> bool:
    """
    Python 스크립트를 현재 인터프리터로 실행한다.
    shell=True 를 사용하지 않고 리스트 방식으로 안전하게 호출한다.
    """
    cmd = [sys.executable] + args
    print(f"\n[실행 중] {description}...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            check=True,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error("스크립트 실행 실패 (종료 코드 %d): %s", e.returncode, " ".join(cmd))
        return False
    except FileNotFoundError:
        logger.error("Python 인터프리터를 찾을 수 없습니다: %s", sys.executable)
        return False


# ---------------------------------------------------------------------------
# 메뉴 기능 구현
# ---------------------------------------------------------------------------

def menu_setup_env() -> None:
    """1. 환경 구축 (Playwright 설치)"""
    print_header("1. 환경 구축 (Playwright & Dependencies)")

    try:
        import playwright  # noqa: F401
        print("[정보] Playwright 패키지가 이미 설치되어 있습니다.")
    except ImportError:
        print("[안내] Playwright 패키지가 없습니다. 설치를 시작합니다.")
        ok = run_script(["-m", "pip", "install", "playwright"], "pip install playwright")
        if not ok:
            print("[오류] Playwright 설치에 실패했습니다. pip가 정상 동작하는지 확인하세요.")
            return

    print("[정보] Chromium 브라우저 확인 및 설치 중...")
    ok = run_script(["-m", "playwright", "install", "chromium"], "playwright install chromium")
    if ok:
        print("[완료] 환경 구축이 성공적으로 완료되었습니다.")
    else:
        print("[오류] Chromium 설치에 실패했습니다.")


def menu_save_auth() -> None:
    """2. 로그인 세션 저장"""
    print_header("2. 로그인 세션 저장")

    if AUTH_FILE.exists():
        overwrite = ask_yes_no(f"  '{AUTH_FILE.name}'이 이미 존재합니다. 덮어쓰시겠습니까?", default=False)
        if not overwrite:
            print("[중지] 기존 세션을 유지합니다.")
            return

    url = input("\n[입력] 로그인할 사이트의 URL: ").strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        print("[오류] 올바른 URL을 입력하세요 (http:// 또는 https:// 포함).")
        return

    print("\n--- 진행 방법 ---")
    print("  1. 브라우저 창이 열리면 직접 로그인하세요.")
    print("  2. 로그인 완료 후 터미널로 돌아와 엔터를 누르세요.")

    script = str(PROJECT_ROOT / "save_auth.py")
    run_script([script, "--url", url, "--output", str(AUTH_FILE)], "로그인 세션 캡처")


def menu_run_crawling() -> None:
    """3. 사이트 크롤링 실행"""
    print_header("3. 사이트 크롤링 실행")

    if not AUTH_FILE.exists():
        print(f"[주의] '{AUTH_FILE.name}'가 없습니다.")
        proceed = ask_yes_no("  비로그인 상태로 크롤링을 진행하시겠습니까?", default=False)
        if not proceed:
            return

    # URL
    start_url = input("\n[입력] 크롤링 시작 URL: ").strip()
    if not (start_url.startswith("http://") or start_url.startswith("https://")):
        print("[오류] 올바른 URL을 입력하세요.")
        return

    # 최대 페이지 수
    raw = input("[입력] 최대 페이지 수 (기본 30): ").strip()
    try:
        max_pages = int(raw) if raw else 30
        if max_pages < 1:
            raise ValueError
    except ValueError:
        print("[정보] 기본값 30으로 설정합니다.")
        max_pages = 30

    # 대기 시간
    raw = input("[입력] 페이지 로드 후 대기 시간(초) (기본 2): ").strip()
    try:
        wait_time = float(raw) if raw else 2.0
        if wait_time < 0:
            raise ValueError
    except ValueError:
        print("[정보] 기본값 2초로 설정합니다.")
        wait_time = 2.0

    # 재시도 횟수
    raw = input("[입력] 실패 시 재시도 횟수 (기본 1): ").strip()
    try:
        retry = int(raw) if raw else 1
        if retry < 0:
            raise ValueError
    except ValueError:
        print("[정보] 기본값 1로 설정합니다.")
        retry = 1

    # 옵션
    headless = ask_yes_no("\n[옵션] 헤드리스 모드로 실행하시겠습니까? (브라우저 창 숨김)", default=True)
    same_sub = ask_yes_no("[옵션] 정확히 같은 서브도메인만 크롤링하시겠습니까?", default=False)

    # 명령 조합
    script = str(PROJECT_ROOT / "crawl.py")
    cmd: list[str] = [
        script,
        "--url", start_url,
        "--max-pages", str(max_pages),
        "--wait", str(wait_time),
        "--retry", str(retry),
        "--output", str(PROJECT_ROOT / "output"),
    ]
    if AUTH_FILE.exists():
        cmd.extend(["--auth", str(AUTH_FILE)])
    if headless:
        cmd.append("--headless")
    if same_sub:
        cmd.append("--same-subdomain-only")

    label = f"크롤링 (최대 {max_pages}페이지, 대기 {wait_time}초)"
    run_script(cmd, label)


def menu_open_output() -> None:
    """4. 스크린샷 폴더 열기"""
    print_header("4. 스크린샷 폴더 열기")
    shots_dir = PROJECT_ROOT / "output" / "screenshots"
    if not shots_dir.exists():
        print("[오류] 스크린샷 폴더가 아직 없습니다. 크롤링을 먼저 실행하세요.")
        return

    print(f"[정보] 폴더를 여는 중: {shots_dir}")
    try:
        if sys.platform == "win32":
            os.startfile(str(shots_dir))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(shots_dir)], check=True)
        else:
            subprocess.run(["xdg-open", str(shots_dir)], check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"[오류] 폴더를 열지 못했습니다: {e}")


def menu_reset() -> None:
    """5. 초기화"""
    import shutil
    print_header("5. 초기화 (Auth 및 출력 데이터 삭제)")
    confirm = ask_yes_no("[주의] auth.json과 output/ 폴더를 모두 삭제하시겠습니까?", default=False)
    if not confirm:
        print("[정보] 초기화를 취소했습니다.")
        return

    if AUTH_FILE.exists():
        AUTH_FILE.unlink()
        print(f"[완료] {AUTH_FILE.name} 삭제.")

    output_dir = PROJECT_ROOT / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print("[완료] output/ 폴더 삭제.")

    print("[완료] 초기화가 완료되었습니다.")


# ---------------------------------------------------------------------------
# 메인 메뉴 루프
# ---------------------------------------------------------------------------

def main_menu() -> None:
    while True:
        print_header("Web Screenshot Autobot — 메인 메뉴")
        print("  1. 환경 구축       (Playwright 설치)")
        print("  2. 로그인 세션 저장 (auth.json 생성)")
        print("  3. 사이트 크롤링   (스크린샷 + JSON 저장)")
        print("  4. 스크린샷 폴더 열기")
        print("  5. 초기화          (Auth 및 데이터 삭제)")
        print("  6. 종료")

        choice = input("\n[선택] 번호를 입력하세요 (1-6): ").strip()

        if choice == "1":
            menu_setup_env()
        elif choice == "2":
            menu_save_auth()
        elif choice == "3":
            menu_run_crawling()
        elif choice == "4":
            menu_open_output()
        elif choice == "5":
            menu_reset()
        elif choice == "6":
            print("\n프로그램을 종료합니다. 감사합니다.")
            break
        else:
            print("[오류] 1~6 사이의 번호를 입력하세요.")


def main() -> None:
    setup_logging()
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
