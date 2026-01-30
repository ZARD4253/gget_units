# GGEN Eternal Crawler

기동戦士ガンダム U.C. ENGAGE (G제네 이터널) 유닛 데이터 크롤링 및 번역 프로젝트

## 📋 프로젝트 구조

```
ggen-eternal-crawler/
├── 01_crawlers/          # 크롤링 스크립트
├── 02_raw_data/          # 크롤링 원본 데이터
├── 03_parsers/           # 파싱 및 번역 스크립트
│   └── translation_dicts/
├── 04_processed_data/    # 처리된 JSON 데이터
└── 05_web/              # 웹용 JS 파일
    └── assets/
```

## 🚀 사용 방법

### 1. 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 전체 파이프라인 실행
python run_pipeline.py
```

### 2. GitHub Actions 수동 실행

1. GitHub 저장소의 **Actions** 탭으로 이동
2. **Update Game Data** 선택
3. **Run workflow** 버튼 클릭
4. 결과는 자동으로 커밋됨

## 📂 파이프라인 단계

1. **크롤링** - 유닛 및 무기 데이터 수집
2. **파싱** - HTML → JSON 변환
3. **ID 매칭** - 유닛과 무기 연결
4. **무기 JSON화** - 무기 데이터 구조화
5. **한글화** - 번역 사전 적용
6. **JS 변환** - 웹용 파일 생성

## 🌐 번역 시스템

### 번역 우선순위
1. **error_correction.json** - 데이터 오류 수정 (최우선)
2. **manual_translation.json** - 수동 번역 추가
3. **auto_translation.json** - 엑셀 자동 생성

### 번역 파일 위치
```
03_parsers/translation_dicts/
├── auto_translation.json          # 자동 생성 (엑셀)
├── manual_translation.json        # 수동 추가
├── error_correction.json          # 오류 수정
├── untranslated_units.json        # 번역 실패 목록
└── untranslated_weapons.json
```

## 📊 출력 파일

### JSON (04_processed_data/)
- `units.json` - 유닛 데이터 (일본어)
- `units_with_ids.json` - ID 포함 유닛 데이터
- `weapons.json` - 무기 데이터 (일본어)
- `units_kr.json` - 유닛 데이터 (한글)
- `weapons_kr.json` - 무기 데이터 (한글)

### JavaScript (05_web/assets/)
- `units_jp.js` - 유닛 데이터 (일본어)
- `weapons_jp.js` - 무기 데이터 (일본어)
- `units_kr.js` - 유닛 데이터 (한글)
- `weapons_kr.js` - 무기 데이터 (한글)

## 🔧 번역 개선 방법

1. `untranslated_units.json` 확인
2. `manual_translation.json`에 번역 추가
3. `error_correction.json`에 데이터 오류 수정
4. 다시 실행하여 번역 개선

## 📝 라이선스

MIT License

## 🤝 기여

이슈 및 PR 환영합니다!
