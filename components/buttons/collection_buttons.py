import discord
from components.modals.collection_info_modal import CollectionInfoModal
from components.modals.collection_leaderboard_modal import CollectionLeaderboardModal

class CollectionAllButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="All", style=discord.ButtonStyle.gray, custom_id="collection_all", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = None
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class CollectionFarmingButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🌾 Farming", style=discord.ButtonStyle.green, custom_id="collection_farming", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'farming'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class CollectionMiningButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⛏️ Mining", style=discord.ButtonStyle.blurple, custom_id="collection_mining", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'mining'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class CollectionForagingButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🪓 Foraging", style=discord.ButtonStyle.green, custom_id="collection_foraging", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'foraging'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class CollectionCombatButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⚔️ Combat", style=discord.ButtonStyle.red, custom_id="collection_combat", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'combat'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class CollectionInfoButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="ℹ️ Info", style=discord.ButtonStyle.blurple, custom_id="collection_info", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = CollectionInfoModal(self.parent_view.bot, self.parent_view)
        await interaction.response.send_modal(modal)

class CollectionLeaderboardButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏆 Leaderboard", style=discord.ButtonStyle.green, custom_id="collection_leaderboard", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = CollectionLeaderboardModal(self.parent_view.bot, self.parent_view.user_id, self.parent_view)
        await interaction.response.send_modal(modal)

class CollectionRewardsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🎁 Rewards", style=discord.ButtonStyle.gray, custom_id="collection_rewards", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎁 Collection Rewards",
            description="Unlock rewards by progressing through collection tiers!",
            color=discord.Color.purple()
        )
        
        tier_rewards = await self.parent_view.bot.game_data.get_all_collection_tier_rewards()
        tier_text = ""
        for tier, rewards in tier_rewards.items():
            tier_text += f"**Tier {tier}:** {rewards['coins']:,} coins"
            if rewards.get('recipes'):
                tier_text += f", {len(rewards['recipes'])} recipe(s)"
            tier_text += "\n"
        
        embed.add_field(name="Per-Tier Rewards", value=tier_text, inline=False)
        
        category_bonuses = await self.parent_view.bot.game_data.get_all_collection_category_bonuses()
        for category, bonuses in category_bonuses.items():
            bonus_text = ""
            for level, stats in bonuses.items():
                stat_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in stats.items()])
                bonus_text += f"Level {level}: {stat_str}\n"
            
            cat_emoji = {'farming': '🌾', 'mining': '⛏️', 'foraging': '🪓', 'combat': '⚔️'}
            embed.add_field(
                name=f"{cat_emoji.get(category, '📦')} {category.title()} Category Bonuses",
                value=bonus_text,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
