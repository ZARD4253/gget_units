import requests
from bs4 import BeautifulSoup
from parsers.weapons import extract_weapons, has_map_weapon   # ← has_map_weapon 추가
from parsers.movement import parse_movement
from parsers.terrain import parse_terrain
from parsers.abilities import parse_abilities
from parsers.mechanism import parse_mechanism

def parse_unit(url, unit_name, rarity, unit_type, obtain_method, base_terrain):
    print(f"[INFO] {unit_name} ({rarity}/{obtain_method}/{unit_type}) 파싱 시작...")

    res = requests.get(url)
    if res.status_code != 200:
        print(f"[ERROR] {unit_name} 페이지 요청 실패: {res.status_code}")
        return {
            "weapons": [],
            "ssp": None,
            "movement": {"before": None, "after": None},
            "terrain": {"before": base_terrain, "after": base_terrain},
            "abilities": {"before_ssp": [], "after_ssp": []},
            "mechanism": None,
            "map_weapon": {"before": False, "after": False}
        }

    soup = BeautifulSoup(res.text, "html.parser")

    target_block = None
    for div in soup.select("div.same_unit_table"):
        target = div.get("data-target", "")
        if rarity in target and unit_type in target and obtain_method in target:
            target_block = div
            break

    if not target_block:
        print(f"[WARN] {unit_name} → 해당 블록을 찾지 못함")
        return {
            "weapons": [],
            "ssp": None,
            "movement": {"before": None, "after": None},
            "terrain": {"before": base_terrain, "after": base_terrain},
            "abilities": {"before_ssp": [], "after_ssp": []},
            "mechanism": None,
            "map_weapon": {"before": False, "after": False}
        }

    ssp_section = target_block.select_one("table.custom_core_table")
    custom_core = []
    if ssp_section:
        for row in ssp_section.select("tr")[1:]:
            cols = row.find_all("td")
            if cols:
                text = cols[-1].get_text(separator="\n", strip=True)
                lines = [line for line in text.split("\n") if line]
                custom_core.extend(lines)

    if rarity == "UR" or not ssp_section:
        weapons = extract_weapons(target_block)
        movement = parse_movement(target_block, [])
        terrain = {"before": base_terrain, "after": base_terrain}
        abilities = parse_abilities(target_block, has_ssp=False)
        mechanism = parse_mechanism(target_block)
        return {
            "weapons": weapons,
            "ssp": None,
            "movement": movement,
            "terrain": terrain,
            "abilities": abilities,
            "mechanism": mechanism,
            "map_weapon": {
                "before": has_map_weapon(weapons),
                "after": has_map_weapon(weapons)  # SSP 없는 경우 before=after 동일
            }
        }
    else:
        before_ssp = extract_weapons(target_block.select_one("div.ssp_weapon_table[data-ssp='0']"))
        after_ssp  = extract_weapons(target_block.select_one("div.ssp_weapon_table[data-ssp='1']"))
        movement   = parse_movement(target_block, custom_core)
        terrain    = parse_terrain(base_terrain, custom_core)
        abilities  = parse_abilities(target_block, has_ssp=True)
        mechanism  = parse_mechanism(target_block)

        return {
            "weapons": {"before_ssp": before_ssp, "after_ssp": after_ssp},
            "ssp": {"custom_core": custom_core},
            "movement": movement,
            "terrain": terrain,
            "abilities": abilities,
            "mechanism": mechanism,
            "map_weapon": {
                "before": has_map_weapon(before_ssp),
                "after": has_map_weapon(after_ssp)
            }
        }