import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import GameDatabase
from utils.data.all_items import ALL_ITEMS

async def update_default_bazaar_prices():
    print("Updating default bazaar prices...")
    db = GameDatabase('skyblock.db')
    await db.initialize()
    
    count = 0
    for item_id, item in ALL_ITEMS.items():
        await db.add_game_item(
            item_id=item.id,
            name=item.name,
            rarity=item.rarity,
            item_type=item.type,
            stats=item.stats,
            lore=item.lore,
            special_ability=item.special_ability,
            craft_recipe=item.craft_recipe,
            npc_sell_price=item.npc_sell_price,
            collection_req=item.collection_req,
            default_bazaar_price=item.default_bazaar_price
        )
        count += 1
    
    print(f"Updated {count} items with default bazaar prices")
    await db.close()

if __name__ == '__main__':
    asyncio.run(update_default_bazaar_prices())
