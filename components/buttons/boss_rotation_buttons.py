import discord
from typing import TYPE_CHECKING
from components.views.boss_rotation_combat_view import BossRotationCombatView

if TYPE_CHECKING:
    from components.views.boss_rotation_view import BossRotationView


class BossRotationMainButton(discord.ui.Button):
    def __init__(self, view: "BossRotationView"):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="boss_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        await self.parent_view.load_data()
        embed = await self.parent_view.get_embed()
        self.parent_view._update_buttons()
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class BossRotationFightButton(discord.ui.Button):
    def __init__(self, view: "BossRotationView"):
        super().__init__(label="⚔️ Fight Boss", style=discord.ButtonStyle.red, custom_id="boss_fight", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        boss_data = self.parent_view.boss_data
        if not boss_data:
            boss_data = await self.parent_view.bot.db.boss_rotation.get_current_boss()
        
        from utils.systems.party_system import PartySystem
        party_id = PartySystem._party_by_member.get(interaction.user.id)
        
        from utils.systems.cooperative_boss_system import CooperativeBossSystem
        session = await CooperativeBossSystem.create_coop_boss_session(
            self.parent_view.bot.db,
            boss_data['boss_id'],
            interaction.user.id,
            party_id
        )
        
        loot_table = {}
        
        combat_view = BossRotationCombatView(
            self.parent_view.bot,
            interaction.user.id,
            boss_data['name'],
            boss_data['health'],
            boss_data['damage'],
            boss_data['rewards_coins'],
            boss_data['rewards_xp'],
            loot_table,
            session
        )
        
        from utils.stat_calculator import StatCalculator
        player_stats = await StatCalculator.calculate_player_stats(
            self.parent_view.bot.db, self.parent_view.bot.game_data, interaction.user.id
        )
        player_health = int(player_stats.get('max_health', 100))
        player_mana = int(player_stats.get('max_mana', 100))
        
        combat_view.player_health = player_health
        combat_view.player_max_health = player_health
        combat_view.player_stats = player_stats
        combat_view.current_mana = player_mana
        combat_view.max_mana = player_mana
        
        player_hp_bar = combat_view._create_health_bar(player_health, player_health)
        mob_hp_bar = combat_view._create_health_bar(boss_data['health'], boss_data['health'])
        mana_bar = combat_view._create_health_bar(player_mana, player_mana) if player_mana > 0 else "[No Mana]"
        
        embed = discord.Embed(
            title=f"{boss_data['emoji']} Boss Battle: {boss_data['name']}",
            description=f"**Prepare for battle!**",
            color=discord.Color.dark_gold()
        )
        
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {player_health}/{player_health} HP", inline=False)
        embed.add_field(name="Your Mana", value=f"{mana_bar}\n✨ {player_mana}/{player_mana}", inline=False)
        embed.add_field(name=f"{boss_data['name']} Health", value=f"{mob_hp_bar}\n❤️ {boss_data['health']:,}/{boss_data['health']:,} HP", inline=False)
        
        if party_id:
            party = PartySystem.get_party(party_id)
            if party:
                member_names = [f"<@{m['user_id']}>" for m in party['members']]
                embed.add_field(
                    name="👥 Party Members",
                    value=", ".join(member_names),
                    inline=False
                )
        
        embed.set_footer(text="Choose your action wisely!")
        
        await interaction.followup.send(embed=embed, view=combat_view)
        combat_view.message = await interaction.original_response()


class BossRotationScheduleButton(discord.ui.Button):
    def __init__(self, view: "BossRotationView"):
        super().__init__(label="🗓️ Schedule", style=discord.ButtonStyle.green, custom_id="boss_schedule", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'schedule'
        await self.parent_view.load_data()
        embed = await self.parent_view.get_embed()
        self.parent_view._update_buttons()
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class BossRotationLeaderboardButton(discord.ui.Button):
    def __init__(self, view: "BossRotationView"):
        super().__init__(label="🏆 Leaderboard", style=discord.ButtonStyle.gray, custom_id="boss_leaderboard", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'leaderboard'
        await self.parent_view.load_data()
        embed = await self.parent_view.get_embed()
        self.parent_view._update_buttons()
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class BossRotationRefreshButton(discord.ui.Button):
    def __init__(self, view: "BossRotationView"):
        super().__init__(label="🔄 Refresh", style=discord.ButtonStyle.gray, custom_id="boss_refresh", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await self.parent_view.load_data()
        embed = await self.parent_view.get_embed()
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
