import discord

class EquipmentSelectModal(discord.ui.Modal, title="Choose Item"):
    item_number = discord.ui.TextInput(
        label="Item Number",
        placeholder="Enter the number of the item you want to equip",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, equipment_slot, items):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.equipment_slot = equipment_slot
        self.items = items
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            idx = int(self.item_number.value) - 1
            if idx < 0 or idx >= len(self.items):
                await interaction.response.send_message(
                    f"❌ Invalid item number! Please choose between 1 and {len(self.items)}.",
                    ephemeral=True
                )
                return
            
            item = self.items[idx]
            success = await self.bot.db.equip_item(self.user_id, item['slot'], self.equipment_slot)
            
            if success:
                await interaction.response.send_message(
                    f"✅ Equipped **{item['name']}** in {self.equipment_slot} slot!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ Failed to equip {item['name']}",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number!",
                ephemeral=True
            )