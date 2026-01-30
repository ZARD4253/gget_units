import json
import pandas as pd
import re
from pathlib import Path

# ======================
# 경로 설정
# ======================
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "02_raw_data"
PROCESSED_DATA_DIR = PROJECT_ROOT / "04_processed_data"
TRANSLATION_DIR = PROJECT_ROOT / "03_parsers" / "translation_dicts"

# 입력 파일
UNITS_JSON = PROCESSED_DATA_DIR / "units_with_ids.json"
WEAPONS_JSON = PROCESSED_DATA_DIR / "weapons.json"
EXCEL_KO = RAW_DATA_DIR / "soshage_units_ko.xlsx"
EXCEL_JA = RAW_DATA_DIR / "soshage_units_ja.xlsx"

# 번역 사전 파일
AUTO_TRANSLATION = TRANSLATION_DIR / "auto_translation.json"
MANUAL_TRANSLATION = TRANSLATION_DIR / "manual_translation.json"
ERROR_CORRECTION = TRANSLATION_DIR / "error_correction.json"

# 출력 파일
OUTPUT_UNITS_KR = PROCESSED_DATA_DIR / "units_kr.json"
OUTPUT_WEAPONS_KR = PROCESSED_DATA_DIR / "weapons_kr.json"
UNTRANSLATED_UNITS = TRANSLATION_DIR / "untranslated_units.json"
UNTRANSLATED_WEAPONS = TRANSLATION_DIR / "untranslated_weapons.json"

# ======================
# 유틸 함수
# ======================
def normalize_name(name):
    """
    이름 정규화 (매칭용)
    - 괄호 제거: (EX), 【SSP】 등
    - 공백 제거
    - 특수문자 제거
    """
    if not name or pd.isna(name):
        return ""
    
    name = str(name)
    # 괄호와 내용물 제거
    name = re.sub(r'[\(（].*?[\)）]', '', name)
    name = re.sub(r'[【】\[\]]', '', name)
    # 공백 제거
    name = re.sub(r'\s+', '', name)
    # 특수문자 제거
    name = re.sub(r'[・･]', '', name)
    
    return name.strip()

def safe_str(val):
    """NaN 처리"""
    if pd.isna(val):
        return ""
    return str(val).strip()

# ======================
# 엑셀 파일 변경 감지
# ======================
def check_excel_modified():
    """
    엑셀 파일이 변경되었는지 확인
    auto_translation.json과 비교
    """
    if not AUTO_TRANSLATION.exists():
        return True  # auto_translation.json 없으면 새로 생성
    
    # auto_translation.json 수정 시간
    auto_mtime = AUTO_TRANSLATION.stat().st_mtime
    
    # 엑셀 파일 수정 시간
    excel_ko_mtime = EXCEL_KO.stat().st_mtime if EXCEL_KO.exists() else 0
    excel_ja_mtime = EXCEL_JA.stat().st_mtime if EXCEL_JA.exists() else 0
    
    # 엑셀이 auto_translation.json보다 최신이면 True
    if excel_ko_mtime > auto_mtime or excel_ja_mtime > auto_mtime:
        return True
    
    return False

