import discord
from typing import Optional
from components.buttons.collection_buttons import (
    CollectionAllButton,
    CollectionFarmingButton,
    CollectionMiningButton,
    CollectionForagingButton,
    CollectionCombatButton,
    CollectionInfoButton,
    CollectionLeaderboardButton,
    CollectionRewardsButton
)

class CollectionMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username, cog=None):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_category = None
        self.cog = cog
        
        self.add_item(CollectionAllButton(self))
        self.add_item(CollectionFarmingButton(self))
        self.add_item(CollectionMiningButton(self))
        self.add_item(CollectionForagingButton(self))
        self.add_item(CollectionCombatButton(self))
        self.add_item(CollectionInfoButton(self))
        self.add_item(CollectionLeaderboardButton(self))
        self.add_item(CollectionRewardsButton(self))
    
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