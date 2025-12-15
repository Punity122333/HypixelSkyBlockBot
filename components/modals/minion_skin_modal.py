import discord

class MinionSkinModal(discord.ui.Modal, title="Apply Skin to Minion"):
    minion_number = discord.ui.TextInput(
        label="Minion Number",
        placeholder="Enter the minion number",
        required=True,
        max_length=3
    )
    
    skin_number = discord.ui.TextInput(
        label="Skin Number",
        placeholder="Enter the skin number from your inventory",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, minions, skins):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.minions = minions
        self.skins = skins
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            minion_idx = int(self.minion_number.value) - 1
            skin_idx = int(self.skin_number.value) - 1
            
            if minion_idx < 0 or minion_idx >= len(self.minions):
                await interaction.response.send_message(
                    f"❌ Invalid minion number! Please choose between 1 and {len(self.minions)}.",
                    ephemeral=True
                )
                return
            
            if skin_idx < 0 or skin_idx >= len(self.skins):
                await interaction.response.send_message(
                    f"❌ Invalid skin number! Please choose between 1 and {len(self.skins)}.",
                    ephemeral=True
                )
                return
            
            minion = self.minions[minion_idx]
            skin = self.skins[skin_idx]
            
            success = await self.bot.db.minion_upgrades.apply_skin(minion['id'], skin['item_id'])
            
            if success:
                await interaction.response.send_message(
                    f"✅ Successfully applied **{skin['name']}** to **{minion['minion_type'].title()} Minion**!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Failed to apply skin. Make sure the skin matches the minion type and you have it in your inventory!",
                    ephemeral=True
                )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter valid numbers!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error applying skin: {str(e)}",
                ephemeral=True
            )
