def parse_abilities(target_block, has_ssp):
    abilities = {"before_ssp": [], "after_ssp": []}

    def collect(container):
        result = []
        if not container:
            return result
        for table in container.find_all("table"):
            header = table.find("th")
            if header and "アビリティ" in header.get_text():
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        name = cols[0].get_text(" ", strip=True)
                        desc = cols[1].get_text(" ", strip=True)
                        result.append({"name": name, "desc": desc})
        return result

    if has_ssp:
        # select_one → select 로 바꿔서 두 블록 모두 가져오기
        before_blocks = target_block.select("div.ssp_weapon_table[data-ssp='0']")
        after_blocks  = target_block.select("div.ssp_weapon_table[data-ssp='1']")
        for b in before_blocks:
            abilities["before_ssp"].extend(collect(b))
        for a in after_blocks:
            abilities["after_ssp"].extend(collect(a))
    else:
        abilities["before_ssp"] = collect(target_block)

    return abilities