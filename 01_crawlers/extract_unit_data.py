from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
import os

# --- 설정 ---
TARGET_URL = "https://appmedia.jp/ggene_eternal/78590855"
OUTPUT_DIR = "02_raw_data"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(options=options)

print(f"[{TARGET_URL}] unit_data 추출 시작...")

try:
    driver.get(TARGET_URL)
    print("⏳ 페이지 로딩 중...")
    
    # 페이지가 완전히 로드될 때까지 대기
    time.sleep(10)  # JavaScript 실행 시간 충분히 대기
    
    # 방법 1: window 객체에서 unit_data 변수 찾기
    print("\n📊 방법 1: window.unit_data 체크...")
    try:
        unit_data = driver.execute_script("return window.unit_data")
        if unit_data:
            print(f"✅ window.unit_data 발견! {len(unit_data)}개 항목")
            data_source = "window.unit_data"
        else:
            print("⚠️ window.unit_data가 비어있거나 없음")
            unit_data = None
    except Exception as e:
        print(f"⚠️ window.unit_data 접근 실패: {e}")
        unit_data = None
    
    # 방법 2: 페이지 소스에서 JavaScript 변수 찾기
    if not unit_data:
        print("\n📊 방법 2: 페이지 소스에서 검색...")
        page_source = driver.page_source
        
        # var unit_data = [...] 패턴 찾기
        if "var unit_data" in page_source or "let unit_data" in page_source or "const unit_data" in page_source:
            print("✅ unit_data 변수 선언 발견!")
            
            # JavaScript를 실행해서 데이터 가져오기
            try:
                unit_data = driver.execute_script("""
                    // 여러 가능성 시도
                    if (typeof unit_data !== 'undefined') return unit_data;
                    if (typeof window.unit_data !== 'undefined') return window.unit_data;
                    
                    // 전역 변수 검색
                    for (let key in window) {
                        if (key.includes('unit') && Array.isArray(window[key])) {
                            return window[key];
                        }
                    }
                    return null;
                """)
                
                if unit_data:
                    print(f"✅ 데이터 추출 성공! {len(unit_data)}개 항목")
                    data_source = "JavaScript execution"
                else:
                    print("❌ 데이터 추출 실패")
            except Exception as e:
                print(f"❌ JavaScript 실행 오류: {e}")
        else:
            print("❌ unit_data 변수를 찾을 수 없습니다")
    
    # 방법 3: 다양한 변수명 시도
    if not unit_data:
        print("\n📊 방법 3: 다양한 변수명 시도...")
        possible_names = [
            'unitData', 'units', 'UNIT_DATA', 'unitList', 
            'mechanicData', 'machineData', 'msData', 
            'unit_list', 'unitdata'
        ]
        
        for var_name in possible_names:
            try:
                result = driver.execute_script(f"return window.{var_name}")
                if result and isinstance(result, list) and len(result) > 0:
                    unit_data = result
                    data_source = f"window.{var_name}"
                    print(f"✅ {var_name} 발견! {len(unit_data)}개 항목")
                    break
            except:
                continue
    
    # 방법 4: 모든 전역 변수 검사
    if not unit_data:
        print("\n📊 방법 4: 모든 전역 배열 변수 검색...")
        try:
            all_arrays = driver.execute_script("""
                let arrays = {};
                for (let key in window) {
                    try {
                        if (Array.isArray(window[key]) && window[key].length > 10) {
                            arrays[key] = {
                                length: window[key].length,
                                sample: window[key][0]
                            };
                        }
                    } catch(e) {}
                }
                return arrays;
            """)
            
            print("\n발견된 배열 변수들:")
            for key, info in all_arrays.items():
                print(f"  - {key}: {info['length']}개 항목")
                print(f"    샘플: {str(info['sample'])[:100]}...")
                
            if all_arrays:
                # 가장 큰 배열을 선택
                largest_key = max(all_arrays.keys(), key=lambda k: all_arrays[k]['length'])
                unit_data = driver.execute_script(f"return window.{largest_key}")
                data_source = f"window.{largest_key} (auto-detected)"
                print(f"\n✅ 자동 선택: {largest_key} ({len(unit_data)}개 항목)")
        except Exception as e:
            print(f"❌ 전역 변수 검색 실패: {e}")
    
    # 결과 저장
    if unit_data and len(unit_data) > 0:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        # JSON 파일로 저장
        output_file = f"{OUTPUT_DIR}/unit_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unit_data, f, ensure_ascii=False, indent=2)
        
        # JavaScript 파일로도 저장
        js_output_file = f"{OUTPUT_DIR}/unit_data.js"
        with open(js_output_file, 'w', encoding='utf-8') as f:
            f.write("var unit_data = ")
            json.dump(unit_data, f, ensure_ascii=False, indent=2)
            f.write(";")
        
        print(f"\n🎉 성공!")
        print(f"   데이터 소스: {data_source}")
        print(f"   총 {len(unit_data)}개 유닛 데이터 추출")
        print(f"   JSON 파일: {output_file}")
        print(f"   JS 파일: {js_output_file}")
        
        # 샘플 데이터 출력
        print(f"\n📄 샘플 데이터 (첫 번째 항목):")
        print(json.dumps(unit_data[0], ensure_ascii=False, indent=2))
        
    else:
        print("\n❌ unit_data를 찾을 수 없습니다!")
        print("\n페이지 소스 일부:")
        print("="*80)
        # script 태그 내용 출력
        scripts = driver.find_elements("tag name", "script")
        for i, script in enumerate(scripts[:5]):  # 첫 5개만
            src = script.get_attribute("src")
            if src:
                print(f"\nScript {i+1}: {src}")
            else:
                content = script.get_attribute("innerHTML")
                if content and len(content) > 100:
                    print(f"\nInline Script {i+1} (처음 500자):")
                    print(content[:500])
        print("="*80)

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n✅ 브라우저 종료")
