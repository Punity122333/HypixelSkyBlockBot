import discord

class AchievementsCategoryModal(discord.ui.Modal, title="View Category"):
    category_input = discord.ui.TextInput(
        label="Category Name",
        placeholder="Enter category name (e.g., Farming, Mining, Combat)",
        required=True,
        max_length=50
    )
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        category = self.category_input.value.strip()
        
        all_achievements = await self.parent_view.bot.db.achievements.get_all_achievements()
        categories = list(set(a['category'] for a in all_achievements))
        
        category_lower = category.lower()
        matching_category = None
        for cat in categories:
            if cat.lower() == category_lower:
                matching_category = cat
                break
        
        if not matching_category:
            await interaction.response.send_message(
                f"❌ Category '{category}' not found. Available categories: {', '.join(categories)}",
                ephemeral=True
            )
            return
        
        self.parent_view.current_category = matching_category
        self.parent_view.current_view = 'category'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
