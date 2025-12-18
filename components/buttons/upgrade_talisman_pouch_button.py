import discord
from utils.systems.talisman_pouch_system import TalismanPouchSystem

class UpgradeTalismanPouchButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📦 Upgrade Talisman Pouch", style=discord.ButtonStyle.green, custom_id="upgrade_talisman_pouch", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your profile!", ephemeral=True)
            return
        
        current_capacity = await self.parent_view.bot.db.get_talisman_pouch_capacity(interaction.user.id)
        
        if current_capacity >= 48:
            await interaction.response.send_message("❌ Your talisman pouch is already at maximum capacity (48 slots)!", ephemeral=True)
            return
        
        cost = await TalismanPouchSystem.get_upgrade_cost(current_capacity)
        new_capacity = current_capacity + 6
        
        embed = discord.Embed(
            title="📦 Upgrade Talisman Pouch",
            description=f"Increase your talisman pouch capacity from **{current_capacity}** to **{new_capacity}** slots",
            color=discord.Color.green()
        )
        
        embed.add_field(name="💰 Cost", value=f"{cost:,} coins", inline=True)
        embed.add_field(name="📈 New Capacity", value=f"{new_capacity} slots", inline=True)
        
        embed.set_footer(text="Click Confirm to purchase this upgrade")
        
        view = ConfirmUpgradeView(self.parent_view, cost)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmUpgradeView(discord.ui.View):
    def __init__(self, parent_view, cost):
        super().__init__(timeout=60)
        self.parent_view = parent_view
        self.cost = cost
    
    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your upgrade!", ephemeral=True)
            return
        
        result = await TalismanPouchSystem.upgrade_pouch(self.parent_view.bot.db, interaction.user.id)
        
        if result['success']:
            embed = discord.Embed(
                title="✅ Upgrade Successful!",
                description=f"Your talisman pouch capacity has been increased to **{result['new_capacity']}** slots!",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Cost", value=f"{result['cost']:,} coins", inline=True)
            await interaction.response.edit_message(embed=embed, view=None)
            
            self.parent_view.current_view = 'talisman_pouch'
            await interaction.followup.send(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.edit_message(
                content=f"❌ {result['message']}",
                embed=None,
                view=None
            )
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your upgrade!", ephemeral=True)
            return
        
        await interaction.response.edit_message(content="❌ Upgrade cancelled.", embed=None, view=None)
