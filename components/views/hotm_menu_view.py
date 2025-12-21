import discord
from components.buttons.hotm_buttons import (
    HotmMainButton,
    HotmPerksButton,
    HotmCommissionsButton,
    HotmCrystalNucleusButton,
    HotmUnlockPerkButton,
    HotmRefreshButton
)


class HotmMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.hotm_data = None
        self.perks = None
        self.commissions = None
        self.message = None
        
        self.add_item(HotmMainButton(self))
        self.add_item(HotmPerksButton(self))
        self.add_item(HotmCommissionsButton(self))
        self.add_item(HotmCrystalNucleusButton(self))
        self.add_item(HotmUnlockPerkButton(self))
        self.add_item(HotmRefreshButton(self))
        
        self._update_buttons()
    
    async def refresh_data(self):
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        from utils.systems.dwarven_mines_system import DwarvenMinesSystem
        
        self.hotm_data = await HeartOfTheMountainSystem.get_hotm_data(self.bot.db, self.user_id)
        
        if self.current_view == 'perks':
            await self.load_perks()
        elif self.current_view == 'commissions':
            await self.load_commissions()
    
    async def load_perks(self):
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        
        self.hotm_data = await HeartOfTheMountainSystem.get_hotm_data(self.bot.db, self.user_id)
        self.perks = await HeartOfTheMountainSystem.get_available_perks(self.bot.db, self.user_id)
    
    async def load_commissions(self):
        from utils.systems.dwarven_mines_system import DwarvenMinesSystem
        
        self.commissions = await DwarvenMinesSystem.get_active_commissions(self.bot.db, self.user_id)
        
        if not self.commissions:
            self.commissions = await DwarvenMinesSystem.generate_daily_commissions(self.bot.db, self.user_id)
    
    def _update_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "hotm_unlock":
                    item.disabled = self.current_view != 'perks'
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'perks':
            return await self.get_perks_embed()
        elif self.current_view == 'commissions':
            return await self.get_commissions_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        
        if not self.hotm_data:
            self.hotm_data = await HeartOfTheMountainSystem.get_hotm_data(self.bot.db, self.user_id)
        
        player_perks = await HeartOfTheMountainSystem.get_player_perks(self.bot.db, self.user_id)
        
        embed = discord.Embed(
            title="⛏️ Heart of the Mountain",
            description=f"Your mining progression system",
            color=discord.Color.orange()
        )
        
        current_tier = self.hotm_data['hotm_tier']
        current_xp = self.hotm_data['hotm_xp']
        next_tier = current_tier + 1
        
        if next_tier in HeartOfTheMountainSystem.HOTM_TIERS:
            xp_needed = HeartOfTheMountainSystem.HOTM_TIERS[next_tier]['xp_required']
            progress = (current_xp / xp_needed) * 100
            embed.add_field(
                name=f"Tier {current_tier}",
                value=f"Progress: {progress:.1f}%\n{current_xp:,}/{xp_needed:,} XP",
                inline=False
            )
        else:
            embed.add_field(name=f"Tier {current_tier}", value="MAX TIER", inline=False)
        
        embed.add_field(
            name="💎 Tokens of the Mountain",
            value=f"{self.hotm_data['token_of_the_mountain']} available",
            inline=True
        )
        
        embed.add_field(
            name="⛏️ Mithril Powder",
            value=f"{self.hotm_data['powder_mithril']:,}",
            inline=True
        )
        
        embed.add_field(
            name="💎 Gemstone Powder",
            value=f"{self.hotm_data['powder_gemstone']:,}",
            inline=True
        )
        
        if player_perks:
            perk_text = "\n".join([f"• {p['perk_name']} ({p['perk_level']}/{p['max_level']})" for p in player_perks[:10]])
            embed.add_field(name="Active Perks", value=perk_text or "None", inline=False)
        
        return embed
    
    async def get_perks_embed(self):
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        
        if not self.hotm_data:
            self.hotm_data = await HeartOfTheMountainSystem.get_hotm_data(self.bot.db, self.user_id)
        
        if not self.perks:
            await self.load_perks()
        
        embed = discord.Embed(
            title="⛏️ HOTM Perks",
            description=f"Tokens Available: {self.hotm_data['token_of_the_mountain']}",
            color=discord.Color.gold()
        )
        
        if self.perks:
            for tier in range(1, self.hotm_data['hotm_tier'] + 1):
                tier_perks = [p for p in self.perks if p['tier'] == tier]
                if tier_perks:
                    perk_text = ""
                    for perk in tier_perks[:5]:
                        current = perk.get('current_level', 0)
                        cost = perk.get('next_cost', 1)
                        status = "✅" if current >= perk['max_level'] else f"💎 {cost}"
                        perk_text += f"{perk['perk_name']} ({current}/{perk['max_level']}) - {status}\n"
                    
                    embed.add_field(name=f"Tier {tier}", value=perk_text, inline=False)
        
        embed.set_footer(text="Click 'Unlock Perk' to upgrade a perk")
        
        return embed
    
    async def get_commissions_embed(self):
        from utils.systems.dwarven_mines_system import DwarvenMinesSystem
        
        if not self.commissions:
            await self.load_commissions()
        
        dwarven_progress = await DwarvenMinesSystem.get_dwarven_progress(self.bot.db, self.user_id)
        
        embed = discord.Embed(
            title="📋 Daily Commissions",
            description=f"Reputation: {dwarven_progress['reputation']}\nCompleted: {dwarven_progress['commissions_completed']}",
            color=discord.Color.blue()
        )
        
        if self.commissions:
            for comm in self.commissions:
                progress_bar = "█" * int((comm['progress'] / comm['requirement']) * 10)
                progress_bar += "░" * (10 - len(progress_bar))
                
                status = "✅ COMPLETE" if comm.get('completed', 0) else f"{comm['progress']}/{comm['requirement']}"
                
                embed.add_field(
                    name=f"{comm['name']}",
                    value=f"{comm['description']}\n{progress_bar} {status}\nRewards: {comm['reward_mithril']}💎 Mithril, {comm['reward_coins']}🪙",
                    inline=False
                )
        
        embed.set_footer(text="Complete commissions to earn Mithril Powder and reputation!")
        
        return embed
