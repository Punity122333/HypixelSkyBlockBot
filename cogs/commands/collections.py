import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, List, Optional
from utils.autocomplete import item_autocomplete

class CollectionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @app_commands.command(name="collections", description="View your collections with tiers and rewards")
    @app_commands.describe(category="Filter by category: farming, mining, foraging, or combat")
    async def collections(self, interaction: discord.Interaction, category: Optional[str] = None):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        all_categories = await self.bot.game_data.get_collection_categories()
        
        if category and category.lower() not in all_categories:
            await interaction.followup.send(f"❌ Invalid category! Choose from: {', '.join(all_categories.keys())}", ephemeral=True)
            return
        
        categories_to_show = [category.lower()] if category else list(all_categories.keys())
        
        embed = discord.Embed(
            title=f"📦 {interaction.user.name}'s Collections",
            description="Progress through collection tiers to unlock rewards!",
            color=discord.Color.gold()
        )
        
        for cat in categories_to_show:
            items = await self.bot.game_data.get_category_items(cat)
            category_text = ""
            category_level = await self.get_category_level(interaction.user.id, cat)
            
            for item_id in items:
                amount = await self.bot.db.get_collection(interaction.user.id, item_id)
                tier = await self.get_tier_for_amount(item_id, amount)
                
                # Show all items in the category, not just ones with progress
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
            embed.description = "No collections yet! Gather resources to start your collection journey."
        
        embed.set_footer(text="Use /collection_rewards to see tier rewards!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="collection_info", description="Get detailed info about a specific collection")
    @app_commands.describe(item="The collection item name")
    async def collection_info(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer()
        
        item_id = item.lower().replace(' ', '_')
        
        tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
        
        if not tiers:
            await interaction.followup.send(f"❌ Collection not found for '{item}'!", ephemeral=True)
            return
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        amount = await self.bot.db.get_collection(interaction.user.id, item_id)
        tier = await self.get_tier_for_amount(item_id, amount)
        category = await self.get_category_for_item(item_id)
        
        embed = discord.Embed(
            title=f"📦 {item.title()} Collection",
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
        
        await interaction.followup.send(embed=embed)

    @collection_info.autocomplete('item')
    async def collection_info_autocomplete(self, interaction: discord.Interaction, current: str):
        return await item_autocomplete(interaction, current)
    
    @app_commands.command(name="collection_rewards", description="View collection tier rewards and category bonuses")
    async def collection_rewards(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
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
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="collection_leaderboard", description="View top collectors")
    @app_commands.describe(item="Specific item to see leaderboard for (optional)")
    async def collection_leaderboard(self, interaction: discord.Interaction, item: Optional[str] = None):
        await interaction.response.defer()
        
        if item:
            item_id = item.lower().replace(' ', '_')
            tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
            if not tiers:
                await interaction.followup.send(f"❌ Collection not found for '{item}'!", ephemeral=True)
                return
            
            top_players = await self.bot.db.get_top_collections(item_id, 10)
            
            embed = discord.Embed(
                title=f"🏆 {item.title()} Collection Leaderboard",
                description="Top 10 collectors",
                color=discord.Color.gold()
            )
            
            leaderboard_text = ""
            for rank, player_data in enumerate(top_players, 1):
                user = await self.bot.fetch_user(player_data['user_id'])
                username = user.name if user else f"User {player_data['user_id']}"
                tier = await self.get_tier_for_amount(item_id, player_data['amount'])
                
                medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'{rank}.')
                leaderboard_text += f"{medal} **{username}**: {player_data['amount']:,} (Tier {tier})\n"
            
            embed.add_field(name="Top Collectors", value=leaderboard_text or "No data yet!", inline=False)
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
        
        await interaction.followup.send(embed=embed)

    @collection_leaderboard.autocomplete('item')
    async def collection_leaderboard_autocomplete(self, interaction: discord.Interaction, current: str):
        return await item_autocomplete(interaction, current)

async def setup(bot):
    await bot.add_cog(CollectionCommands(bot))
