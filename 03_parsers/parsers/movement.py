def parse_movement(target_block, custom_core):
    before_move = None
    after_move = None
    for row in target_block.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            if "移動力" in label:
                before_move = cells[1].get_text(strip=True)
                after_move = before_move
                break
    for core in custom_core:
        if "移動力" in core and "→" in core:
            parts = core.replace("移動力", "").split("→")
            if len(parts) == 2:
                before_move, after_move = parts[0].strip(), parts[1].strip()
    return {"before": before_move, "after": after_move}
    
    
    
    