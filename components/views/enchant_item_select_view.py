import discord
from components.modals.enchant_item_select_modal import EnchantItemSelectModal

class EnchantItemSelectView(discord.ui.View):
    def __init__(self, bot, user_id, items, enchantment, level, enchant_data, cost, xp_gained):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.items = items
        self.enchantment = enchantment
        self.level = level
        self.enchant_data = enchant_data
        self.cost = cost
        self.xp_gained = xp_gained

        choose_button = discord.ui.Button(
            label="✨ Choose Item",
            style=discord.ButtonStyle.primary,
            custom_id=f"choose_item_to_enchant:{user_id}"
        )
        choose_button.callback = self.choose_callback
        self.add_item(choose_button)
    
    async def choose_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = EnchantItemSelectModal(
            self.bot, self.user_id, self.items, self.enchantment, 
            self.level, self.enchant_data, self.cost, self.xp_gained
        )
        await interaction.response.send_modal(modal)
