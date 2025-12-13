import discord
from utils.systems.potion_system import PotionSystem
from components.views.potion_select_view import PotionSelectView

class UsePotionButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🧪 Use Potion", style=discord.ButtonStyle.green, custom_id="use_potion", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        potions = []
        inventory = await self.parent_view.bot.db.get_inventory(self.parent_view.user_id)
        
        for item_row in inventory:
            item_id = item_row['item_id']
            if item_id in PotionSystem.POTION_EFFECTS:
                item = await self.parent_view.bot.game_data.get_item(item_id)
                if item:
                    potions.append({
                        'item_id': item_id,
                        'name': item.name,
                        'rarity': getattr(item, 'rarity', 'COMMON')
                    })
        
        if not potions:
            await interaction.response.send_message("You don't have any potions!", ephemeral=True)
            return
        
        rarity_emojis = {
            'COMMON': '⬜',
            'UNCOMMON': '🟩',
            'RARE': '🟦',
            'EPIC': '🟪',
            'LEGENDARY': '🟧',
            'MYTHIC': '🟥'
        }
        
        embed = discord.Embed(
            title="🧪 Available Potions",
            description="Choose a potion to use:",
            color=discord.Color.green()
        )
        
        potion_list = []
        for i, potion in enumerate(potions[:20], 1):
            rarity_emoji = rarity_emojis.get(potion['rarity'], '⬜')
            effect = PotionSystem.POTION_EFFECTS.get(potion['item_id'], {})
            
            if effect.get('type') == 'instant_heal':
                effect_text = f"Heals {effect['amount']} HP"
            elif effect.get('type') == 'god':
                effect_text = "All stat bonuses!"
            else:
                stat_name = effect.get('stat', 'unknown').replace('_', ' ').title()
                effect_text = f"+{effect.get('amount', 0)} {stat_name}"
            
            potion_list.append(f"**{i}.** {rarity_emoji} {potion['name']}\n    {effect_text}")
        
        embed.add_field(
            name="Potions",
            value="\n".join(potion_list) if potion_list else "No potions available",
            inline=False
        )
        
        if len(potions) > 20:
            embed.set_footer(text=f"Showing 20 of {len(potions)} potions")
        
        view = PotionSelectView(self.parent_view.bot, self.parent_view.user_id, potions, self.parent_view)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
