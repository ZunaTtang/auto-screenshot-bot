import argparse
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urljoin, urldefrag
from collections import deque
import os, json, re

def normalize_url(url):
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    return parsed._replace(query="", fragment="").geturl().rstrip("/")

def is_internal(base, href):
    if not href:
        return False
    if href.startswith(("javascript:", "#", "mailto:", "tel:")):
        return False
    parsed = urlparse(href)
    return (not parsed.netloc) or (parsed.netloc == base)

def slugify(url):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", url)[:150]

def main():
    parser = argparse.ArgumentParser(description="Site crawler with screenshots")
    parser.add_argument("--url", required=True, help="Start URL")
    parser.add_argument("--auth", help="auth.json path")
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--output", default="output")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--wait", type=float, default=2.0, help="Wait time in seconds after load")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    shots_dir = os.path.join(args.output, "screenshots")
    os.makedirs(shots_dir, exist_ok=True)

    visited = set()
    queue = deque([(normalize_url(args.url), None)])
    results = []

    base = urlparse(args.url).netloc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context_args = {}
        if args.auth:
            context_args["storage_state"] = args.auth

        context = browser.new_context(**context_args)
        page = context.new_page()

        while queue and len(visited) < args.max_pages:
            url, parent = queue.popleft()
            url = normalize_url(url)

            if url in visited:
                continue
            visited.add(url)

            try:
                page.goto(url, timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass # Ignore networkidle timeout if it still loads some assets

                # Custom wait as requested by user
                if args.wait > 0:
                    page.wait_for_timeout(args.wait * 1000)

                title = page.title()
                h1 = page.locator("h1").all_text_contents()

                links = page.locator("a[href]").evaluate_all("""
                    els => els.map(a => a.getAttribute("href"))
                """)

                filename = slugify(url) + ".png"
                shot_path = os.path.join(shots_dir, filename)
                page.screenshot(path=shot_path, full_page=True)

                internal_links = []
                for href in links:
                    full = normalize_url(urljoin(url, href))
                    if is_internal(base, full):
                        internal_links.append(full)
                        if full not in visited:
                            queue.append((full, url))

                results.append({
                    "url": url,
                    "parent": parent,
                    "title": title,
                    "h1": h1,
                    "links": list(set(internal_links)),
                    "screenshot": shot_path,
                    "error": None
                })

                print(f"[OK] {url}")

            except Exception as e:
                print(f"[ERROR] {url} -> {e}")
                results.append({
                    "url": url,
                    "parent": parent,
                    "error": str(e)
                })

        with open(os.path.join(args.output, "pages.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        browser.close()

    print("\n✅ 완료")

if __name__ == "__main__":
    main()