# ======================
# 엑셀에서 auto_translation.json 생성
# ======================
def build_auto_translation():
    """
    엑셀 파일들을 읽어서 auto_translation.json 생성
    """
    print("📖 엑셀 파일 로드 중...")
    
    ko_df = pd.read_excel(EXCEL_KO)
    ja_df = pd.read_excel(EXCEL_JA)
    
    print(f"   한글: {len(ko_df)}개 행")
    print(f"   일본어: {len(ja_df)}개 행")
    
    auto_dict = {
        "units": {},
        "weapons": {},
        "ability_terms": {}
    }
    
    # 정규화된 이름으로도 검색 가능하도록
    normalized_map = {
        "units": {},
        "weapons": {},
        "ability_terms": {}
    }
    
    print("\n🔄 auto_translation.json 생성 중...")
    
    for i in range(min(len(ko_df), len(ja_df))):
        # 유닛명
        ja_unit = safe_str(ja_df.iloc[i]['Unit_Name_0_ja'])
        ko_unit = safe_str(ko_df.iloc[i]['Unit_Name'])
        
        if ja_unit and ko_unit:
            auto_dict["units"][ja_unit] = ko_unit
            normalized_map["units"][normalize_name(ja_unit)] = ko_unit
        
        # 무기명 (1~7)
        for w in range(1, 8):
            ja_col = f'Weapon_Name_ja_{w}'
            ko_col = f'Weapons_{w}'
            
            if ja_col in ja_df.columns and ko_col in ko_df.columns:
                ja_weapon = safe_str(ja_df.iloc[i][ja_col])
                ko_weapon = safe_str(ko_df.iloc[i][ko_col])
                
                if ja_weapon and ko_weapon:
                    auto_dict["weapons"][ja_weapon] = ko_weapon
                    normalized_map["weapons"][normalize_name(ja_weapon)] = ko_weapon
        
        # 어빌리티명 (1~4) → ability_terms로 통합
        for a in range(1, 5):
            ja_col = f'Ability_Name_ja_{a}'
            ko_col = f'Ability_Name_{a}'
            
            if ja_col in ja_df.columns and ko_col in ko_df.columns:
                ja_ability = safe_str(ja_df.iloc[i][ja_col])
                ko_ability = safe_str(ko_df.iloc[i][ko_col])
                
                if ja_ability and ko_ability:
                    auto_dict["ability_terms"][ja_ability] = ko_ability
                    normalized_map["ability_terms"][normalize_name(ja_ability)] = ko_ability
        
        # 어빌리티 설명 (1~4) → ability_terms로 통합
        for a in range(1, 5):
            ja_col = f'Ability_Description_ja_{a}'
            ko_col = f'Ability_Description_{a}'
            
            if ja_col in ja_df.columns and ko_col in ko_df.columns:
                ja_desc = safe_str(ja_df.iloc[i][ja_col])
                ko_desc = safe_str(ko_df.iloc[i][ko_col])
                
                if ja_desc and ko_desc:
                    auto_dict["ability_terms"][ja_desc] = ko_desc
    
    print(f"   유닛: {len(auto_dict['units'])}개")
    print(f"   무기: {len(auto_dict['weapons'])}개")
    print(f"   어빌리티 용어: {len(auto_dict['ability_terms'])}개")
    
    return auto_dict, normalized_map

