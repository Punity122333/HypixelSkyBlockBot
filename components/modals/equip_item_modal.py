import discord
from utils.helper import show_equipment_select

class EquipItemModal(discord.ui.Modal, title="Equip Item"):
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
        
        slot_mappings = {
            'helmet': ['HELMET'],
            'chestplate': ['CHESTPLATE'],
            'chest': ['CHESTPLATE'],
            'leggings': ['LEGGINGS'],
            'legs': ['LEGGINGS'],
            'boots': ['BOOTS'],
            'sword': ['SWORD'],
            'bow': ['BOW'],
            'axe': ['AXE'],
            'hoe': ['HOE'],
            'fishing_rod': ['FISHING_ROD'],
            'pickaxe': ['PICKAXE'],
            'shovel': ['SHOVEL']
        }
        
        if slot_value not in slot_mappings:
            await interaction.response.send_message(
                f"❌ Invalid slot! Choose from: {', '.join(list(slot_mappings.keys()))}",
                ephemeral=True
            )
            return
        
        await show_equipment_select(interaction, slot_value, slot_mappings[slot_value])