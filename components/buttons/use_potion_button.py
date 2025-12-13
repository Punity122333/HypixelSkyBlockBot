import discord
from utils.systems.potion_system import PotionSystem

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
                    potions.append((item_id, item.name))
        
        if not potions:
            await interaction.response.send_message("You don't have any potions!", ephemeral=True)
            return
        
        class PotionSelect(discord.ui.Select):
            def __init__(self, potions_list, parent_button):
                self.parent_button = parent_button
                options = [
                    discord.SelectOption(label=name, value=potion_id)
                    for potion_id, name in potions_list[:25]
                ]
                super().__init__(placeholder="Choose a potion...", options=options)
            
            async def callback(self, interaction: discord.Interaction):
                potion_id = self.values[0]
                potion_effect = PotionSystem.POTION_EFFECTS.get(potion_id)
                
                if potion_effect and potion_effect.get('type') == 'instant_heal':
                    result = await PotionSystem.use_health_potion_in_combat(
                        self.parent_button.parent_view.bot.db,
                        self.parent_button.parent_view.user_id,
                        potion_id,
                        self.parent_button.parent_view.player_health,
                        self.parent_button.parent_view.player_max_health
                    )
                    
                    if result['success']:
                        self.parent_button.parent_view.player_health = result['new_health']
                        await interaction.response.send_message(
                            f"❤️ You used a health potion! Healed {result['heal_amount']} HP!",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            f"❌ {result['message']}",
                            ephemeral=True
                        )
                else:
                    result = await PotionSystem.use_potion(
                        self.parent_button.parent_view.bot.db,
                        self.parent_button.parent_view.user_id,
                        potion_id
                    )
                    
                    if result['success']:
                        if result.get('type') == 'god':
                            await interaction.response.send_message(
                                f"✨ You used a God Potion! All stat bonuses active for {result['duration']}s!",
                                ephemeral=True
                            )
                        else:
                            await interaction.response.send_message(
                                f"✨ You used the potion! +{result['amount']} {result['stat']} for {result['duration']}s",
                                ephemeral=True
                            )
                        self.parent_button.parent_view.player_stats = None
                    else:
                        await interaction.response.send_message(
                            f"❌ {result['message']}",
                            ephemeral=True
                        )
        
        view = discord.ui.View()
        view.add_item(PotionSelect(potions, self))
        await interaction.response.send_message("Select a potion to use:", view=view, ephemeral=True)
