import subprocess
import sys
import os

def run_script(script_path):
    """파이썬 스크립트를 실행하고 성공 여부를 반환합니다."""
    print(f"\n🚀 실행 중: {script_path}")
    
    # 현재 실행 중인 파이썬 인터프리터(sys.executable)를 사용하여 스크립트 실행
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ 성공: {script_path}")
        return True
    else:
        print(f"❌ 실패: {script_path} (Exit Code: {result.returncode})")
        return False

def main():
    # 프로젝트 루트 경로 (이 스크립트가 있는 곳)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 실행 순서 정의
    pipeline_steps = [
        # 1. 크롤링
        "01_crawlers/extract_unit_data.py",
        "01_crawlers/extract_weapons_table.py",
        
        # 2. 파싱 (기본)
        "03_parsers/main.py",
        
        # 3. ID 매칭
        "03_parsers/match_weapon_ids.py",
        
        # 4. 무기 JSON화
        "03_parsers/parse_weapons_to_json.py",
        
        # 5. 한글화
        "03_parsers/translate_to_korean.py",
        
        # 6. JS 변환 (최종)
        "convert_json_to_js.py"
    ]

    print("=========================================")
    print("🤖 GGEN Eternal Crawler Pipeline 시작")
    print("=========================================")

    for step in pipeline_steps:
        script_full_path = os.path.join(base_dir, step)
        
        # 파일 존재 확인
        if not os.path.exists(script_full_path):
            print(f"⛔ 파일 없음: {step}")
            print("파이프라인을 중단합니다.")
            sys.exit(1)

        # 스크립트 실행
        success = run_script(script_full_path)
        
        # 실패 시 파이프라인 중단
        if not success:
            print("\n⛔ 오류가 발생하여 파이프라인을 중단합니다.")
            sys.exit(1)

    print("\n=========================================")
    print("✨ 모든 작업이 성공적으로 완료되었습니다!")
    print("=========================================")

if __name__ == "__main__":
    main()