# ======================
# 번역 사전 로드
# ======================
def load_translation_dicts():
    """
    번역 사전 파일들 로드 (없으면 빈 딕셔너리)
    """
    print("\n📚 번역 사전 로드 중...")
    
    TRANSLATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # 엑셀 파일 변경 확인
    excel_modified = check_excel_modified()
    
    if excel_modified:
        print("   🔄 엑셀 파일 변경 감지 → auto_translation.json 재생성")
        # auto_translation.json 생성
        auto_dict, normalized_map = build_auto_translation()
        
        # auto_translation.json 저장
        with open(AUTO_TRANSLATION, 'w', encoding='utf-8') as f:
            json.dump(auto_dict, f, ensure_ascii=False, indent=2)
        print(f"   ✅ {AUTO_TRANSLATION} 생성됨")
    else:
        print("   ⚡ 엑셀 파일 변경 없음 → 기존 auto_translation.json 사용")
        # 기존 auto_translation.json 로드
        with open(AUTO_TRANSLATION, 'r', encoding='utf-8') as f:
            auto_dict = json.load(f)
        
        # normalized_map 재생성 (필요시)
        normalized_map = {
            "units": {},
            "weapons": {},
            "ability_terms": {}
        }
        for unit_ja, unit_ko in auto_dict.get("units", {}).items():
            normalized_map["units"][normalize_name(unit_ja)] = unit_ko
        for weapon_ja, weapon_ko in auto_dict.get("weapons", {}).items():
            normalized_map["weapons"][normalize_name(weapon_ja)] = weapon_ko
        for term_ja, term_ko in auto_dict.get("ability_terms", {}).items():
            normalized_map["ability_terms"][normalize_name(term_ja)] = term_ko
        
        print(f"   ✅ {AUTO_TRANSLATION} 로드됨")
    
    # manual_translation.json 로드 (없으면 빈 딕셔너리)
    if MANUAL_TRANSLATION.exists():
        with open(MANUAL_TRANSLATION, 'r', encoding='utf-8') as f:
            manual_dict = json.load(f)
        print(f"   ✅ {MANUAL_TRANSLATION} 로드됨")
    else:
        manual_dict = {"units": {}, "weapons": {}, "ability_terms": {}}
        with open(MANUAL_TRANSLATION, 'w', encoding='utf-8') as f:
            json.dump(manual_dict, f, ensure_ascii=False, indent=2)
        print(f"   📝 {MANUAL_TRANSLATION} 생성됨 (빈 파일)")
    
    # error_correction.json 로드 (없으면 빈 딕셔너리)
    if ERROR_CORRECTION.exists():
        with open(ERROR_CORRECTION, 'r', encoding='utf-8') as f:
            error_dict = json.load(f)
        print(f"   ✅ {ERROR_CORRECTION} 로드됨")
    else:
        error_dict = {"units": {}, "weapons": {}}
        with open(ERROR_CORRECTION, 'w', encoding='utf-8') as f:
            json.dump(error_dict, f, ensure_ascii=False, indent=2)
        print(f"   📝 {ERROR_CORRECTION} 생성됨 (빈 파일)")
    
    return auto_dict, manual_dict, error_dict, normalized_map

# ======================
# 치환 번역 함수
# ======================
def translate_text(text, auto_dict, manual_dict):
    """
    텍스트를 치환 방식으로 번역
    1. manual 우선 적용
    2. auto 적용
    """
    if not text or pd.isna(text):
        return text, False
    
    text = str(text)
    original_text = text
    
    # 통합 딕셔너리 생성 (manual이 auto보다 우선)
    combined_terms = {**auto_dict, **manual_dict}
    
    # 긴 것부터 치환 (중요!)
    sorted_terms = sorted(
        combined_terms.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )
    
    for ja_term, ko_term in sorted_terms:
        text = text.replace(ja_term, ko_term)
    
    # 번역 성공 여부 (원문과 다르면 성공)
    translated = (text != original_text)
    
    return text, translated

