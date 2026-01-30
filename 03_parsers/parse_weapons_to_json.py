import json
from bs4 import BeautifulSoup
from pathlib import Path
import re

# ======================
# 경로 설정
# ======================
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "04_processed_data"

HTML_PATH = PROCESSED_DATA_DIR / "weapons_with_ids.html"
OUTPUT_JSON = PROCESSED_DATA_DIR / "weapons.json"

# ======================
# 유틸
# ======================
def safe_int(val):
    try:
        return int(val)
    except:
        return 0

def clean_text(txt):
    return re.sub(r"\s+", " ", txt).strip()

# ======================
# HTML 로드
# ======================
html = Path(HTML_PATH).read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

weapons = []

# ======================
# 무장 파싱
# ======================
for div in soup.select(".weapon_effect_wrapper"):
    unit_id = div.get("data-unit-id") or div.get("id") or ""
    
    # 무장명
    name_span = div.select_one(".weapon_name span")
    name = clean_text(name_span.text.replace("【", "").replace("】", "")) if name_span else ""
    
    # POWER
    pow_span = div.select_one(".weapon_pow span")
    power = safe_int(pow_span.text.replace(",", "")) if pow_span else 0
    
    # RANGE
    range_min = safe_int(div.get("data-range_min"))
    range_max = safe_int(div.get("data-range_max"))
    range_text = ""
    range_span = div.select_one(".weapon_range span")
    if range_span:
        range_text = clean_text(range_span.text)
    
    # 속성 (ビーム / 物理 / 射撃 / 格闘 / 覚醒 등)
    elements = []
    for e in div.select(".weapon_elem"):
        t = e.get("data-type")
        if t:
            elements.append(t)
    
    # MAP
    is_map = div.get("data-weapon_category") == "MAP兵器"
    map_type = div.get("data-map_weapon_type") or ""
    
    # SSP
    ssp_type = div.get("data-ssp_weapon") or "通常"
    is_ssp = ssp_type != "通常"
    
    # 효과 태그
    effect_tags = []
    if div.get("data-effect_tag"):
        effect_tags = [
            t.strip()
            for t in div["data-effect_tag"].split(",")
            if t.strip()
        ]
    
    # 효과 텍스트 (HTML 제거 버전)
    effect_div = div.select_one(".weapon_effect")
    effect_text = clean_text(effect_div.get_text(" ")) if effect_div else ""
    
    # % 수치 최대값
    percents = []
    if effect_div:
        percents = [int(p) for p in re.findall(r"(\d+)%", effect_div.text)]
    max_effect_percent = max(percents) if percents else 0
    
    weapon = {
        "unit_id": unit_id,
        "name": name,
        "power": power,
        "range": {
            "min": range_min,
            "max": range_max,
            "text": range_text
        },
        "elements": elements,
        "is_map": is_map,
        "map_type": map_type,
        "ssp": ssp_type,
        "is_ssp": is_ssp,
        "effect_tags": effect_tags,
        "effect_text": effect_text,
        "max_effect_percent": max_effect_percent
    }
    weapons.append(weapon)

# ======================
# JSON 저장
# ======================
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(weapons, f, ensure_ascii=False, indent=2)

print(f"✅ 무장 {len(weapons)}개 추출 완료 → {OUTPUT_JSON}")
