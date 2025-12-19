async def format_enchantments_display(db, inventory_item_id: int) -> str:
    enchantments = await db.get_item_enchantments(inventory_item_id)
    
    if not enchantments:
        return ""
    
    enchant_lines = []
    for enchant in enchantments:
        enchant_data = await db.get_enchantment(enchant['enchantment_id'])
        if enchant_data:
            level_roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
            level_str = level_roman[enchant['level'] - 1] if enchant['level'] <= 10 else str(enchant['level'])
            enchant_lines.append(f"✨ {enchant_data['name']} {level_str}")
    
    return '\n'.join(enchant_lines) if enchant_lines else ""


async def format_enchantment_stats_display(db, inventory_item_id: int) -> str:
    enchantments = await db.get_item_enchantments(inventory_item_id)
    
    if not enchantments:
        return ""
    
    total_stats = {}
    for enchant in enchantments:
        enchant_data = await db.get_enchantment(enchant['enchantment_id'])
        if enchant_data and 'stat_bonuses' in enchant_data:
            stat_bonuses = enchant_data['stat_bonuses']
            for stat, value in stat_bonuses.items():
                bonus = value * enchant['level']
                total_stats[stat] = total_stats.get(stat, 0) + bonus
    
    if not total_stats:
        return ""
    
    stat_lines = []
    for stat, value in list(total_stats.items())[:3]:
        stat_lines.append(f"+{int(value)} {stat.replace('_', ' ').title()}")
    
    return '\n'.join(stat_lines)
