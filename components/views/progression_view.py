import discord
from components.buttons.progression_buttons import (
    ProgressionMainButton,
    ProgressionMilestonesButton,
    ProgressionToolsButton,
    ProgressionStatsButton
)

class ProgressionMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        
        self.main_button = ProgressionMainButton(self)
        self.milestones_button = ProgressionMilestonesButton(self)
        self.tools_button = ProgressionToolsButton(self)
        self.stats_button = ProgressionStatsButton(self)
        
        self._update_buttons()
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'milestones':
            return await self.get_milestones_embed()
        elif self.current_view == 'tools':
            return await self.get_tools_embed()
        elif self.current_view == 'stats':
            return await self.get_stats_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        player = await self.bot.db.get_player(self.user_id)
        progression = await self.bot.db.get_player_progression(self.user_id)
        
        embed = discord.Embed(
            title=f"🎯 Progression Overview",
            description="Your journey through SkyBlock",
            color=discord.Color.purple()
        )
        
        if player:
            wealth = player.get('coins', 0) + player.get('bank', 0)
            
            milestones = [
                (0, "🌱 Newcomer"),
                (10000, "💼 Trader"),
                (50000, "🏪 Merchant"),
                (100000, "💰 Wealthy"),
                (500000, "📈 Investor"),
                (1000000, "💎 Millionaire"),
                (5000000, "🏆 Tycoon"),
                (10000000, "👑 Mogul"),
            ]
            
            current_rank = "🌱 Newcomer"
            next_milestone = 10000
            
            for threshold, rank in milestones:
                if wealth >= threshold:
                    current_rank = rank
                else:
                    next_milestone = threshold
                    break
            
            embed.add_field(
                name="Current Rank",
                value=current_rank,
                inline=True
            )
            
            embed.add_field(
                name="Total Wealth",
                value=f"{wealth:,} coins",
                inline=True
            )
            
            if wealth < 10000000:
                remaining = next_milestone - wealth
                embed.add_field(
                    name="Next Milestone",
                    value=f"{remaining:,} coins away",
                    inline=True
                )
        
        if progression:
            status = ""
            if progression.get('tutorial_completed'):
                status += "✅ Tutorial Complete\n"
            else:
                status += "❌ Tutorial Pending (use `/begin`)\n"
            
            if progression.get('first_mine_date'):
                status += "✅ First Mining Session\n"
            else:
                status += "⛏️ Start mining (use `/mine`)\n"
            
            if progression.get('first_farm_date'):
                status += "✅ First Farming Session\n"
            else:
                status += "🌾 Start farming (use `/farm`)\n"
            
            if progression.get('first_auction_date'):
                status += "✅ First Auction Created\n"
            else:
                status += "📦 Create your first auction\n"
            
            if progression.get('first_trade_date'):
                status += "✅ First Trade Completed\n"
            else:
                status += "🤝 Complete your first trade\n"
            
            embed.add_field(name="Progress Checklist", value=status, inline=False)
        
        embed.set_footer(text="Use buttons below to view detailed progression")
        return embed
    
    async def get_milestones_embed(self):
        player = await self.bot.db.get_player(self.user_id)
        
        embed = discord.Embed(
            title="🏆 Wealth Milestones",
            description="Track your progress to riches",
            color=discord.Color.gold()
        )
        
        if player:
            wealth = player.get('coins', 0) + player.get('bank', 0)
            
            milestones = [
                (0, "🌱 Newcomer", "Starting your journey"),
                (10000, "💼 Trader", "Learning the basics of trade"),
                (50000, "🏪 Merchant", "Building a business"),
                (100000, "💰 Wealthy", "Accumulating fortune"),
                (500000, "📈 Investor", "Smart investments paying off"),
                (1000000, "💎 Millionaire", "Elite wealth status"),
                (5000000, "🏆 Tycoon", "Master of commerce"),
                (10000000, "👑 Mogul", "Economic powerhouse"),
            ]
            
            milestone_text = ""
            for threshold, rank, desc in milestones:
                if wealth >= threshold:
                    milestone_text += f"✅ **{rank}** - {desc}\n"
                else:
                    remaining = threshold - wealth
                    milestone_text += f"🔒 **{rank}** - {remaining:,} coins to go\n"
            
            embed.add_field(
                name=f"Your Wealth: {wealth:,} coins",
                value=milestone_text,
                inline=False
            )
            
            total_earned = player.get('total_earned', 0)
            total_spent = player.get('total_spent', 0)
            net_profit = total_earned - total_spent
            
            embed.add_field(
                name="Trading Performance",
                value=f"**Total Earned:** {total_earned:,} coins\n**Total Spent:** {total_spent:,} coins\n**Net Profit:** {net_profit:,} coins",
                inline=False
            )
        
        embed.set_footer(text="Keep progressing to unlock achievements and rank up!")
        return embed
    
    async def get_tools_embed(self):
        inventory = await self.bot.db.get_inventory(self.user_id)
        player_items = [item['item_id'] for item in inventory] if inventory else []
        
        embed = discord.Embed(
            title="🛠️ Tool Progression Path",
            description="Upgrade your tools to gather resources faster!",
            color=discord.Color.blue()
        )
        
        tool_tiers_from_db = await self.bot.game_data.get_all_tool_tiers()
        
        if tool_tiers_from_db:
            for tool_type, tiers in tool_tiers_from_db.items():
                current_tier = -1
                for tier_info in tiers:
                    if tier_info.get('item_id') in player_items:
                        current_tier = tier_info.get('tier', -1)
                
                status = ""
                for tier_info in tiers:
                    tier_num = tier_info.get('tier', 0)
                    tier_name = tier_info.get('name', 'Unknown')
                    
                    if tier_num <= current_tier:
                        status += f"✅ {tier_name}\n"
                    elif tier_num == current_tier + 1:
                        status += f"⏭️ {tier_name} (Next Upgrade)\n"
                        if tier_info.get('recipe'):
                            try:
                                import json
                                recipe_data = tier_info.get('recipe')
                                if isinstance(recipe_data, str):
                                    recipe_dict = json.loads(recipe_data)
                                else:
                                    recipe_dict = recipe_data
                                
                                recipe_str = ", ".join([f"{amt}x {item.replace('_', ' ').title()}" for item, amt in recipe_dict.items()])
                                status += f"   Recipe: {recipe_str}\n"
                            except:
                                pass
                    else:
                        status += f"🔒 {tier_name}\n"
                
                display_name = tool_type.title().replace("_", " ")
                embed.add_field(name=f"{display_name}s", value=status or "None", inline=False)
        else:
            embed.add_field(
                name="No Tool Data",
                value="Tool progression data is being loaded...",
                inline=False
            )
        
        embed.set_footer(text="Use /craft <item_id> to craft upgrades!")
        return embed
    
    async def get_stats_embed(self):
        player = await self.bot.db.get_player(self.user_id)
        skills = await self.bot.db.get_skills(self.user_id)
        
        embed = discord.Embed(
            title="📊 Progression Statistics",
            description="Your overall progress and stats",
            color=discord.Color.green()
        )
        
        if player:
            embed.add_field(
                name="💰 Economy",
                value=f"Coins: {player.get('coins', 0):,}\nBank: {player.get('bank', 0):,}\nNet Worth: {(player.get('coins', 0) + player.get('bank', 0)):,}",
                inline=True
            )
            
            embed.add_field(
                name="⚔️ Combat Stats",
                value=f"Health: {player.get('health', 100)}/{player.get('max_health', 100)}\nDefense: {player.get('defense', 0)}\nStrength: {player.get('strength', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="🔮 Magic Stats",
                value=f"Mana: {player.get('mana', 20)}/{player.get('max_mana', 20)}\nIntelligence: {player.get('intelligence', 0)}",
                inline=True
            )
        
        if skills:
            skill_text = ""
            total_level = 0
            skill_count = 0
            
            for skill in skills:
                skill_name = skill.get('skill_name', 'Unknown')
                level = skill.get('level', 0)
                total_level += level
                skill_count += 1
                
                skill_display = skill_name.title()
                skill_text += f"{skill_display}: {level}\n"
            
            avg_skill = total_level / skill_count if skill_count > 0 else 0
            
            embed.add_field(
                name=f"🎓 Skills (Avg: {avg_skill:.1f})",
                value=skill_text[:1024] if skill_text else "No skills yet",
                inline=False
            )
        
        achievements = await self.bot.db.get_achievements(self.user_id)
        embed.add_field(
            name="🏅 Achievements",
            value=f"{len(achievements)} unlocked",
            inline=True
        )
        
        embed.set_footer(text="Keep playing to improve your stats!")
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.milestones_button)
        self.add_item(self.tools_button)
        self.add_item(self.stats_button)
