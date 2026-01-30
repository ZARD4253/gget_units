import json
import os

def convert_json_to_js():
    # 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, '04_processed_data')
    dest_dir = os.path.join(base_dir, '05_web', 'assets')
    
    # 목적지 폴더가 없으면 생성
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"📁 폴더 생성됨: {dest_dir}")
    
    # 변환 작업 목록 정의
    # (소스 JSON 파일명, 타겟 JS 파일명, JS 변수명)
    tasks = [
        # 일본어 데이터 - units_with_ids.json 사용 (ID 포함)
        ('units_with_ids.json', 'units_jp.js', 'rawUnits'),
        ('weapons.json', 'weapons_jp.js', 'rawWeapons'),
        
        # 한글 데이터
        ('units_kr.json', 'units_kr.js', 'rawUnits'),
        ('weapons_kr.json', 'weapons_kr.js', 'rawWeapons'),
    ]
    
    print("🔄 JSON -> JS 변환 시작...")
    
    for json_file, js_file, var_name in tasks:
        json_path = os.path.join(src_dir, json_file)
        js_path = os.path.join(dest_dir, js_file)
        
        # 소스 파일이 존재하는지 확인
        if not os.path.exists(json_path):
            print(f"⚠️ 경고: {json_file} 파일을 찾을 수 없어 건너뜁니다.")
            continue
        
        try:
            # JSON 읽기
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JS 내용 작성 (const 변수명 = 데이터;)
            # ensure_ascii=False를 해야 한글/일어가 깨지지 않고 그대로 보입니다.
            js_content = f"const {var_name} = {json.dumps(data, ensure_ascii=False, indent=2)};"
            
            # JS 쓰기
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            print(f"✅ 변환 완료: {json_file} -> {js_file} ({var_name})")
        
        except Exception as e:
            print(f"❌ 오류 발생 ({json_file}): {e}")
    
    print("🎉 모든 변환 작업이 완료되었습니다.")

if __name__ == "__main__":
    convert_json_to_js()
