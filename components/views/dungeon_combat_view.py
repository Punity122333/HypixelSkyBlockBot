import random
from typing import Optional, TYPE_CHECKING
import discord
from discord.ui import View, Button
from utils.stat_calculator import StatCalculator
from utils.systems.combat_system import CombatSystem
from utils.systems.party_system import PartySystem

if TYPE_CHECKING:
    from main import SkyblockBot

class DungeonCombatView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, mob_name: str, mob_health: int, mob_damage: int, mob_defense: int, dungeon_view, party_id: Optional[int] = None):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.mob_name = mob_name
        self.mob_health = mob_health
        self.mob_max_health = mob_health
        self.mob_damage = mob_damage
        self.mob_defense = mob_defense
        self.dungeon_view = dungeon_view
        self.party_id = party_id
        self.player_health: Optional[int] = None
        self.player_max_health: Optional[int] = None
        self.message: Optional[discord.Message] = None
        self.is_defending = False
        
        self.party_member_healths = {}
        self.party_member_max_healths = {}
        
        self.dungeon_view_buttons_backup = []
        for child in list(self.dungeon_view.children):
            self.dungeon_view_buttons_backup.append(child)
            self.dungeon_view.remove_item(child)
        
        self.add_item(Button(label="⚔️ Attack", style=discord.ButtonStyle.red, custom_id="dungeon_combat_attack", row=0))
        self.add_item(Button(label="🛡️ Defend", style=discord.ButtonStyle.blurple, custom_id="dungeon_combat_defend", row=0))
        self.add_item(Button(label="🏃 Continue", style=discord.ButtonStyle.gray, custom_id="dungeon_combat_run", row=0, disabled=True))
        
        for item in self.children:
            if isinstance(item, Button) and item.custom_id:
                item.callback = self.create_callback(item.custom_id)
    
    def create_callback(self, button_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Only the dungeon author can use combat buttons!", ephemeral=True)
                return
            
            if self.player_health is None:
                player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
                self.player_health = int(player_stats['health'])
                self.player_max_health = int(player_stats['health'])
            
            if button_id == "dungeon_combat_attack":
                await self.handle_attack(interaction)
            elif button_id == "dungeon_combat_defend":
                await self.handle_defend(interaction)
            elif button_id == "dungeon_combat_run":
                await self.handle_continue(interaction)
        
        return callback
    
    async def handle_attack(self, interaction: discord.Interaction):
        if self.player_health is None:
            player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
            self.player_health = int(player_stats['health'])
            self.player_max_health = int(player_stats['health'])
            
            if self.party_id:
                party = PartySystem.get_party_by_id(self.party_id)
                if party:
                    for member in party['members']:
                        member_stats = await StatCalculator.calculate_full_stats(self.bot.db, member['user_id'])
                        self.party_member_healths[member['user_id']] = int(member_stats['health'])
                        self.party_member_max_healths[member['user_id']] = int(member_stats['health'])
        
        total_party_damage = 0
        party_members = []
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                party_members = party['members']
                for member in party_members:
                    member_damage_result = await CombatSystem.calculate_player_damage(
                        self.bot.db, member['user_id'], self.mob_defense
                    )
                    total_party_damage += int(member_damage_result['damage'])
        else:
            damage_result = await CombatSystem.calculate_player_damage(
                self.bot.db, self.user_id, self.mob_defense
            )
            total_party_damage = int(damage_result['damage'])
        
        damage_result = await CombatSystem.calculate_player_damage(
            self.bot.db, self.user_id, self.mob_defense
        )
        is_crit = damage_result['is_crit']
        
        self.mob_health -= total_party_damage
        
        result = f"⚔️ You dealt **{total_party_damage}** damage"
        if is_crit:
            result += " ✨ **CRIT!**"
        result += f" to the {self.mob_name}!"
        
        if self.party_id and len(party_members) > 1:
            result += f"\n👥 Combined party damage from {len(party_members)} members!"
        
        if self.mob_health <= 0:
            await self.handle_victory(interaction, result)
            return
        
        defense_multiplier = 0.5 if self.is_defending else 1.0
        self.is_defending = False
        
        player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
        player_defense = player_stats.get('defense', 0)
        mob_damage_dealt = int(CombatSystem._calculate_mob_damage(self.mob_damage, player_defense) * defense_multiplier)
        
        if self.party_id and len(party_members) > 1:
            for member in party_members:
                member_health = self.party_member_healths.get(member['user_id'], 0)
                if member_health > 0:
                    member_health -= mob_damage_dealt
                    self.party_member_healths[member['user_id']] = member_health
                    
                    player = await self.bot.db.get_player(member['user_id'])
                    if player:
                        await self.bot.db.update_player(member['user_id'], current_health=max(0, member_health))
            
            all_dead = all(hp <= 0 for hp in self.party_member_healths.values())
            
            if all_dead:
                await self.handle_defeat(interaction, result + f"\n💥 All party members took **{mob_damage_dealt}** damage!\n👥 The entire party has been wiped out!")
                return
            
            alive_count = sum(1 for hp in self.party_member_healths.values() if hp > 0)
            result += f"\n💥 All party members took **{mob_damage_dealt}** damage! ({alive_count}/{len(party_members)} alive)"
        else:
            self.player_health = (self.player_health or 0) - mob_damage_dealt
            self.dungeon_view.current_health = self.player_health
            self.dungeon_view.total_damage += mob_damage_dealt
            
            result += f"\n💥 {self.mob_name} dealt **{mob_damage_dealt}** damage to you!"
            
            if self.player_health <= 0:
                await self.handle_defeat(interaction, result)
                return
        
        embed = discord.Embed(
            title=f"⚔️ Fighting {self.mob_name}",
            description=result,
            color=discord.Color.red()
        )
        
        if self.party_id and len(party_members) > 1:
            total_party_health = sum(max(0, hp) for hp in self.party_member_healths.values())
            total_party_max_health = sum(self.party_member_max_healths.values())
            embed.add_field(name="Total Party Health", value=f"❤️ {total_party_health}/{total_party_max_health}", inline=True)
            
            health_bars = []
            for member in party_members:
                member_hp = self.party_member_healths.get(member['user_id'], 0)
                member_max_hp = self.party_member_max_healths.get(member['user_id'], 100)
                member_name = member.get('username', f"Player {member['user_id']}")
                status = "💀" if member_hp <= 0 else "❤️"
                health_bars.append(f"{status} {member_name}: {max(0, member_hp)}/{member_max_hp}")
            
            embed.add_field(name="Party Members", value="\n".join(health_bars), inline=False)
        else:
            embed.add_field(name="Your Health", value=f"❤️ {self.player_health}/{self.player_max_health}", inline=True)
        
        embed.add_field(name="Enemy Health", value=f"💀 {self.mob_health}/{self.mob_max_health}", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_defend(self, interaction: discord.Interaction):
        self.is_defending = True
        
        player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
        player_defense = player_stats.get('defense', 0)
        mob_damage_dealt = int(CombatSystem._calculate_mob_damage(self.mob_damage, player_defense) * 0.5)
        
        party_members = []
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                party_members = party['members']
        
        if self.party_id and len(party_members) > 1:
            for member in party_members:
                member_health = self.party_member_healths.get(member['user_id'], 0)
                if member_health > 0:
                    member_health -= mob_damage_dealt
                    self.party_member_healths[member['user_id']] = member_health
                    
                    player = await self.bot.db.get_player(member['user_id'])
                    if player:
                        await self.bot.db.update_player(member['user_id'], current_health=max(0, member_health))
            
            all_dead = all(hp <= 0 for hp in self.party_member_healths.values())
            
            result = f"🛡️ Party defended! Only took **{mob_damage_dealt}** damage each (50% reduced)"
            
            if all_dead:
                await self.handle_defeat(interaction, result + f"\n👥 The entire party has been wiped out!")
                return
            
            alive_count = sum(1 for hp in self.party_member_healths.values() if hp > 0)
            result += f"\n({alive_count}/{len(party_members)} party members alive)"
        else:
            self.player_health = (self.player_health or 0) - mob_damage_dealt
            self.dungeon_view.current_health = self.player_health
            self.dungeon_view.total_damage += mob_damage_dealt
            
            result = f"🛡️ You defended! Only took **{mob_damage_dealt}** damage (50% reduced)"
            
            if self.player_health <= 0:
                await self.handle_defeat(interaction, result)
                return
        
        embed = discord.Embed(
            title=f"⚔️ Fighting {self.mob_name}",
            description=result,
            color=discord.Color.blurple()
        )
        
        if self.party_id and len(party_members) > 1:
            total_party_health = sum(max(0, hp) for hp in self.party_member_healths.values())
            total_party_max_health = sum(self.party_member_max_healths.values())
            embed.add_field(name="Total Party Health", value=f"❤️ {total_party_health}/{total_party_max_health}", inline=True)
            
            health_bars = []
            for member in party_members:
                member_hp = self.party_member_healths.get(member['user_id'], 0)
                member_max_hp = self.party_member_max_healths.get(member['user_id'], 100)
                member_name = member.get('username', f"Player {member['user_id']}")
                status = "💀" if member_hp <= 0 else "❤️"
                health_bars.append(f"{status} {member_name}: {max(0, member_hp)}/{member_max_hp}")
            
            embed.add_field(name="Party Members", value="\n".join(health_bars), inline=False)
        else:
            embed.add_field(name="Your Health", value=f"❤️ {self.player_health}/{self.player_max_health}", inline=True)
        
        embed.add_field(name="Enemy Health", value=f"💀 {self.mob_health}/{self.mob_max_health}", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_victory(self, interaction: discord.Interaction, result: str):
        coins = random.randint(50, 150)
        self.dungeon_view.coins_gained_in_run += coins
        
        if random.random() > 0.6:
            secret_count = random.randint(1, 2)
            self.dungeon_view.secrets_found += secret_count
            result += f"\n✨ Found {secret_count} secret(s) while fighting!"
        
        embed = discord.Embed(
            title=f"✅ {self.mob_name} Defeated!",
            description=result + f"\n\n💰 Gained {coins} coins!",
            color=discord.Color.green()
        )
        
        for child in self.children:
            if isinstance(child, Button):
                if child.custom_id == "dungeon_combat_run":
                    child.disabled = False
                    child.label = "➡️ Continue"
                else:
                    child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_defeat(self, interaction: discord.Interaction, result: str):
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                for member in party['members']:
                    member_max_health = self.party_member_max_healths.get(member['user_id'], 100)
                    respawn_health = member_max_health // 2
                    self.party_member_healths[member['user_id']] = respawn_health
                    
                    player = await self.bot.db.get_player(member['user_id'])
                    if player:
                        await self.bot.db.update_player(member['user_id'], current_health=respawn_health)
        
        self.dungeon_view.death_count += 1
        self.dungeon_view.current_health = self.dungeon_view.max_health // 2 if self.dungeon_view.max_health else 50
        self.player_health = self.dungeon_view.current_health
        
        embed = discord.Embed(
            title=f"💀 You Died!",
            description=result + f"\n\n💀 Deaths: {self.dungeon_view.death_count}\nRespawning with half health...",
            color=discord.Color.dark_red()
        )
        
        for child in self.children:
            if isinstance(child, Button):
                if child.custom_id == "dungeon_combat_run":
                    child.disabled = False
                    child.label = "➡️ Continue"
                else:
                    child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_continue(self, interaction: discord.Interaction):
        for child in self.dungeon_view_buttons_backup:
            self.dungeon_view.add_item(child)
        
        embed = discord.Embed(
            title=f"🏰 {self.dungeon_view.floor_name} - Room {self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}",
            description="Continue exploring the dungeon!",
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ Health", value=f"{self.dungeon_view.current_health or 0}/{self.dungeon_view.max_health or 0}", inline=True)
        embed.add_field(name="🗝️ Keys", value=str(self.dungeon_view.keys), inline=True)
        embed.add_field(name="✨ Secrets", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)
        embed.add_field(name="💀 Deaths", value=str(self.dungeon_view.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.dungeon_view.wither_doors_unlocked} B:{self.dungeon_view.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(self.dungeon_view.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self.dungeon_view)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Only the dungeon author can use combat buttons!", ephemeral=True)
            return False
        return True
