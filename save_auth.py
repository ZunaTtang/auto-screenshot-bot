"""
save_auth.py — Playwright를 사용해 로그인 세션을 auth.json으로 저장한다.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, Error as PlaywrightError

logger = logging.getLogger("save_auth")


def validate_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def save_session(url: str, output_path: Path) -> bool:
    """
    브라우저를 열어 사용자가 직접 로그인하도록 한 뒤
    스토리지 상태를 output_path 에 저장한다.
    반환값: 성공 여부
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            logger.info("브라우저를 여는 중: %s", url)
            page.goto(url, timeout=30_000)

            print("\n👉 브라우저에서 직접 로그인하세요.")
            print("   로그인 완료 후 이 창으로 돌아와 엔터를 누르세요.")
            input("\n[엔터] 로그인 완료 후 엔터: ")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(output_path))
            logger.info("세션 저장 완료: %s", output_path)
            print(f"\n✅ 세션 저장 완료: {output_path}")

            browser.close()
            return True

    except PlaywrightError as e:
        logger.error("Playwright 오류: %s", e)
        print(f"\n❌ 브라우저 오류가 발생했습니다: {e}")
        return False
    except KeyboardInterrupt:
        print("\n작업이 취소되었습니다.")
        return False


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    parser = argparse.ArgumentParser(
        description="로그인 세션을 auth.json으로 저장합니다.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--url", required=True, help="로그인 페이지 URL")
    parser.add_argument("--output", default="auth.json", help="저장할 파일 경로")
    args = parser.parse_args()

    if not validate_url(args.url):
        print("❌ 올바른 URL을 입력하세요 (http:// 또는 https:// 로 시작해야 합니다).")
        sys.exit(1)

    success = save_session(url=args.url, output_path=Path(args.output))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()