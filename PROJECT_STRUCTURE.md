# G Generation Eternal - 자동 데이터 크롤링 & 파싱 프로젝트

## 📁 권장 디렉토리 구조

```
ggen-eternal-crawler/
├── 01_crawlers/                    # 크롤링 스크립트들
│   ├── extract_unit_data.py        # AppMedia에서 unit_data.json 추출
│   ├── extract_weapons_table.py    # AppMedia에서 weapons 테이블 추출
│   └── extract_notices.py          # 네이버 게임 라운지 공지사항 크롤링
│
├── 02_raw_data/                    # 크롤링된 원본 데이터
│   ├── unit_data.json              # extract_unit_data.py 결과
│   ├── unit_data.js                # JavaScript 버전
│   ├── weapons_raw.html            # extract_weapons_table.py 결과
│   └── .gitkeep
│
├── 03_parsers/                     # 파싱 스크립트들
│   ├── main.py                     # 메인 실행 파일
│   ├── unit_parser.py              # 유닛 상세 파싱
│   └── parsers/                    # 모듈화된 파서들
│       ├── __init__.py
│       ├── weapons.py
│       ├── movement.py
│       ├── terrain.py
│       ├── abilities.py
│       └── mechanism.py
│
├── 04_processed_data/              # 최종 가공 데이터
│   ├── units.json                  # 최종 유닛 데이터
│   ├── weapons.json                # 최종 무기 데이터
│   └── units.js                    # JavaScript 버전 (웹 사용)
│
├── 05_web/                         # GitHub Pages용 웹 파일
│   ├── index.html                  # 공지사항 페이지
│   ├── feed.xml                    # RSS 피드
│   └── assets/
│       ├── units.js
│       └── weapons.js
│
├── .github/
│   └── workflows/
│       └── auto_update.yml         # GitHub Actions 자동화
│
├── requirements.txt                # Python 패키지 목록
├── config.json                     # 설정 파일
└── README.md                       # 프로젝트 설명
```

## 🔄 작업 흐름

### 1단계: 크롤링 (01_crawlers/)
```bash
# 1. AppMedia에서 unit_data 추출
python 01_crawlers/extract_unit_data.py
# → 02_raw_data/unit_data.json 생성

# 2. AppMedia에서 weapons 테이블 추출  
python 01_crawlers/extract_weapons_table.py
# → 02_raw_data/weapons_raw.html 생성

# 3. 네이버 라운지 공지사항 크롤링
python 01_crawlers/extract_notices.py
# → 05_web/index.html, feed.xml 생성
```

### 2단계: 파싱 (03_parsers/)
```bash
# unit_data.json → 상세 파싱
python 03_parsers/main.py
# → 04_processed_data/units.json 생성
```

### 3단계: 웹 배포용 파일 생성
```bash
# JSON → JS 변환
python convert_to_web.py
# → 05_web/assets/units.js, weapons.js 생성
```

## 📝 파일명 변경 사항

| 기존 | 변경 후 | 설명 |
|------|---------|------|
| `input.json` | `02_raw_data/unit_data.json` | 크롤링한 원본 데이터 |
| `output.json` | `04_processed_data/units.json` | 파싱 완료 데이터 |
| `weapons.html` | `02_raw_data/weapons_raw.html` | 무기 테이블 원본 |

## 🚀 GitHub Actions 자동화

매일 자정에 자동으로:
1. 크롤링 실행
2. 데이터 파싱
3. GitHub Pages 업데이트
4. 변경사항 자동 커밋

## 📦 필요 패키지

```txt
selenium==4.15.0
beautifulsoup4==4.12.0
requests==2.31.0
lxml==4.9.3
```

## ⚙️ 설정 파일 (config.json)

```json
{
  "urls": {
    "unit_data": "https://appmedia.jp/ggene_eternal/78590855",
    "weapons": "https://appmedia.jp/ggene_eternal/78850862",
    "notices": "https://game.naver.com/lounge/SD_Gundam_G_Generation_ETERNAL/board/22"
  },
  "output": {
    "raw_data_dir": "02_raw_data",
    "processed_data_dir": "04_processed_data",
    "web_dir": "05_web"
  }
}
```

## 🎯 다음 작업

1. ✅ 크롤러 스크립트 완성
2. ✅ 파서 스크립트 준비
3. ⬜ weapons 파싱 로직 추가
4. ⬜ weapon ID 매칭 로직
5. ⬜ GitHub Actions 설정
6. ⬜ 통합 실행 스크립트
