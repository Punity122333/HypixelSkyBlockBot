import discord


class IslandNameModal(discord.ui.Modal, title="Rename Island"):
    name = discord.ui.TextInput(
        label="Island Name",
        placeholder="Enter your island name",
        required=True,
        max_length=50
    )
    
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.view.bot.db.island.update_island(
            interaction.user.id,
            island_name=str(self.name)
        )
        
        embed = await self.view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)


class PlaceDecorationModal(discord.ui.Modal, title="Place Decoration"):
    decoration_id = discord.ui.TextInput(
        label="Decoration ID",
        placeholder="Enter decoration ID (e.g., oak_tree, fountain)",
        required=True,
        max_length=50
    )
    
    position_x = discord.ui.TextInput(
        label="X Position",
        placeholder="Enter X coordinate (0-20)",
        required=True,
        max_length=3
    )
    
    position_y = discord.ui.TextInput(
        label="Y Position",
        placeholder="Enter Y coordinate (0-20)",
        required=True,
        max_length=3
    )
    
    rotation = discord.ui.TextInput(
        label="Rotation",
        placeholder="Enter rotation (0, 90, 180, 270)",
        required=False,
        default="0",
        max_length=3
    )
    
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            x = int(self.position_x.value)
            y = int(self.position_y.value)
            rot = int(self.rotation.value) if self.rotation.value else 0
            
            success = await self.view.bot.db.island.add_decoration(
                interaction.user.id,
                str(self.decoration_id),
                x, y, rot
            )
            
            if success:
                embed = await self.view.get_embed()
                await interaction.response.edit_message(embed=embed, view=self.view)
            else:
                await interaction.response.send_message(
                    "❌ Failed to place decoration! Check if you have enough coins, the decoration exists, and the position is valid.",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message("❌ Invalid coordinates or rotation!", ephemeral=True)


class ApplyThemeModal(discord.ui.Modal, title="Apply Island Theme"):
    theme_id = discord.ui.TextInput(
        label="Theme ID",
        placeholder="Enter theme ID (e.g., default, tropical, medieval)",
        required=True,
        max_length=50
    )
    
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        success = await self.view.bot.db.island.set_theme(interaction.user.id, str(self.theme_id))
        
        if success:
            embed = await self.view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.view)
        else:
            await interaction.response.send_message(
                "❌ Failed to apply theme! Check if you have enough coins, meet the requirements, and the theme ID is valid.",
                ephemeral=True
            )