# ======================
# 유닛 번역
# ======================
def translate_units(auto_dict, manual_dict, error_dict, normalized_map):
    """
    units_with_ids.json → units_kr.json
    """
    print("\n📝 유닛 데이터 번역 중...")
    
    with open(UNITS_JSON, 'r', encoding='utf-8') as f:
        units = json.load(f)
    
    translated_units = []
    untranslated_list = []
    
    stats = {
        "total": len(units),
        "error_corrected": 0,
        "unit_name_translated": 0,
        "unit_name_failed": 0,
        "ability_translated": 0,
        "ability_failed": 0
    }
    
    for unit in units:
        unit_name_ja = unit.get('unit_name', '')
        
        # 1️⃣ error_correction에 있으면 완전 교체
        if unit_name_ja in error_dict.get("units", {}):
            translated_units.append(error_dict["units"][unit_name_ja])
            stats["error_corrected"] += 1
            print(f"   🔧 에러 수정 적용: {unit_name_ja}")
            continue
        
        # 2️⃣ 복사본 생성
        translated_unit = unit.copy()
        untranslated_info = {
            "unit_name_ja": unit_name_ja,
            "unit_name_translated": False,
            "untranslated_abilities": []
        }
        
        # 3️⃣ 유닛명 번역 (manual → auto → 정규화)
        if unit_name_ja in manual_dict.get("units", {}):
            translated_unit["unit_name"] = manual_dict["units"][unit_name_ja]
            stats["unit_name_translated"] += 1
        elif unit_name_ja in auto_dict.get("units", {}):
            translated_unit["unit_name"] = auto_dict["units"][unit_name_ja]
            stats["unit_name_translated"] += 1
        else:
            # 정규화 매칭 시도
            normalized = normalize_name(unit_name_ja)
            if normalized in normalized_map["units"]:
                translated_unit["unit_name"] = normalized_map["units"][normalized]
                stats["unit_name_translated"] += 1
            else:
                translated_unit["unit_name"] = unit_name_ja
                stats["unit_name_failed"] += 1
                untranslated_info["unit_name_translated"] = False
        
        if translated_unit["unit_name"] != unit_name_ja:
            untranslated_info["unit_name_translated"] = True
        
        # 4️⃣ 어빌리티 번역 (치환 방식)
        if 'abilities' in translated_unit:
            abilities = translated_unit['abilities']
            
            # before_ssp
            if 'before_ssp' in abilities and abilities['before_ssp']:
                for ability in abilities['before_ssp']:
                    original_name = ability.get('name', '')
                    original_desc = ability.get('description', '')
                    
                    # 이름 번역
                    translated_name, name_success = translate_text(
                        original_name,
                        auto_dict.get('ability_terms', {}),
                        manual_dict.get('ability_terms', {})
                    )
                    ability['name'] = translated_name
                    
                    # 설명 번역
                    translated_desc, desc_success = translate_text(
                        original_desc,
                        auto_dict.get('ability_terms', {}),
                        manual_dict.get('ability_terms', {})
                    )
                    ability['description'] = translated_desc
                    
                    if name_success or desc_success:
                        stats["ability_translated"] += 1
                    else:
                        stats["ability_failed"] += 1
                        untranslated_info["untranslated_abilities"].append({
                            "name_ja": original_name,
                            "description_ja": original_desc
                        })
            
            # after_ssp
            if 'after_ssp' in abilities and abilities['after_ssp']:
                for ability in abilities['after_ssp']:
                    original_name = ability.get('name', '')
                    original_desc = ability.get('description', '')
                    
                    # 이름 번역
                    translated_name, name_success = translate_text(
                        original_name,
                        auto_dict.get('ability_terms', {}),
                        manual_dict.get('ability_terms', {})
                    )
                    ability['name'] = translated_name
                    
                    # 설명 번역
                    translated_desc, desc_success = translate_text(
                        original_desc,
                        auto_dict.get('ability_terms', {}),
                        manual_dict.get('ability_terms', {})
                    )
                    ability['description'] = translated_desc
                    
                    if name_success or desc_success:
                        stats["ability_translated"] += 1
                    else:
                        stats["ability_failed"] += 1
                        untranslated_info["untranslated_abilities"].append({
                            "name_ja": original_name,
                            "description_ja": original_desc
                        })
        
        translated_units.append(translated_unit)
        
        # 번역 실패한 항목 기록
        if not untranslated_info["unit_name_translated"] or untranslated_info["untranslated_abilities"]:
            # 전체 유닛 정보 포함
            untranslated_full = translated_unit.copy()
            untranslated_full["_translation_info"] = untranslated_info
            untranslated_list.append(untranslated_full)
    
    print(f"\n   📊 번역 통계:")
    print(f"      총 유닛: {stats['total']}개")
    print(f"      에러 수정: {stats['error_corrected']}개")
    print(f"      유닛명 번역 성공: {stats['unit_name_translated']}개")
    print(f"      유닛명 번역 실패: {stats['unit_name_failed']}개")
    print(f"      어빌리티 번역 성공: {stats['ability_translated']}개")
    print(f"      어빌리티 번역 실패: {stats['ability_failed']}개")
    
    return translated_units, untranslated_list

