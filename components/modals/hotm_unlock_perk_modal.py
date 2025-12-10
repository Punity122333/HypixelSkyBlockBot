import discord


class HotmUnlockPerkModal(discord.ui.Modal, title="Unlock HOTM Perk"):
    perk_name = discord.ui.TextInput(label="Perk Name", placeholder="e.g., mining_speed", required=True)
    
    def __init__(self, bot, view):
        super().__init__()
        self.bot = bot
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        
        perk_id = self.perk_name.value.lower().replace(' ', '_')
        
        result = await HeartOfTheMountainSystem.unlock_perk(self.bot.db, interaction.user.id, perk_id)
        
        if result['success']:
            embed = discord.Embed(
                title="✅ Perk Upgraded!",
                description=f"**{result['perk_name']}** is now level {result['new_level']}",
                color=discord.Color.green()
            )
            embed.add_field(name="Cost", value=f"{result['cost']} Tokens", inline=True)
            embed.add_field(name="Remaining", value=f"{result['remaining_tokens']} Tokens", inline=True)
        else:
            embed = discord.Embed(
                title="❌ Failed to Unlock Perk",
                description=result.get('error', 'Unknown error'),
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        await self.view.refresh_data()
        if self.view.message:
            await self.view.message.edit(embed=await self.view.get_embed(), view=self.view)
