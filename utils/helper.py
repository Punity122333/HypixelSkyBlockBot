from components.views.equipment_select_view import EquipmentSelectView
import discord
from utils.data.game_constants import MINION_DATA

async def get_minion_data_from_db(game_data_manager, minion_type: str):
    minion_data = await game_data_manager.get_minion_data(minion_type)
    if minion_data:
        return {
            'produces': minion_data['produces'],
            'speed': minion_data['base_speed'],
            'max_tier': minion_data['max_tier'],
            'category': minion_data['category']
        }
    return MINION_DATA.get(minion_type, {})


async def show_equipment_select(interaction: discord.Interaction, equipment_slot: str, item_types: list):
    bot = interaction.client
    user_id = interaction.user.id
    
    inventory = await bot.db.get_inventory(user_id)# type: ignore
    
    if not inventory:
        await interaction.response.send_message(
            f"❌ Your inventory is empty! Craft or buy items first.",
            ephemeral=True
        )
        return
    
    matching_items = []
    for item in inventory:
        game_item = await bot.db.get_game_item(item['item_id'])# type: ignore
        
        if game_item and game_item['item_type'] in item_types:
            matching_items.append({
                'slot': item['slot'],
                'item_id': item['item_id'],
                'name': game_item['name'],
                'rarity': game_item['rarity'],
                'amount': item.get('amount', 1)
            })
    
    if not matching_items:
        await interaction.response.send_message(
            f"❌ You don't have any {equipment_slot} items in your inventory!\n"
            f"Looking for types: {', '.join(item_types)}", 
            ephemeral=True
        )
        return
    
    view = EquipmentSelectView(bot, user_id, equipment_slot, matching_items)
    
    embed = discord.Embed(
        title=f"🎒 Select {equipment_slot.title()} to Equip",
        description=f"Choose an item from your inventory to equip\nFound {len(matching_items)} matching items\n\nClick 'Choose Item' and enter the number.",
        color=discord.Color.blue()
    )
    
    for idx, item in enumerate(matching_items):
        amount_text = f" (x{item['amount']})" if item.get('amount', 1) > 1 else ""
        embed.add_field(
            name=f"{idx+1}. {item['name']}{amount_text}",
            value=f"✨ {item['rarity']}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
