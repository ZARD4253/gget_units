import json
from bs4 import BeautifulSoup
import hashlib
import os
from pathlib import Path

def make_hash_id(key_parts, length=8):
    raw = "_".join(key_parts)
    return "U" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:length]

# 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "02_raw_data"
PROCESSED_DATA_DIR = PROJECT_ROOT / "04_processed_data"

# JSON 로드 (units.json)
input_json = PROCESSED_DATA_DIR / "units.json"
with open(input_json, "r", encoding="utf-8") as f:
    units = json.load(f)

# HTML 로드 (weapons_raw.html)
input_html = RAW_DATA_DIR / "weapons_raw.html"
with open(input_html, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

rows = []
for tr in soup.select("tbody.unit_tbody tr"):
    img_tag = tr.find("img")
    src = img_tag["src"].strip() if img_tag else ""
    src_file = os.path.basename(src) if src else ""

    # 무장 div 여러 개 가져오기
    weapon_divs = tr.find_all("div", {"class": "weapon_effect_wrapper"})
    rarity = weapon_divs[0].get("data-rarity1", "").strip() if weapon_divs else ""
    unit_type = weapon_divs[0].get("data-type", "").strip() if weapon_divs else ""
    obtain = weapon_divs[0].get("data-name_type", "").strip() if weapon_divs else ""

    a_tag = tr.find("a")
    html_name = a_tag.get_text(strip=True) if a_tag else ""

    rows.append({
        "tr": tr,
        "weapon_divs": weapon_divs,
        "src_file": src_file,
        "rarity": rarity,
        "type": unit_type,
        "obtain": obtain,
        "html_name": html_name
    })

json_failures = []
html_failures = []

# 1️⃣ 아이콘 기준 자동 매칭
for i, unit in enumerate(units):
    name = unit.get("name", "").strip() or unit.get("unit_name", "").strip()
    icon = unit.get("icon", "").strip()
    icon_file = os.path.basename(icon) if icon else ""
    rarity = unit.get("rarity", "").strip()
    unit_type = unit.get("type", "").strip()
    obtain = unit.get("obtain_method", "").strip()

    if icon_file:
        match = next(
            (r for r in rows if r["src_file"] == icon_file),
            None
        )
        if match:
            unit_id = make_hash_id([icon_file, rarity, unit_type, obtain])
            unit["id"] = unit_id
            for div in match["weapon_divs"]:
                div["data-unit-id"] = unit_id   # <-- 무장 div에 data-unit-id 부여
            continue

    # 실패한 경우 기록
    json_failures.append({
        "index": i,
        "name": name,
        "icon_file": icon_file,
        "rarity": rarity,
        "type": unit_type,
        "obtain": obtain
    })

# HTML 실패 목록 (data-unit-id 없는 무장 div)
html_failures = [r for r in rows if not any(div.get("data-unit-id") for div in r["weapon_divs"])]

# 2️⃣ 이름 자동 매칭
for j in json_failures:
    candidates = [h for h in html_failures if h["html_name"] == j["name"]]
    if len(candidates) == 1:
        # 이름 동일 → 자동 매칭
        sel = candidates[0]
        unit_id = make_hash_id([sel["src_file"], sel["rarity"], sel["type"], sel["obtain"]])
        units[j["index"]]["id"] = unit_id
        for div in sel["weapon_divs"]:
            div["data-unit-id"] = unit_id
        print(f"[자동매칭] JSON({j['index']+1}) {j['name']} → ID={unit_id}")
    elif len(candidates) > 1:
        # 후보 여러 개 → 수동 선택
        print(f"\nJSON({j['index']+1}) {j['name']} icon={j['icon_file']} rarity={j['rarity']} type={j['type']} obtain={j['obtain']}")
        for k, row in enumerate(candidates, start=1):
            print(f"  {k}. HTML name={row['html_name']} rarity={row['rarity']} type={row['type']} obtain={row['obtain']} icon={row['src_file']}")
        choice = input("→ 매칭할 번호 입력: ")
        if choice.isdigit():
            sel = candidates[int(choice)-1]
            unit_id = make_hash_id([sel["src_file"], sel["rarity"], sel["type"], sel["obtain"]])
            units[j["index"]]["id"] = unit_id
            for div in sel["weapon_divs"]:
                div["data-unit-id"] = unit_id
            print(f"[수동매칭] JSON({j['index']+1}) {j['name']} → ID={unit_id}")

# 출력 디렉토리 생성
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 결과 저장
output_json = PROCESSED_DATA_DIR / "units_with_ids.json"
output_html = PROCESSED_DATA_DIR / "weapons_with_ids.html"

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(units, f, indent=4, ensure_ascii=False)

with open(output_html, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"\n✅ 완료!")
print(f"   출력: {output_json}")
print(f"   출력: {output_html}")
