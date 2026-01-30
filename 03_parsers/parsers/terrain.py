def parse_terrain(base_terrain, custom_core):
    terrain = {"before": base_terrain.copy(), "after": base_terrain.copy()}
    for core in custom_core:
        if "適性" in core and "→" in core:
            for key in base_terrain.keys():
                if key in core:
                    parts = core.split("→")
                    if len(parts) == 2:
                        terrain["after"][key] = parts[1].strip()
    return terrain