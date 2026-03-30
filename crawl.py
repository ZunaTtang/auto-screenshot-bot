"""
crawl.py — BFS 방식 웹 크롤러 + 전체 화면 스크린샷 캡처
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import time
from collections import deque
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urldefrag, urlparse

from playwright.sync_api import sync_playwright, Page, Response, Error as PlaywrightError


# ---------------------------------------------------------------------------
# Logging setup (호출 측에서 설정되므로 여기서는 getLogger만)
# ---------------------------------------------------------------------------
logger = logging.getLogger("crawler")


# ---------------------------------------------------------------------------
# URL 유틸
# ---------------------------------------------------------------------------

def normalize_url(url: str) -> str:
    """fragment와 trailing slash를 제거해 URL을 정규화한다."""
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    # query는 유지, fragment만 제거
    clean = parsed._replace(fragment="").geturl().rstrip("/")
    return clean


def is_same_domain(base_netloc: str, href: str, same_subdomain_only: bool) -> bool:
    """
    href가 base_netloc과 같은 도메인(또는 서브도메인)에 속하는지 확인한다.

    same_subdomain_only=True  → 정확한 netloc 일치만 허용
    same_subdomain_only=False → 루트 도메인이 같으면 허용 (subdomain 포함)
    """
    if not href:
        return False
    if href.startswith(("javascript:", "#", "mailto:", "tel:", "data:")):
        return False
    parsed = urlparse(href)
    if not parsed.netloc:          # 상대 경로
        return True
    if same_subdomain_only:
        return parsed.netloc == base_netloc
    # 루트 도메인 비교 (예: sub.example.com vs example.com)
    base_root = ".".join(base_netloc.split(".")[-2:])
    href_root = ".".join(parsed.netloc.split(".")[-2:])
    return base_root == href_root


def url_to_filename(url: str) -> str:
    """URL → 안전한 파일명 (충돌 방지용 해시 8자 포함)."""
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", url)[:100]
    digest = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{slug}_{digest}.png"


# ---------------------------------------------------------------------------
# 크롤러 핵심 로직
# ---------------------------------------------------------------------------

def fetch_page(
    page: Page,
    url: str,
    wait_ms: int,
    retry: int,
) -> tuple[Optional[Response], Optional[str]]:
    """
    페이지를 로드하고 (response, error_msg) 튜플을 반환한다.
    retry 횟수만큼 재시도한다.
    """
    last_err: Optional[str] = None
    for attempt in range(1, retry + 2):  # 기본 1회 + retry 추가 시도
        try:
            response = page.goto(url, timeout=30_000, wait_until="domcontentloaded")
            # networkidle 대기 (실패해도 계속 진행)
            try:
                page.wait_for_load_state("networkidle", timeout=10_000)
            except PlaywrightError:
                pass
            if wait_ms > 0:
                page.wait_for_timeout(wait_ms)
            return response, None
        except PlaywrightError as e:
            last_err = str(e)
            if attempt <= retry:
                logger.warning("재시도 %d/%d — %s : %s", attempt, retry, url, last_err)
                time.sleep(1)
    return None, last_err


def crawl(
    start_url: str,
    output_dir: Path,
    auth_path: Optional[str],
    max_pages: int,
    headless: bool,
    wait_sec: float,
    same_subdomain_only: bool,
    retry: int,
) -> list[dict]:
    """BFS 크롤링 실행. 결과 목록을 반환한다."""

    shots_dir = output_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    base_netloc = urlparse(start_url).netloc
    start_norm = normalize_url(start_url)

    visited: set[str] = set()
    queued: set[str] = {start_norm}   # 큐에 넣은 URL 추적 (중복 방지)
    queue: deque[tuple[str, Optional[str]]] = deque([(start_norm, None)])
    results: list[dict] = []
    wait_ms = int(wait_sec * 1000)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context_kwargs: dict = {}
        if auth_path and Path(auth_path).exists():
            context_kwargs["storage_state"] = auth_path
        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        while queue and len(visited) < max_pages:
            url, parent = queue.popleft()

            if url in visited:
                continue
            visited.add(url)

            logger.info("[%d/%d] %s", len(visited), max_pages, url)

            response, error_msg = fetch_page(page, url, wait_ms, retry)

            if error_msg:
                logger.error("FAIL %s — %s", url, error_msg)
                results.append({
                    "url": url,
                    "parent": parent,
                    "status": None,
                    "title": None,
                    "h1": [],
                    "links": [],
                    "screenshot": None,
                    "error": error_msg,
                })
                continue

            status = response.status if response else None
            title = page.title()

            try:
                h1 = page.locator("h1").all_text_contents()
            except PlaywrightError:
                h1 = []

            # 링크 수집
            try:
                raw_links: list[str] = page.locator("a[href]").evaluate_all(
                    "els => els.map(a => a.getAttribute('href'))"
                )
            except PlaywrightError:
                raw_links = []

            internal_links: list[str] = []
            for href in raw_links:
                if not href:
                    continue
                full = normalize_url(urljoin(url, href))
                if is_same_domain(base_netloc, full, same_subdomain_only):
                    internal_links.append(full)
                    if full not in visited and full not in queued:
                        queued.add(full)
                        queue.append((full, url))

            # 스크린샷
            filename = url_to_filename(url)
            shot_path = shots_dir / filename
            try:
                page.screenshot(path=str(shot_path), full_page=True)
            except PlaywrightError as e:
                logger.warning("스크린샷 실패 %s — %s", url, e)
                shot_path = None  # type: ignore

            results.append({
                "url": url,
                "parent": parent,
                "status": status,
                "title": title,
                "h1": h1,
                "links": sorted(set(internal_links)),
                "screenshot": str(shot_path) if shot_path else None,
                "error": None,
            })
            logger.info("OK [%s] %s", status, url)

        browser.close()

    return results


# ---------------------------------------------------------------------------
# CLI 진입점
# ---------------------------------------------------------------------------

def setup_logging(output_dir: Path, verbose: bool) -> None:
    log_path = output_dir / "crawler.log"
    output_dir.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Web Screenshot Crawler — BFS 방식으로 사이트를 탐색하며 스크린샷을 저장합니다.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--url", required=True, help="크롤링 시작 URL")
    parser.add_argument("--auth", default=None, help="auth.json 경로 (로그인 세션)")
    parser.add_argument("--max-pages", type=int, default=30, help="최대 크롤링 페이지 수")
    parser.add_argument("--output", default="output", help="결과 저장 폴더")
    parser.add_argument("--headless", action="store_true", help="헤드리스 모드로 실행")
    parser.add_argument("--wait", type=float, default=2.0, help="페이지 로드 후 대기 시간(초)")
    parser.add_argument(
        "--same-subdomain-only",
        action="store_true",
        help="정확히 같은 서브도메인만 크롤링 (기본: 같은 루트 도메인 전체)",
    )
    parser.add_argument("--retry", type=int, default=1, help="실패 시 재시도 횟수")
    parser.add_argument("--verbose", action="store_true", help="DEBUG 수준 로그 출력")
    args = parser.parse_args()

    output_dir = Path(args.output)
    setup_logging(output_dir, args.verbose)
    logger.info("크롤링 시작: %s (최대 %d페이지)", args.url, args.max_pages)

    results = crawl(
        start_url=args.url,
        output_dir=output_dir,
        auth_path=args.auth,
        max_pages=args.max_pages,
        headless=args.headless,
        wait_sec=args.wait,
        same_subdomain_only=args.same_subdomain_only,
        retry=args.retry,
    )

    pages_json = output_dir / "pages.json"
    with open(pages_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    success = sum(1 for r in results if not r["error"])
    failed = len(results) - success
    logger.info("완료: 성공 %d / 실패 %d / 결과 저장: %s", success, failed, pages_json)
    print(f"\n✅ 완료 — 성공: {success}개, 실패: {failed}개")
    if failed:
        print(f"⚠️  실패 URL은 {pages_json} 에서 확인하세요.")


if __name__ == "__main__":
    main()