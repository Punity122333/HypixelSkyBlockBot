import discord
from utils.stat_calculator import StatCalculator
from utils.systems.badge_system import BadgeSystem
from utils.systems.market_graphing_system import MarketGraphingSystem
import json
from components.buttons.profile_buttons import (
    ProfileButton,
    DetailedStatsButton,
    ProfileWardrobeButton,
    ProfileTalismanPouchButton
)

class ProfileMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_view = 'profile'
        self.wardrobe_page = 1
        
        self.add_item(ProfileButton(self))
        self.add_item(DetailedStatsButton(self))
        self.add_item(ProfileWardrobeButton(self))
        self.add_item(ProfileTalismanPouchButton(self))
    
    async def get_embed(self):
        if self.current_view == 'profile':
            return await self.get_profile_embed()
        elif self.current_view == 'stats':
            return await self.get_stats_embed()
        elif self.current_view == 'wardrobe':
            return await self.get_wardrobe_embed()
        elif self.current_view == 'talisman_pouch':
            return await self.get_talisman_pouch_embed()
        else:
            return await self.get_profile_embed()
    
    async def get_profile_embed(self):
        player = await self.bot.player_manager.get_player_fresh(self.user_id)
        stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
        skills = await self.bot.db.get_skills(self.user_id)
        
        embed = discord.Embed(
            title=f"📊 {self.username}'s Profile",
            color=discord.Color.gold()
        )
        
        networth = await MarketGraphingSystem.calculate_networth(self.bot.db, self.user_id)
        badges = await BadgeSystem.get_player_badges(self.bot.db, self.user_id)
        all_badges = await BadgeSystem.get_all_badges(self.bot.db)
        
        await BadgeSystem.check_and_unlock_badges(self.bot.db, self.user_id, 'networth', networth=networth)
        await BadgeSystem.check_and_unlock_badges(self.bot.db, self.user_id, 'coins', coins=player['coins'])
        
        embed.add_field(name="💰 Purse", value=f"{player['coins']:,} coins", inline=True)
        embed.add_field(name="🏦 Bank", value=f"{player['bank']:,} coins", inline=True)
        embed.add_field(name="💎 Networth", value=f"{networth:,.0f} coins", inline=True)
        
        embed.add_field(name="❤️ Health", value=f"{int(stats['health'])}/{int(stats['max_health'])}", inline=True)
        embed.add_field(name="💪 Mana", value=f"{int(stats['max_mana'])}", inline=True)
        embed.add_field(name="🛡️ Defense", value=str(int(stats['defense'])), inline=True)
        
        skill_avg = sum(s['level'] for s in skills) / len(skills) if skills else 0
        embed.add_field(name="📚 Skill Average", value=f"{skill_avg:.2f}", inline=True)
        
        embed.add_field(name="🏅 Badges", value=f"{len(badges)}/{len(all_badges)}", inline=True)
        
        embed.add_field(name="📊 Trading Rep", value=f"{player.get('trading_reputation', 0)}", inline=True)
        
        if badges:
            top_badges = [b['name'] for b in badges[:5]]
            embed.add_field(name="Recent Badges", value='\n'.join(top_badges), inline=False)
        
        progression = await self.bot.db.get_player_progression(self.user_id)
        if progression:
            
            achievements = len(json.loads(progression.get('achievements', '[]')))
            embed.add_field(name="🏆 Achievements", value=f"{achievements} unlocked", inline=True)
        
        stocks = await self.bot.db.get_player_stocks(self.user_id)
        if stocks:
            portfolio_value = sum(s['shares'] * s['current_price'] for s in stocks)
            embed.add_field(name="📈 Portfolio Value", value=f"{int(portfolio_value):,} coins", inline=True)
        
        embed.set_footer(text="Use buttons to view detailed stats • /badges to see all badges")
        return embed
    
    async def get_stats_embed(self):
        stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)

        embed = discord.Embed(
            title=f"📈 {self.username}'s Complete Stats",
            description="All your character statistics",
            color=discord.Color.blue()
        )
        

        embed.add_field(name="❤️ Health", value=f"{int(stats.get('health', 0))}/{int(stats.get('max_health', 0))}", inline=True)
        embed.add_field(name="🛡️ Defense", value=str(int(stats.get('defense', 0))), inline=True)
        embed.add_field(name="⚔️ Strength", value=str(int(stats.get('strength', 0))), inline=True)

        embed.add_field(name="☠️ Crit Chance", value=f"{stats.get('crit_chance', 0):.1f}%", inline=True)
        embed.add_field(name="💥 Crit Damage", value=f"{stats.get('crit_damage', 0):.1f}%", inline=True)
        embed.add_field(name="💢 Ferocity", value=str(int(stats.get('ferocity', 0))), inline=True)

        embed.add_field(name="💙 Max Mana", value=str(int(stats.get('max_mana', 0))), inline=True)
        embed.add_field(name="✨ Intelligence", value=str(int(stats.get('intelligence', 0))), inline=True)
        embed.add_field(name="⚡ Ability Damage", value=f"{stats.get('ability_damage', 0):.1f}%", inline=True)
        
        embed.add_field(name="🏃 Speed", value=str(int(stats.get('speed', 0))), inline=True)
        embed.add_field(name="⚔️ Attack Speed", value=f"{stats.get('attack_speed', 0):.1f}%", inline=True)
        embed.add_field(name="💚 Health Regen", value=f"{stats.get('health_regen', 0):.1f}%", inline=True)

        embed.add_field(name="🛡️ True Defense", value=str(int(stats.get('true_defense', 0))), inline=True)

        embed.add_field(name="🔮 Magic Find", value=str(int(stats.get('magic_find', 0))), inline=True)
        embed.add_field(name="🍀 Pet Luck", value=str(int(stats.get('pet_luck', 0))), inline=True)

        embed.add_field(name="⛏️ Mining Speed", value=str(int(stats.get('mining_speed', 0))), inline=True)
        embed.add_field(name="⛏️ Mining Fortune", value=str(int(stats.get('mining_fortune', 0))), inline=True)

        embed.add_field(name="🌾 Farming Fortune", value=str(int(stats.get('farming_fortune', 0))), inline=True)

        embed.add_field(name="🪓 Foraging Fortune", value=str(int(stats.get('foraging_fortune', 0))), inline=True)

        embed.add_field(name="🎣 Fishing Speed", value=str(int(stats.get('fishing_speed', 0))), inline=True)
        embed.add_field(name="🐟 Sea Creature Chance", value=f"{stats.get('sea_creature_chance', 0):.1f}%", inline=True)
        
        embed.set_footer(text="Use buttons to view profile overview • All stats displayed")
        return embed
    
    async def get_wardrobe_embed(self):
        
        equipped = await self.bot.db.get_equipped_items(self.user_id)
        
        embed = discord.Embed(
            title=f"👔 {self.username}'s Wardrobe",
            description="Equip armor, weapons, and tools to enhance your stats!",
            color=discord.Color.purple()
        )

        equipment_emojis = {
            'helmet': '🪖',
            'chestplate': '🦺',
            'leggings': '👖',
            'boots': '👢',
            'sword': '🗡️',
            'bow': '🏹',
            'pickaxe': '⛏️',
            'axe': '🪓',
            'hoe': '🌾',
            'fishing_rod': '🎣'
        }
        
        for slot, emoji in equipment_emojis.items():
            item = equipped.get(slot)
            if item and 'name' in item:
                item_id = item.get('item_id')
                item_type = item.get('item_type')
                
                stat_display = ""
                if item_type in ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']:
                    armor_stats = await self.bot.db.get_armor_stats(item_id)
                    if armor_stats:
                        top_stats = [(k, v) for k, v in armor_stats.items() if k not in ['item_id'] and v > 0]
                        top_stats.sort(key=lambda x: x[1], reverse=True)
                        stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in top_stats[:3]])
                elif item_type in ['SWORD', 'BOW']:
                    weapon_stats = await self.bot.db.get_weapon_stats(item_id)
                    if weapon_stats:
                        top_stats = [(k, v) for k, v in weapon_stats.items() if k not in ['item_id'] and v > 0]
                        top_stats.sort(key=lambda x: x[1], reverse=True)
                        stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in top_stats[:3]])
                elif item_type in ['PICKAXE', 'AXE', 'HOE', 'SHOVEL', 'FISHING_ROD']:
                    tool_stats = await self.bot.db.get_tool_stats(item_id)
                    if tool_stats:
                        top_stats = [(k, v) for k, v in tool_stats.items() if k not in ['item_id', 'tool_type', 'durability'] and v > 0 and v != 1.0]
                        top_stats.sort(key=lambda x: x[1], reverse=True)
                        stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in top_stats[:3]])
                
                if not stat_display:
                    stats = json.loads(item.get('stats', '{}'))
                    stat_display = '\n'.join([f"{k}: {v}" for k, v in list(stats.items())[:3]])
                
                embed.add_field(
                    name=f"{emoji} {slot.title()}",
                    value=f"**{item['name']}**\n{stat_display if stat_display else 'No stats'}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"{emoji} {slot.title()}",
                    value="*Empty*\n\nClick button to equip",
                    inline=True
                )
        
        active_pet = await self.bot.db.get_active_pet(self.user_id)
        if active_pet:
            from database.misc import get_pet_stats
            pet_type = active_pet['pet_type'].lower()
            rarity = active_pet['rarity'].upper()
            level = active_pet.get('level', 1)
            
            PET_STATS = await get_pet_stats()
            pet_stats = PET_STATS.get(pet_type, {}).get(rarity, {})
            level_multiplier = 1 + (level / 100)
            scaled_stats = {k: int(v * level_multiplier) for k, v in pet_stats.items()}
            
            stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in list(scaled_stats.items())[:3]])
            
            embed.add_field(
                name=f"🐾 Active Pet",
                value=f"**{pet_type.title()} (Lvl {level})**\n{rarity}\n{stat_display if stat_display else 'No stats'}",
                inline=True
            )
        else:
            embed.add_field(
                name=f"🐾 Active Pet",
                value="*None*\n\nEquip a pet for bonuses",
                inline=True
            )
        
        embed.set_footer(text="Use the buttons below to equip or unequip items")
        return embed
    
    async def get_talisman_pouch_embed(self):
        from utils.systems.talisman_pouch_system import TalismanPouchSystem
        
        talismans = await TalismanPouchSystem.get_talisman_pouch(self.bot.db, self.user_id)
        bonuses = await TalismanPouchSystem.get_talisman_bonuses(self.bot.db, self.user_id)
        
        embed = discord.Embed(
            title=f"📿 {self.username}'s Talisman Pouch",
            description=f"Talismans provide passive stat bonuses\n{len(talismans)}/{TalismanPouchSystem.MAX_TALISMANS} slots used",
            color=discord.Color.purple()
        )
        
        if talismans:
            talisman_list = []
            for i, talisman_data in enumerate(talismans):
                talisman_id = talisman_data['talisman_id']
                item = await self.bot.game_data.get_item(talisman_id)
                if item:
                    stats_str = ', '.join([f"+{v} {k.replace('_', ' ').title()}" for k, v in item.stats.items()]) if item.stats else 'No stats'
                    talisman_list.append(f"{i+1}. **{item.name}** ({item.rarity})\n   {stats_str}")
            
            if talisman_list:
                embed.add_field(name="📿 Equipped Talismans", value="\n".join(talisman_list[:8]), inline=True)
                if len(talisman_list) > 8:
                    embed.add_field(name="\u200b", value="\n".join(talisman_list[8:16]), inline=True)
                if len(talisman_list) > 16:
                    embed.add_field(name="\u200b", value="\n".join(talisman_list[16:]), inline=True)
        
        if bonuses:
            stat_list = []
            for stat, value in bonuses.items():
                stat_display = stat.replace('_', ' ').title()
                stat_list.append(f"**{stat_display}:** +{value}")
            
            embed.add_field(name="📊 Total Stat Bonuses", value="\n".join(stat_list) if stat_list else "No bonuses", inline=False)
        else:
            embed.add_field(name="📊 Total Stat Bonuses", value="No bonuses", inline=False)
        
        embed.set_footer(text="Use /talisman_add and /talisman_remove to manage talismans")
        
        return embed
