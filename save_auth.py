import argparse
from playwright.sync_api import sync_playwright

def main():
    parser = argparse.ArgumentParser(description="Save login session (auth.json)")
    parser.add_argument("--url", required=True, help="Login page URL")
    parser.add_argument("--output", default="auth.json", help="Output auth file")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(args.url)

        print("\n👉 브라우저에서 직접 로그인하세요.")
        input("로그인 완료 후 엔터를 누르세요... ")

        context.storage_state(path=args.output)
        print(f"\n✅ 세션 저장 완료: {args.output}")

        browser.close()

if __name__ == "__main__":
    main()