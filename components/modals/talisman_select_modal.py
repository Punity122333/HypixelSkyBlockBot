import discord

class TalismanSelectModal(discord.ui.Modal, title="Choose Talisman"):
    talisman_number = discord.ui.TextInput(
        label="Talisman Number",
        placeholder="Enter the number of the talisman you want to equip",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, talismans):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.talismans = talismans
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            idx = int(self.talisman_number.value) - 1
            if idx < 0 or idx >= len(self.talismans):
                await interaction.response.send_message(
                    f"❌ Invalid talisman number! Please choose between 1 and {len(self.talismans)}.",
                    ephemeral=True
                )
                return
            
            talisman = self.talismans[idx]
            talisman_id = talisman['item_id']
            
            from utils.systems.talisman_pouch_system import TalismanPouchSystem
            result = await TalismanPouchSystem.add_talisman_to_pouch(
                self.bot.db,
                self.user_id,
                talisman_id
            )
            
            if result['success']:
                await interaction.response.send_message(
                    f"✅ {result['message']}",
                    ephemeral=True
                )
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
