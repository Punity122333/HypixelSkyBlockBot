import discord
from utils.systems.potion_system import PotionSystem

class PotionSelectModal(discord.ui.Modal, title="Use Potion"):
    potion_number = discord.ui.TextInput(
        label="Potion Number",
        placeholder="Enter the number of the potion you want to use",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, potions, parent_view):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.potions = potions
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            idx = int(self.potion_number.value) - 1
            if idx < 0 or idx >= len(self.potions):
                await interaction.response.send_message(
                    f"❌ Invalid potion number! Please choose between 1 and {len(self.potions)}.",
                    ephemeral=True
                )
                return
            
            potion = self.potions[idx]
            potion_id = potion['item_id']
            potion_effect = PotionSystem.POTION_EFFECTS.get(potion_id)
            
            if not potion_effect:
                await interaction.response.send_message(
                    "❌ Invalid potion!",
                    ephemeral=True
                )
                return
            
            if potion_effect.get('type') == 'instant_heal':
                if hasattr(self.parent_view, 'player_health') and self.parent_view.player_health is not None:
                    result = await PotionSystem.use_health_potion_in_combat(
                        self.bot.db,
                        self.user_id,
                        potion_id,
                        self.parent_view.player_health,
                        self.parent_view.player_max_health
                    )
                    
                    if result['success']:
                        self.parent_view.player_health = result['new_health']
                        await interaction.response.send_message(
                            f"❤️ You used **{potion['name']}**! Healed {result['heal_amount']} HP!",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            f"❌ {result['message']}",
                            ephemeral=True
                        )
                else:
                    result = await PotionSystem.use_potion(
                        self.bot.db,
                        self.user_id,
                        potion_id
                    )
                    
                    if result['success']:
                        embed = discord.Embed(
                            title="❤️ Health Potion Used!",
                            description=f"You consumed **{potion['name']}**!",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="Effect", value=f"Restores {result['amount']} HP (use in combat)", inline=True)
                        embed.set_footer(text="Health potions work instantly in combat!")
                        await interaction.response.send_message(embed=embed)
                    else:
                        await interaction.response.send_message(
                            f"❌ {result['message']}",
                            ephemeral=True
                        )
            else:
                result = await PotionSystem.use_potion(
                    self.bot.db,
                    self.user_id,
                    potion_id
                )
                
                if result['success']:
                    if result.get('type') == 'god':
                        duration_min = result['duration'] // 60
                        embed = discord.Embed(
                            title="✨ God Potion Activated!",
                            description=f"You consumed **{potion['name']}** and gained ALL stat bonuses!",
                            color=discord.Color.gold()
                        )
                        god_effects = PotionSystem.POTION_EFFECTS['god_potion']['effects']
                        effects_text = "\n".join([f"+{amt} {stat.replace('_', ' ').title()}" for stat, amt in list(god_effects.items())[:10]])
                        embed.add_field(name="Effects (showing 10)", value=effects_text, inline=False)
                        embed.add_field(name="Duration", value=f"{duration_min} minutes", inline=True)
                        embed.set_footer(text=f"Total: {len(god_effects)} stat bonuses active!")
                        await interaction.response.send_message(embed=embed)
                    else:
                        duration_min = result['duration'] // 60
                        stat_name = result['stat'].replace('_', ' ').title()
                        embed = discord.Embed(
                            title="🧪 Potion Used!",
                            description=f"You consumed **{potion['name']}** and gained a temporary buff!",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Effect", value=f"+{result['amount']} {stat_name}", inline=True)
                        embed.add_field(name="Duration", value=f"{duration_min} minutes", inline=True)
                        await interaction.response.send_message(embed=embed)
                    
                    if hasattr(self.parent_view, 'player_stats'):
                        self.parent_view.player_stats = None
                else:
                    await interaction.response.send_message(
                        f"❌ {result['message']}",
                        ephemeral=True
                    )
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number!",
                ephemeral=True
            )
