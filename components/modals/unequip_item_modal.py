
import discord

class UnequipItemModal(discord.ui.Modal, title="Unequip Item"):
    slot = discord.ui.TextInput(
        label="Equipment Slot",
        placeholder="helmet, sword, bow, axe, hoe, fishing_rod, etc.",
        required=True
    )
    
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):
        slot_value = self.slot.value.lower().strip()
        
        valid_slots = ['helmet', 'chestplate', 'chest', 'leggings', 'legs', 'boots', 'sword', 'bow', 'axe', 'hoe', 'fishing_rod', 'pickaxe', 'shovel']
        
        if slot_value not in valid_slots:
            await interaction.response.send_message(
                f"❌ Invalid slot! Choose from: helmet, chestplate, leggings, boots, sword, bow, pickaxe, axe, hoe, fishing_rod",
                ephemeral=True
            )
            return

        if slot_value == 'chest':
            slot_value = 'chestplate'
        elif slot_value == 'legs':
            slot_value = 'leggings'
        
        bot = interaction.client
        success = await bot.db.unequip_item(self.user_id, slot_value)  # type: ignore
        
        if success:
            await interaction.response.send_message(
                f"✅ Unequipped {slot_value}!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ No {slot_value} equipped!",
                ephemeral=True
            )
