import discord

class MinionUpgradeModal(discord.ui.Modal, title="Upgrade Minion"):
    minion_number = discord.ui.TextInput(
        label="Minion Number",
        placeholder="Enter the number of the minion you want to upgrade",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, minions):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.minions = minions
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            idx = int(self.minion_number.value) - 1
            if idx < 0 or idx >= len(self.minions):
                await interaction.response.send_message(
                    f"❌ Invalid minion number! Please choose between 1 and {len(self.minions)}.",
                    ephemeral=True
                )
                return
            
            minion = self.minions[idx]
            current_tier = minion['tier']
            
            minion_data = await self.bot.game_data.get_minion_data(minion['minion_type'])
            max_tier = minion_data['max_tier'] if minion_data else 11
            
            if current_tier >= max_tier:
                await interaction.response.send_message(
                    f"❌ This minion is already at max tier ({max_tier})!",
                    ephemeral=True
                )
                return
            
            upgrade_cost = 5000 * current_tier
            
            player = await self.bot.db.players.get_player(self.user_id)
            if player['coins'] < upgrade_cost:
                await interaction.response.send_message(
                    f"❌ You need {upgrade_cost:,} coins to upgrade this minion! (You have {player['coins']:,})",
                    ephemeral=True
                )
                return
            
            await self.bot.db.players.update_player(self.user_id, coins=player['coins'] - upgrade_cost)
            await self.bot.db.upgrade_minion(minion['id'])
            
            await interaction.response.send_message(
                f"✅ Successfully upgraded **{minion['minion_type'].title()} Minion** to Tier {current_tier + 1} for {upgrade_cost:,} coins!",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error upgrading minion: {str(e)}",
                ephemeral=True
            )
