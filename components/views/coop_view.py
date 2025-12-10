import discord
from components.buttons.coop_buttons import (
    CoopCreateButton,
    CoopMainButton,
    CoopMembersButton,
    CoopBankButton,
    CoopMinionsButton,
    CoopInviteButton,
    CoopLeaveButton,
    CoopDepositButton,
    CoopWithdrawButton,
    CoopRefreshButton
)

class CoopView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.coop_data = None
        self.members_data = []
        self.minions_data = []
        
        self.create_button = CoopCreateButton(self)
        self.main_button = CoopMainButton(self)
        self.members_button = CoopMembersButton(self)
        self.bank_button = CoopBankButton(self)
        self.minions_button = CoopMinionsButton(self)
        self.invite_button = CoopInviteButton(self)
        self.leave_button = CoopLeaveButton(self)
        self.deposit_button = CoopDepositButton(self)
        self.withdraw_button = CoopWithdrawButton(self)
        self.refresh_button = CoopRefreshButton(self)
        
        self._update_buttons()
    
    async def load_coop_data(self):
        from utils.systems.coop_system import CoopSystem
        
        self.coop_data = await CoopSystem.get_player_coop(self.bot.db, self.user_id)
        if self.coop_data:
            self.members_data = await CoopSystem.get_coop_members(self.bot.db, self.coop_data['id'])
            self.minions_data = await CoopSystem.get_shared_minions(self.bot.db, self.coop_data['id'])
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'members':
            return await self.get_members_embed()
        elif self.current_view == 'bank':
            return await self.get_bank_embed()
        elif self.current_view == 'minions':
            return await self.get_minions_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        if not self.coop_data:
            embed = discord.Embed(
                title="🤝 Co-op System",
                description="You're not in a co-op. Create one to get started!",
                color=discord.Color.blue()
            )
            embed.add_field(name="Benefits", value="✓ Shared bank\n✓ Shared minions\n✓ Shared island\n✓ Team roles", inline=False)
            return embed
        
        embed = discord.Embed(
            title=f"🤝 {self.coop_data['coop_name']}",
            description="Co-op Overview",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Members", value=str(len(self.members_data)), inline=True)
        embed.add_field(name="Shared Bank", value=f"{self.coop_data['shared_bank']:,} coins", inline=True)
        embed.add_field(name="Total Minions", value=str(len(self.minions_data)), inline=True)
        
        return embed
    
    async def get_members_embed(self):
        if not self.coop_data:
            return await self.get_main_embed()
        
        embed = discord.Embed(
            title=f"🤝 {self.coop_data['coop_name']} - Members",
            description="Co-op member list",
            color=discord.Color.blue()
        )
        
        member_list = []
        for member in self.members_data:
            role_emoji = "👑" if member['role'] == 'owner' else "⭐" if member['role'] == 'admin' else "👤"
            member_list.append(f"{role_emoji} **{member['username']}** - {member['role'].title()}")
        
        embed.add_field(name=f"Members ({len(self.members_data)})", value='\n'.join(member_list) if member_list else "No members", inline=False)
        
        return embed
    
    async def get_bank_embed(self):
        if not self.coop_data:
            return await self.get_main_embed()
        
        embed = discord.Embed(
            title=f"🤝 {self.coop_data['coop_name']} - Bank",
            description="Shared bank management",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Balance", value=f"{self.coop_data['shared_bank']:,} coins", inline=True)
        embed.add_field(name="Capacity", value=f"{self.coop_data['bank_capacity']:,} coins", inline=True)
        
        usage_percent = (self.coop_data['shared_bank'] / self.coop_data['bank_capacity'] * 100) if self.coop_data['bank_capacity'] > 0 else 0
        embed.add_field(name="Usage", value=f"{usage_percent:.1f}%", inline=True)
        
        return embed
    
    async def get_minions_embed(self):
        if not self.coop_data:
            return await self.get_main_embed()
        
        embed = discord.Embed(
            title=f"🤝 {self.coop_data['coop_name']} - Minions",
            description="Shared minions",
            color=discord.Color.purple()
        )
        
        if not self.minions_data:
            embed.add_field(name="No Minions", value="Place minions to see them here", inline=False)
        else:
            minion_list = []
            for minion in self.minions_data[:10]:
                minion_list.append(f"**{minion['minion_type'].replace('_', ' ').title()}** - Level {minion['tier']}")
            
            embed.add_field(name=f"Minions ({len(self.minions_data)})", value='\n'.join(minion_list), inline=False)
        
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        if not self.coop_data:
            self.add_item(self.create_button)
            self.add_item(self.refresh_button)
            return
        
        if self.current_view == 'main':
            self.add_item(self.members_button)
            self.add_item(self.bank_button)
            self.add_item(self.minions_button)
            self.add_item(self.invite_button)
            self.add_item(self.leave_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'members':
            self.add_item(self.main_button)
            self.add_item(self.invite_button)
            self.add_item(self.leave_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'bank':
            self.add_item(self.main_button)
            self.add_item(self.deposit_button)
            self.add_item(self.withdraw_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'minions':
            self.add_item(self.main_button)
            self.add_item(self.refresh_button)
