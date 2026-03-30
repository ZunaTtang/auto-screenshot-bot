# Web Screenshot Autobot

> Python + Playwright 기반 **CLI 웹 크롤러**
> 내부 링크를 BFS 방식으로 탐색하며 전체 화면 스크린샷을 자동으로 저장합니다.
> 로그인이 필요한 페이지도 세션 저장 기능으로 크롤링 가능합니다.

---

## 📋 필수 요구사항

| 항목 | 최소 버전 |
|---|---|
| Python | 3.9 이상 |
| pip | (Python과 함께 설치됨) |

Python이 설치되어 있지 않다면:
1. [python.org](https://www.python.org/downloads/) 에서 최신 버전을 다운로드합니다.
2. 설치 시 **"Add Python to PATH"** 를 반드시 체크합니다.

---

## 🚀 시작하기

<<<<<<< HEAD
### Windows
=======
윈도우 사용자라면 폴더 내의 **`실행.bat`** 파일을 더블 클릭하는 것이 가장 간편합니다.
맥(macOS) 또는 리눅스 사용자라면 터미널에서 **`실행.command`** 파일을 실행하세요.
>>>>>>> 05b3b285e873c74a5b1fd13cd91a4e9b099633d2

`실행.bat` 파일을 더블클릭하세요.

<<<<<<< HEAD
### macOS
=======
### 맥 / 리눅스 (macOS / Linux)
1. 터미널을 엽니다.
2. 해당 폴더로 이동한 후 다음 명령어를 입력하여 실행 권한을 부여합니다 (최초 1회).
   ```bash
   chmod +x 실행.command
   ```
3. 다음 명령어로 프로그램을 실행합니다.
   ```bash
   ./실행.command
   ```
>>>>>>> 05b3b285e873c74a5b1fd13cd91a4e9b099633d2

```bash
# 최초 1회: 실행 권한 부여
chmod +x 실행.command

# 실행 (더블클릭 또는 터미널에서)
./실행.command
```

### 직접 실행 (터미널)

<<<<<<< HEAD
```bash
python run.py
```

---

## 📦 수동 환경 설정 (선택)

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

또는 프로그램 실행 후 **메뉴 1번 (환경 구축)** 을 선택하면 자동으로 설치됩니다.

---

## 🗂 메뉴 설명

| 번호 | 메뉴 | 설명 |
|---|---|---|
| 1 | 환경 구축 | Playwright & Chromium 자동 설치 (최초 1회) |
| 2 | 로그인 세션 저장 | 브라우저에서 직접 로그인 → `auth.json` 저장 |
| 3 | 사이트 크롤링 | URL 입력 → BFS 탐색 → 스크린샷 + JSON 저장 |
| 4 | 스크린샷 폴더 열기 | `output/screenshots/` 폴더를 파일 탐색기로 열기 |
| 5 | 초기화 | `auth.json` 및 `output/` 폴더 전체 삭제 |
| 6 | 종료 | 프로그램 종료 |

---

## ⚙️ 크롤링 옵션 (메뉴 3 실행 시 입력)

| 옵션 | 기본값 | 설명 |
|---|---|---|
| 최대 페이지 수 | 30 | 이 수를 초과하면 크롤링을 중단합니다 |
| 대기 시간(초) | 2.0 | 페이지 로드 후 스크린샷 촬영 전 대기 시간 |
| 재시도 횟수 | 1 | 페이지 로드 실패 시 재시도 횟수 |
| 헤드리스 모드 | Y (숨김) | N 선택 시 브라우저 창이 화면에 나타납니다 |
| 서브도메인 제한 | N | Y 선택 시 정확히 같은 서브도메인만 크롤링합니다 |

> 동적 콘텐츠가 많은 사이트는 대기 시간을 **5~10초**로 설정하세요.

---

## 📁 프로젝트 구조

```
├── run.py              # 메인 CLI (여기서 실행)
├── crawl.py            # BFS 크롤러 + 스크린샷 엔진
├── save_auth.py        # 로그인 세션 저장
├── requirements.txt    # 의존성 목록
├── 실행.bat            # Windows 원클릭 실행 파일
├── 실행.command        # macOS 원클릭 실행 파일
├── auth.json           # 로그인 세션 (자동 생성, Git 제외)
└── output/             # 크롤링 결과 (자동 생성, Git 제외)
    ├── screenshots/    # 페이지별 스크린샷 (.png)
    ├── pages.json      # 크롤링 결과 요약 (URL, 상태코드, 제목 등)
    └── crawler.log     # 크롤링 상세 로그
```

---

## 📄 결과물 예시 (`pages.json`)

```json
[
  {
    "url": "https://example.com",
    "parent": null,
    "status": 200,
    "title": "Example Domain",
    "h1": ["Example Domain"],
    "links": ["https://example.com/about"],
    "screenshot": "output/screenshots/https_example_com_a1b2c3d4.png",
    "error": null
  }
]
```

---

## ⚠️ 주의사항

- `auth.json` 에는 로그인 쿠키 정보가 포함되어 있습니다. **절대 공개 저장소에 업로드하지 마세요.** (`.gitignore`에 포함되어 있습니다)
- 과도한 요청은 사이트에서 차단될 수 있습니다. 최대 페이지 수와 대기 시간을 적절히 설정하세요.
- 크롤링 범위는 시작 URL과 동일한 루트 도메인으로 자동 제한됩니다.
=======
- `실행.bat`: 윈도우용 원클릭 실행 파일 (권장)
- `실행.command`: 맥/리눅스용 실행 파일
- `run.py`: 통합 실행 스크립트
- `save_auth.py`: 로그인 세션 저장 전용 스크립트
- `crawl.py`: 사이트 탐색 및 스크린샷 캡처 핵심 엔진
- `auth.json`: 저장된 로그인 세션 정보 (자동 생성)
- `output/`: 크롤링 결과(스크린샷 및 JSON 데이터)가 저장되는 폴더

## ⚠️ 주의사항

- 크롤링 중 브라우저 창이 보이지 않는 모드(Headless)로 작동하도록 설정되어 있습니다.
- 너무 많은 페이지를 크롤링할 경우 사이트 측에서 차단될 수 있으므로 적절한 `최대 페이지 수`를 설정하세요.
- 스크린샷이 제대로 찍히지 않는 경우 `대기 시간`을 5~10초 정도로 넉넉하게 설정해 보세요.
>>>>>>> 05b3b285e873c74a5b1fd13cd91a4e9b099633d2
