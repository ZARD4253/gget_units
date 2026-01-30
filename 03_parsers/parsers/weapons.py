def extract_weapons(container):
    weapons = []
    if not container:
        return weapons
    for w in container.select("div.weapon_container"):
        name = w.select_one("div.w_name").get_text(strip=True)
        attrs = [elem.get_text(strip=True) for elem in w.select("div.w_element div.weapon_elem")]

        # line2_wrapper 테이블에서 헤더-값 매칭
        table = w.select_one("div.line2_wrapper table")
        stats = {}
        if table:
            headers = [th.get_text(strip=True) for th in table.select("tr th")]
            values  = [td.get_text(strip=True) for td in table.select("tr td")]
            if len(headers) == len(values):
                stats = dict(zip(headers, values))

        # line3_wrapper 효과
        effects = []
        for e in w.select("div.line3_wrapper"):
            for li in e.find_all("li"):
                effects.append(li.get_text(strip=True))
            for td in e.find_all("td"):
                effects.append(td.get_text(strip=True))
            text = e.get_text(separator="\n", strip=True)
            for line in text.split("\n"):
                if line and line not in effects:
                    effects.append(line)

        weapons.append({
            "name": name,
            "attributes": attrs,
            "range": stats.get("射程"),
            "power": stats.get("パワー"),
            "en_cost": stats.get("EN"),
            "accuracy": stats.get("命中"),
            "critical": stats.get("クリティカル"),
            "effects": effects
        })
    return weapons


# MAP병기 여부 판정 함수 추가
def has_map_weapon(weapons):
    if not weapons:
        return False
    for w in weapons:
        # 이름이나 속성에 'MAP'이 들어가면 MAP병기로 판정
        if "MAP" in w.get("name", "") or any("MAP" in attr for attr in w.get("attributes", [])):
            return True
    return False