# ======================
# 무기 번역
# ======================
def translate_weapons(auto_dict, manual_dict, error_dict, normalized_map):
    """
    weapons.json → weapons_kr.json
    """
    print("\n🔫 무기 데이터 번역 중...")
    
    with open(WEAPONS_JSON, 'r', encoding='utf-8') as f:
        weapons = json.load(f)
    
    translated_weapons = []
    untranslated_list = []
    
    stats = {
        "total": len(weapons),
        "error_corrected": 0,
        "translated": 0,
        "failed": 0
    }
    
    for weapon in weapons:
        weapon_name_ja = weapon.get('name', '')
        
        # 1️⃣ error_correction에 있으면 완전 교체
        if weapon_name_ja in error_dict.get("weapons", {}):
            translated_weapons.append(error_dict["weapons"][weapon_name_ja])
            stats["error_corrected"] += 1
            continue
        
        # 2️⃣ 복사본 생성
        translated_weapon = weapon.copy()
        
        # 3️⃣ 무기명 번역 (manual → auto → 정규화)
        if weapon_name_ja in manual_dict.get("weapons", {}):
            translated_weapon["name"] = manual_dict["weapons"][weapon_name_ja]
            stats["translated"] += 1
        elif weapon_name_ja in auto_dict.get("weapons", {}):
            translated_weapon["name"] = auto_dict["weapons"][weapon_name_ja]
            stats["translated"] += 1
        else:
            # 정규화 매칭 시도
            normalized = normalize_name(weapon_name_ja)
            if normalized in normalized_map["weapons"]:
                translated_weapon["name"] = normalized_map["weapons"][normalized]
                stats["translated"] += 1
            else:
                translated_weapon["name"] = weapon_name_ja
                stats["failed"] += 1
                untranslated_list.append(translated_weapon)
        
        translated_weapons.append(translated_weapon)
    
    print(f"\n   📊 번역 통계:")
    print(f"      총 무기: {stats['total']}개")
    print(f"      에러 수정: {stats['error_corrected']}개")
    print(f"      번역 성공: {stats['translated']}개")
    print(f"      번역 실패: {stats['failed']}개")
    
    return translated_weapons, untranslated_list

# ======================
# 메인 실행
# ======================
def main():
    print("="*70)
    print("🌐 한글화 작업 시작")
    print("="*70)
    
    # 1. 번역 사전 로드
    auto_dict, manual_dict, error_dict, normalized_map = load_translation_dicts()
    
    # 2. 유닛 번역
    units_kr, untranslated_units = translate_units(
        auto_dict, manual_dict, error_dict, normalized_map
    )
    
    # 3. 무기 번역
    weapons_kr, untranslated_weapons = translate_weapons(
        auto_dict, manual_dict, error_dict, normalized_map
    )
    
    # 4. 저장
    print("\n💾 저장 중...")
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRANSLATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # 번역된 데이터 저장
    with open(OUTPUT_UNITS_KR, 'w', encoding='utf-8') as f:
        json.dump(units_kr, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {OUTPUT_UNITS_KR}")
    
    with open(OUTPUT_WEAPONS_KR, 'w', encoding='utf-8') as f:
        json.dump(weapons_kr, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {OUTPUT_WEAPONS_KR}")
    
    # 번역 실패 목록 저장
    with open(UNTRANSLATED_UNITS, 'w', encoding='utf-8') as f:
        json.dump(untranslated_units, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {UNTRANSLATED_UNITS} ({len(untranslated_units)}개)")
    
    with open(UNTRANSLATED_WEAPONS, 'w', encoding='utf-8') as f:
        json.dump(untranslated_weapons, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {UNTRANSLATED_WEAPONS} ({len(untranslated_weapons)}개)")
    
    print("\n" + "="*70)
    print("✅ 한글화 완료!")
    print("="*70)
    print("\n📝 다음 단계:")
    print("   1. untranslated_units.json 확인")
    print("   2. untranslated_weapons.json 확인")
    print("   3. manual_translation.json에 번역 추가")
    print("   4. error_correction.json에 오류 수정 추가")
    print("   5. 다시 실행하여 번역 개선")

if __name__ == "__main__":
    main()
