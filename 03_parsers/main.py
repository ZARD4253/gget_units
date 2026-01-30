import json
import os
import sys
from pathlib import Path

# 프로젝트 루트 기준 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "02_raw_data"
PROCESSED_DATA_DIR = PROJECT_ROOT / "04_processed_data"

# unit_parser 임포트
from unit_parser import parse_unit

def main():
    """
    메인 실행 함수
    - 입력: 02_raw_data/unit_data.json (AppMedia 크롤링 결과)
    - 출력: 04_processed_data/units.json (파싱 완료 데이터)
    """
    
    # 입력 파일 경로
    input_file = RAW_DATA_DIR / "unit_data.json"
    
    # 입력 파일 존재 확인
    if not input_file.exists():
        print(f"❌ 입력 파일을 찾을 수 없습니다: {input_file}")
        print(f"\n먼저 크롤러를 실행하세요:")
        print(f"  python 01_crawlers/extract_unit_data.py")
        sys.exit(1)
    
    # unit_data.json 읽기
    print(f"📖 입력 파일 로드: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        units = json.load(f)
    
    print(f"✅ 총 {len(units)}개 유닛 데이터 로드됨\n")
    
    # 파싱 시작
    results = []
    success_count = 0
    error_count = 0
    
    for idx, unit in enumerate(units, start=1):
        try:
            print(f"[{idx}/{len(units)}] {unit['name']} 처리 중...")
            
            parsed = parse_unit(
                unit["url"],
                unit["name"],
                unit["レアリティ"],
                unit["タイプ"],
                unit["入手タイプ"],
                unit["地形適正"]
            )
            
            unit_name = unit["name"]
            # SSP 데이터 부족 표시
            if parsed["ssp"] and parsed["ssp"].get("custom_core") is None:
                unit_name += " (데이터부족)"
            
            results.append({
                "unit_name": unit_name,
                "rarity": unit["レアリティ"],
                "obtain_method": unit["入手タイプ"],
                "type": unit["タイプ"],
                "weapons": parsed["weapons"],
                "ssp": parsed["ssp"],
                "movement": parsed["movement"],
                "terrain": parsed["terrain"],
                "abilities": parsed["abilities"],
                "mechanism": parsed["mechanism"],
                "map_weapon": parsed["map_weapon"],
                # 원본 필드 추가
                "icon": unit.get("icon"),
                "url": unit.get("url"),
                "タグ": unit.get("タグ"),
                "作品": unit.get("作品"),
                "ステータス": unit.get("ステータス"),
                "アビ込みステータス": unit.get("アビ込みステータス")
            })
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
            error_count += 1
            continue
    
    # 출력 디렉토리 생성
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 결과 저장
    output_file = PROCESSED_DATA_DIR / "units.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 요약 출력
    print("\n" + "="*60)
    print("📊 파싱 완료 요약")
    print("="*60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"📁 출력 파일: {output_file}")
    print("="*60)

if __name__ == "__main__":
    main()
