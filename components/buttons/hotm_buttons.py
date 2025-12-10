import discord
from components.modals.hotm_unlock_perk_modal import HotmUnlockPerkModal


class HotmMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="hotm_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)


class HotmPerksButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⭐ Perks", style=discord.ButtonStyle.green, custom_id="hotm_perks", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.parent_view.load_perks()
        self.parent_view.current_view = 'perks'
        self.parent_view._update_buttons()
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)


class HotmCommissionsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📋 Commissions", style=discord.ButtonStyle.gray, custom_id="hotm_commissions", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.parent_view.load_commissions()
        self.parent_view.current_view = 'commissions'
        self.parent_view._update_buttons()
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)


class HotmCrystalNucleusButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔮 Crystal Nucleus", style=discord.ButtonStyle.blurple, custom_id="hotm_nucleus", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        from utils.systems.crystal_hollows_system import CrystalHollowsSystem
        
        player = await self.parent_view.bot.player_manager.get_player_fresh(self.parent_view.user_id)
        
        if player['coins'] < 10000:
            await interaction.followup.send("❌ You need 10,000 coins to enter the Crystal Nucleus!", ephemeral=True)
            return
        
        await self.parent_view.bot.player_manager.remove_coins(self.parent_view.user_id, 10000)
        
        result = await CrystalHollowsSystem.explore_nucleus(self.parent_view.bot.db, self.parent_view.user_id)
        
        if result['success']:
            await self.parent_view.bot.player_manager.add_coins(self.parent_view.user_id, result['rewards']['coins'])
            
            embed = discord.Embed(
                title="🔮 Crystal Nucleus Exploration",
                description="You ventured into the mysterious Crystal Nucleus!",
                color=discord.Color.purple()
            )
            
            if result['crystal_found']:
                embed.add_field(
                    name="💎 CRYSTAL FOUND!",
                    value=f"You discovered a {result['crystal_type'].upper()} crystal!",
                    inline=False
                )
            
            rewards_text = f"🪙 {result['rewards']['coins']:,} coins\n"
            rewards_text += f"⛏️ {result['rewards']['mithril_powder']:,} Mithril Powder\n"
            rewards_text += f"💎 {result['rewards']['gemstone_powder']:,} Gemstone Powder"
            
            embed.add_field(name="Rewards", value=rewards_text, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            await self.parent_view.refresh_data()
            await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)


class HotmUnlockPerkButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔓 Unlock Perk", style=discord.ButtonStyle.green, custom_id="hotm_unlock", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(HotmUnlockPerkModal(self.parent_view.bot, self.parent_view))


class HotmRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔄 Refresh", style=discord.ButtonStyle.gray, custom_id="hotm_refresh", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.parent_view.refresh_data()
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)
