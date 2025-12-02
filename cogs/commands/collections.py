import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, List, Optional
from utils.autocomplete import item_autocomplete

class CollectionInfoModal(discord.ui.Modal, title="Collection Info"):
    item = discord.ui.TextInput(label="Item Name", placeholder="e.g., wheat", required=True)
    
    def __init__(self, bot, cog):
        super().__init__()
        self.bot = bot
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        item_id = self.item.value.lower().replace(' ', '_')
        
        tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
        
        if not tiers:
            await interaction.followup.send(f"❌ Collection not found for '{self.item.value}'!", ephemeral=True)
            return
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        amount = await self.bot.db.get_collection(interaction.user.id, item_id)
        tier = await self.cog.get_tier_for_amount(item_id, amount)
        category = await self.cog.get_category_for_item(item_id)
        
        embed = discord.Embed(
            title=f"📦 {self.item.value.title()} Collection",
            description=f"Category: {category.title() if category else 'Unknown'}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Current Tier", value=f"{tier}/10", inline=True)
        embed.add_field(name="Total Collected", value=f"{amount:,}", inline=True)
        
        tiers_info = ""
        tier_rewards = await self.bot.game_data.get_all_collection_tier_rewards()
        for i, req in enumerate(tiers):
            tier_num = i + 1
            status = "✅" if amount >= req else "🔒"
            reward = tier_rewards.get(tier_num, {})
            reward_text = f" → {reward.get('coins', 0):,} coins"
            if reward.get('recipes'):
                reward_text += f", {len(reward['recipes'])} recipe(s)"
            tiers_info += f"{status} Tier {tier_num}: {req:,}{reward_text}\n"
        
        embed.add_field(name="Tier Tree", value=tiers_info, inline=False)
        
        if tier < 10 and tier < len(tiers):
            next_tier = tier + 1
            next_req = tiers[tier]
            progress = (amount / next_req) * 100 if next_req > 0 else 100
            embed.add_field(
                name=f"Progress to Tier {next_tier}",
                value=f"{amount:,} / {next_req:,} ({progress:.1f}%)",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class CollectionLeaderboardModal(discord.ui.Modal, title="Collection Leaderboard"):
    item = discord.ui.TextInput(label="Item Name (optional)", placeholder="e.g., wheat", required=False)
    
    def __init__(self, bot, user_id, cog):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.item.value:
            item_id = self.item.value.lower().replace(' ', '_')
            tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
            if not tiers:
                await interaction.followup.send(f"❌ Collection not found for '{self.item.value}'!", ephemeral=True)
                return
            
            top_players = await self.bot.db.get_top_collections(item_id, 100)
            
            view = CollectionLeaderboardView(self.bot, self.user_id, item_id, self.item.value.title(), top_players, self.cog)
            embed = await view.get_embed()
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            all_categories = await self.bot.game_data.get_collection_categories()
            categories_data = {}
            for category in all_categories.keys():
                top_player = await self.bot.db.get_top_category_collectors(category, 1)
                if top_player:
                    categories_data[category] = top_player[0]
            
            embed = discord.Embed(
                title="🏆 Collection Category Leaders",
                description="Top collectors in each category",
                color=discord.Color.gold()
            )
            
            for category, player_data in categories_data.items():
                user = await self.bot.fetch_user(player_data['user_id'])
                username = user.name if user else f"User {player_data['user_id']}"
                level = player_data.get('total_tiers', 0)
                
                cat_emoji = {'farming': '🌾', 'mining': '⛏️', 'foraging': '🪓', 'combat': '⚔️'}
                embed.add_field(
                    name=f"{cat_emoji.get(category, '📦')} {category.title()}",
                    value=f"**{username}**\nLevel: {level}",
                    inline=True
                )
        
            await interaction.followup.send(embed=embed, ephemeral=True)

class CollectionLeaderboardView(discord.ui.View):
    def __init__(self, bot, user_id, item_id, item_name, top_players, cog):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.item_id = item_id
        self.item_name = item_name
        self.top_players = top_players
        self.cog = cog
        self.page = 0
        self.items_per_page = 10
    
    async def get_embed(self):
        embed = discord.Embed(
            title=f"🏆 {self.item_name} Collection Leaderboard",
            description="Top collectors",
            color=discord.Color.gold()
        )
        
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        page_players = self.top_players[start:end]
        
        leaderboard_text = ""
        for i, player_data in enumerate(page_players, start=start + 1):
            try:
                user = await self.bot.fetch_user(player_data['user_id'])
                username = user.name if user else f"User {player_data['user_id']}"
            except:
                username = f"User {player_data['user_id']}"
            
            tier = await self.cog.get_tier_for_amount(self.item_id, player_data['amount'])
            
            medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, f'{i}.')
            leaderboard_text += f"{medal} **{username}**: {player_data['amount']:,} (Tier {tier})\n"
        
        embed.add_field(name="Top Collectors", value=leaderboard_text or "No data yet!", inline=False)
        
        total_pages = (len(self.top_players) + self.items_per_page - 1) // self.items_per_page if self.top_players else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=0)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = (len(self.top_players) + self.items_per_page - 1) // self.items_per_page
        if self.page < total_pages - 1:
            self.page += 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()

class CollectionMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username, cog=None):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_category = None
        self.cog = cog
    
    async def get_category_for_item(self, item_id: str) -> Optional[str]:
        return await self.bot.game_data.get_item_category(item_id)
    
    async def get_tier_for_amount(self, item_id: str, amount: int) -> int:
        tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
        if not tiers:
            return 0
        tier = 0
        for i, req in enumerate(tiers):
            if amount >= req:
                tier = i + 1
            else:
                break
        return tier
    
    async def get_category_level(self, category: str) -> int:
        items = await self.bot.game_data.get_category_items(category)
        if not items:
            return 0
        total_tiers = 0
        for item_id in items:
            amount = await self.bot.db.get_collection(self.user_id, item_id)
            tier = await self.get_tier_for_amount(item_id, amount)
            total_tiers += tier
        return total_tiers
    
    async def get_embed(self):
        embed = discord.Embed(
            title=f"📦 {self.username}'s Collections",
            description="Progress through collection tiers to unlock rewards!",
            color=discord.Color.gold()
        )
        
        all_categories = await self.bot.game_data.get_collection_categories()
        categories_to_show = [self.current_category] if self.current_category else list(all_categories.keys())
        
        for cat in categories_to_show:
            items = await self.bot.game_data.get_category_items(cat)
            category_text = ""
            category_level = await self.get_category_level(cat)
            
            for item_id in items[:10]:
                amount = await self.bot.db.get_collection(self.user_id, item_id)
                tier = await self.get_tier_for_amount(item_id, amount)
                
                display_name = item_id.replace('_', ' ').title()
                tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
                
                if tier < 10 and tiers and tier < len(tiers):
                    next_req = tiers[tier]
                    category_text += f"{display_name} {tier}/10: {amount:,}/{next_req:,}\n"
                else:
                    category_text += f"{display_name} MAX: {amount:,}\n"
            
            if category_text:
                cat_emoji = {'farming': '🌾', 'mining': '⛏️', 'foraging': '🪓', 'combat': '⚔️'}
                embed.add_field(
                    name=f"{cat_emoji.get(cat, '📦')} {cat.title()} (Level {category_level})",
                    value=category_text[:1024],
                    inline=False
                )
        
        if len(embed.fields) == 0:
            embed.description = "No collections yet!"
        
        embed.set_footer(text="Use category buttons to filter")
        return embed
    
    @discord.ui.button(label="All", style=discord.ButtonStyle.gray, row=0)
    async def all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = None
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="🌾 Farming", style=discord.ButtonStyle.green, row=0)
    async def farming_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'farming'
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="⛏️ Mining", style=discord.ButtonStyle.blurple, row=0)
    async def mining_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'mining'
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="🪓 Foraging", style=discord.ButtonStyle.green, row=1)
    async def foraging_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'foraging'
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="⚔️ Combat", style=discord.ButtonStyle.red, row=1)
    async def combat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'combat'
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.blurple, row=2)
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = CollectionInfoModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏆 Leaderboard", style=discord.ButtonStyle.green, row=2)
    async def leaderboard_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = CollectionLeaderboardModal(self.bot, self.user_id, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎁 Rewards", style=discord.ButtonStyle.gray, row=2)
    async def rewards_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎁 Collection Rewards",
            description="Unlock rewards by progressing through collection tiers!",
            color=discord.Color.purple()
        )
        
        tier_rewards = await self.bot.game_data.get_all_collection_tier_rewards()
        tier_text = ""
        for tier, rewards in tier_rewards.items():
            tier_text += f"**Tier {tier}:** {rewards['coins']:,} coins"
            if rewards.get('recipes'):
                tier_text += f", {len(rewards['recipes'])} recipe(s)"
            tier_text += "\n"
        
        embed.add_field(name="Per-Tier Rewards", value=tier_text, inline=False)
        
        category_bonuses = await self.bot.game_data.get_all_collection_category_bonuses()
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

class CollectionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="collections", description="View and manage your collections")
    async def collections_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = CollectionMenuView(self.bot, interaction.user.id, interaction.user.name, self)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

    async def get_tier_for_amount(self, item_id: str, amount: int) -> int:
        tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
        if not tiers:
            return 0
        tier = 0
        for i, req in enumerate(tiers):
            if amount >= req:
                tier = i + 1
            else:
                break
        return tier
    
    async def get_category_for_item(self, item_id: str) -> Optional[str]:
        return await self.bot.game_data.get_item_category(item_id)
    
    async def get_category_level(self, user_id: int, category: str) -> int:
        items = await self.bot.game_data.get_category_items(category)
        if not items:
            return 0
        total_tiers = 0
        for item_id in items:
            amount = await self.bot.db.get_collection(user_id, item_id)
            tier = await self.get_tier_for_amount(item_id, amount)
            total_tiers += tier
        return total_tiers



async def setup(bot):
    await bot.add_cog(CollectionCommands(bot))
