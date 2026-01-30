def parse_mechanism(target_block):
    mechanisms = []
    for table in target_block.find_all("table"):
        header = table.find("th", colspan="2")
        if header and "機構" in header.get_text():
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    name = cols[0].get_text(strip=True)
                    desc = cols[1].get_text(separator="\n", strip=True)
                    mechanisms.append({"name": name, "desc": desc})
            break
    return mechanisms if mechanisms else None