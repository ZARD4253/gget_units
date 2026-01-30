from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# --- 설정 ---
TARGET_URL = "https://appmedia.jp/ggene_eternal/78850862"
OUTPUT_DIR = "02_raw_data"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(options=options)

print(f"[{TARGET_URL}] 무기 테이블 추출 시작...")

try:
    driver.get(TARGET_URL)
    print("⏳ 페이지 로딩 대기 중...")
    
    # 페이지 로딩 대기
    time.sleep(5)
    
    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # <table class="unit_list_table"> 찾기
    weapon_table = soup.find('table', class_='unit_list_table')
    
    if weapon_table:
        print("✅ unit_list_table 테이블 발견!")
        
        # 테이블의 행 개수 확인
        rows = weapon_table.find_all('tr')
        print(f"📊 총 {len(rows)}개의 행 발견")
        
        # 출력 디렉토리 생성
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        # HTML 파일로 저장
        output_file = f"{OUTPUT_DIR}/weapons.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 완전한 HTML 문서로 저장
            f.write('''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>武装一覧 - Gジェネエターナル</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #d32f2f;
            padding-bottom: 10px;
        }
        .unit_list_table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .unit_list_table th,
        .unit_list_table td {
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
        }
        .unit_list_table th {
            background-color: #f8f9fa;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .unit_list_table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .unit_list_table tr:hover {
            background-color: #f0f0f0;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            .unit_list_table {
                font-size: 12px;
            }
            .unit_list_table th,
            .unit_list_table td {
                padding: 6px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔫 武装一覧 (Weapons List)</h1>
        <p>取得日時: ''' + time.strftime("%Y-%m-%d %H:%M:%S") + '''</p>
        <p>元のURL: <a href="''' + TARGET_URL + '''" target="_blank">''' + TARGET_URL + '''</a></p>
        
''')
            
            # 테이블 내용 저장 (prettify로 보기 좋게)
            f.write(weapon_table.prettify())
            
            f.write('''
    </div>
</body>
</html>''')
        
        print(f"\n🎉 성공!")
        print(f"   파일 저장: {output_file}")
        print(f"   총 행 수: {len(rows)}")
        
        # 테이블 구조 미리보기
        print("\n📄 테이블 구조 미리보기:")
        print("="*80)
        
        # 헤더 출력
        header = weapon_table.find('tr')
        if header:
            headers = header.find_all(['th', 'td'])
            print("헤더:")
            for i, h in enumerate(headers):
                print(f"  {i+1}. {h.get_text().strip()}")
        
        # 첫 번째 데이터 행 출력
        data_rows = weapon_table.find_all('tr')[1:6]  # 처음 5개 행만
        print("\n첫 5개 데이터 행:")
        for idx, row in enumerate(data_rows):
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text().strip()[:30] for cell in cells]
            print(f"  행 {idx+1}: {' | '.join(cell_texts)}")
        
        print("="*80)
        
        # 원본 테이블만 저장 (스타일 없이)
        raw_output_file = f"{OUTPUT_DIR}/weapons_raw.html"
        with open(raw_output_file, 'w', encoding='utf-8') as f:
            f.write(str(weapon_table))
        
        print(f"\n📦 원본 테이블도 저장: {raw_output_file}")
        
    else:
        print("❌ unit_list_table 클래스를 가진 테이블을 찾을 수 없습니다!")
        
        # 다른 테이블들 찾기
        all_tables = soup.find_all('table')
        print(f"\n페이지에서 발견된 테이블 개수: {len(all_tables)}")
        
        for i, table in enumerate(all_tables[:5]):  # 처음 5개만
            classes = table.get('class', [])
            print(f"\n테이블 {i+1}:")
            print(f"  클래스: {classes}")
            print(f"  행 개수: {len(table.find_all('tr'))}")
            
        # 페이지 소스 일부 저장
        debug_file = f"{OUTPUT_DIR}/page_source_debug.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n🔍 디버그: 전체 페이지 소스 저장 → {debug_file}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n✅ 브라우저 종료")
