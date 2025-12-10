import discord
from discord.ui import View, Button
from typing import Dict, List, Tuple

class HelpView(View):
    def __init__(self, user_id, command_categories: Dict[str, List[Tuple[str, str]]]):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.page = 0
        self.command_categories = command_categories
        self.categories = list(command_categories.keys())
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        if self.page > 0:
            prev_button = Button(label="Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if self.page < len(self.categories) - 1:
            next_button = Button(label="Next", style=discord.ButtonStyle.gray)
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page -= 1
        self.add_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page += 1
        self.add_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_embed(self):
        embed = discord.Embed(
            title="SkyBlock Bot Commands",
            description="All available commands organized by category",
            color=discord.Color.blue()
        )
        
        total_commands = sum(len(cmds) for cmds in self.command_categories.values())
        
        for category_name, commands_list in self.command_categories.items():
            if not commands_list:
                continue
            commands_text = "\n".join([f"`/{cmd}` - {desc}" for cmd, desc in commands_list])
            embed.add_field(
                name=category_name,
                value=commands_text,
                inline=False
            )
        
        embed.set_footer(text=f"Total: {total_commands} commands | Use /claim_starter_pack to begin!")
        return embed
