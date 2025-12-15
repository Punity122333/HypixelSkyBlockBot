import discord

class MinionPlaceModal(discord.ui.Modal, title="Place Minion"):
    minion_number = discord.ui.TextInput(
        label="Minion Number",
        placeholder="Enter the number of the minion you want to place",
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
            item_id = minion['item_id']
            minion_type = item_id.replace('_minion', '')
            
            await self.bot.db.inventory.remove_item(self.user_id, item_id, 1)
            
            existing_minions = await self.bot.db.get_user_minions(self.user_id)
            next_slot = len(existing_minions) + 1
            
            await self.bot.db.add_minion(self.user_id, minion_type, 1, next_slot)
            
            await interaction.response.send_message(
                f"✅ Successfully placed **{minion['name']}** in slot {next_slot}!",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error placing minion: {str(e)}",
                ephemeral=True
            )
