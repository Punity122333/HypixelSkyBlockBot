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
        self.add_item(Button(label="✨ Ability", style=discord.ButtonStyle.green, custom_id="dungeon_combat_ability", row=0))
        self.add_item(Button(label="🏃 Continue", style=discord.ButtonStyle.gray, custom_id="dungeon_combat_run", row=0, disabled=True))
        
        for item in self.children:
            if isinstance(item, Button) and item.custom_id:
                item.callback = self.create_callback(item.custom_id)
    
    def _create_health_bar(self, current: int, maximum: int) -> str:
        percentage = current / maximum if maximum > 0 else 0
        filled = int(percentage * 20)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}]"
    
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
            elif button_id == "dungeon_combat_ability":
                await self.handle_ability(interaction)
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
        
        mob_health_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        embed.add_field(name="Enemy Health", value=f"💀 {self.mob_health}/{self.mob_max_health}\n{mob_health_bar}", inline=True)
        
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
        
        mob_health_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        embed.add_field(name="Enemy Health", value=f"💀 {self.mob_health}/{self.mob_max_health}\n{mob_health_bar}", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_ability(self, interaction: discord.Interaction):
        if self.player_health is None:
            player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
            self.player_health = int(player_stats['health'])
            self.player_max_health = int(player_stats['health'])
        
        weapon_info = await CombatSystem.get_equipped_weapon_info(self.bot.db, self.user_id)
        
        from utils.systems.weapon_abilities import WeaponAbilities
        
        ability_damage = 0
        mana_cost = 50
        ability_name = "Generic Ability"
        
        if weapon_info:
            weapon_id = weapon_info['item_id']
            has_weapon_ability = await WeaponAbilities.has_ability(self.bot.db, weapon_id)
            
            if has_weapon_ability:
                ability = await WeaponAbilities.get_ability(self.bot.db, weapon_id)
                if ability:
                    ability_name = ability.get('ability_name', 'Weapon Ability')
                    mana_cost = ability.get('mana_cost', 50)
                    
                    weapon_damage, _ = await CombatSystem._get_equipped_weapon_damage_and_tier(self.bot.db, self.user_id)
                    full_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
                    full_stats['user_id'] = self.user_id
                    ability_damage = int(await WeaponAbilities.calculate_ability_damage(
                        self.bot.db, weapon_id, full_stats, weapon_damage
                    ))
        
        if ability_damage == 0:
            player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
            combat_effects = StatCalculator.apply_combat_effects(player_stats, None)
            ability_multiplier = 3 + (player_stats.get('ability_damage', 0) / 100)
            ability_damage = int(combat_effects['base_damage'] * ability_multiplier)
        
        player = await self.bot.db.get_player(self.user_id)
        current_mana = player.get('mana', 0) if player else 0
        
        if current_mana < mana_cost:
            await interaction.response.send_message("❌ Not enough mana!", ephemeral=True)
            return
        
        self.mob_health -= ability_damage
        
        await self.bot.db.update_player(self.user_id, mana=current_mana - mana_cost)
        
        result = f"✨ **{ability_name}** dealt {ability_damage} damage! (-{mana_cost} mana)"
        
        if self.mob_health <= 0:
            await self.handle_victory(interaction, result)
            return
        
        defense_multiplier = 0.5 if self.is_defending else 1.0
        self.is_defending = False
        
        player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
        player_defense = player_stats.get('defense', 0)
        mob_damage_dealt = int(CombatSystem._calculate_mob_damage(self.mob_damage, player_defense) * defense_multiplier)
        
        self.player_health = (self.player_health or 0) - mob_damage_dealt
        self.dungeon_view.current_health = self.player_health
        self.dungeon_view.total_damage += mob_damage_dealt
        
        result += f"\n🩸 {self.mob_name} dealt {mob_damage_dealt} damage to you!"
        
        if self.player_health <= 0:
            await self.handle_defeat(interaction, result)
            return
        
        embed = discord.Embed(
            title=f"⚔️ Fighting {self.mob_name}",
            description=result,
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Your Health", value=f"❤️ {self.player_health}/{self.player_max_health}", inline=True)
        mob_health_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        embed.add_field(name="Enemy Health", value=f"💀 {self.mob_health}/{self.mob_max_health}\n{mob_health_bar}", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_victory(self, interaction: discord.Interaction, result: str):
        coins = random.randint(50, 150)
        self.dungeon_view.coins_gained_in_run += coins
        
        if random.random() > 0.6:
            secret_count = random.randint(1, 2)
            self.dungeon_view.secrets_found += secret_count
            result += f"\n✨ Found {secret_count} secret(s) while fighting!"
        
        # Check if this was a boss (all rooms cleared)
        is_boss = self.dungeon_view.rooms_cleared > self.dungeon_view.total_rooms
        
        if is_boss:
            # Boss defeated - trigger dungeon completion
            await self._complete_dungeon_after_boss(interaction, result)
            return
        
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
    
    async def _complete_dungeon_after_boss(self, interaction: discord.Interaction, combat_result: str):
        await interaction.response.defer()
        
        from utils.systems.party_system import PartySystem
        from utils.normalize import normalize_item_id
        from utils.compat import roll_loot as compat_roll_loot
        
        floor_id = self.dungeon_view.floor_name.lower().replace(' ', '')
        score = self.dungeon_view._calculate_score()
        
        score += 100
        boss_coins = random.randint(500, 1000)
        self.dungeon_view.coins_gained_in_run += boss_coins
        
        floor_key = normalize_item_id(self.dungeon_view.floor_name)
        loot_table = await self.bot.game_data.get_loot_table(floor_key, 'dungeon')
        if not loot_table:
            loot_table = {}
        
        player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
        magic_find = player_stats.get('magic_find', 0)
        
        drops = await CombatSystem.roll_combat_loot(
            self.bot.game_data, 
            self.bot.db, 
            self.user_id, 
            loot_table, 
            magic_find
        )
        dungeon_loot = await self.dungeon_view._roll_dungeon_loot(floor_key, score, magic_find)
        
        combat_drop_yield = await CombatSystem._get_combat_drop_yield_multiplier(
            self.bot.db, self.user_id
        )
        dungeon_loot = [(item_id, max(1, int(amount * combat_drop_yield))) for item_id, amount in dungeon_loot]
        
        items_obtained = []
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                member_ids = [m['user_id'] for m in party['members']]
                
                for member_id in member_ids:
                    member_stats = await StatCalculator.calculate_full_stats(self.bot.db, member_id)
                    member_magic_find = member_stats.get('magic_find', 0)
                    
                    member_drops = await CombatSystem.roll_combat_loot(
                        self.bot.game_data, 
                        self.bot.db, 
                        member_id, 
                        loot_table, 
                        member_magic_find
                    )
                    member_dungeon_loot = await self.dungeon_view._roll_dungeon_loot(floor_key, score, member_magic_find)
                    
                    member_combat_drop_yield = await CombatSystem._get_combat_drop_yield_multiplier(
                        self.bot.db, member_id
                    )
                    member_dungeon_loot = [(item_id, max(1, int(amount * member_combat_drop_yield))) for item_id, amount in member_dungeon_loot]
                    
                    for item_id, amount in member_drops:
                        await self.bot.db.add_item_to_inventory(member_id, item_id, amount)
                        if member_id == self.user_id:
                            items_obtained.append(f"{item_id.replace('_', ' ').title()} x{amount}")
                    
                    for item_id, amount in member_dungeon_loot:
                        await self.bot.db.add_item_to_inventory(member_id, item_id, amount)
                        if member_id == self.user_id:
                            items_obtained.append(f"✨ {item_id.replace('_', ' ').title()} x{amount}")
        else:
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                items_obtained.append(f"{item_id.replace('_', ' ').title()} x{amount}")
            
            for item_id, amount in dungeon_loot:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                items_obtained.append(f"✨ {item_id.replace('_', ' ').title()} x{amount}")
        
        coin_rewards = (self.dungeon_view.rooms_cleared * 100) + (self.dungeon_view.secrets_found * 50) - (self.dungeon_view.death_count * 50)
        xp_rewards = (self.dungeon_view.rooms_cleared * 20) + (self.dungeon_view.secrets_found * 10) + 100
        total_rewards = coin_rewards + self.dungeon_view.coins_gained_in_run
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                member_data = party['members']
                coins_per_member = total_rewards // len(member_data)
                
                for member in member_data:
                    member_id = member['user_id']
                    await self.bot.player_manager.add_coins(member_id, coins_per_member)
        else:
            await self.bot.player_manager.add_coins(self.user_id, total_rewards)
        
        embed = discord.Embed(
            title=f"🏆 {self.dungeon_view.floor_name} CLEARED!",
            description=f"**BOSS DEFEATED!**\n{combat_result}\n\n💰 +{boss_coins} bonus coins!\n\n**Final Score: {score}**",
            color=discord.Color.gold()
        )
        embed.add_field(name="Rooms Cleared", value=f"{self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}", inline=True)
        embed.add_field(name="Secrets Found", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)
        embed.add_field(name="Deaths", value=str(self.dungeon_view.death_count), inline=True)
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                member_data = party['members']
                coins_per_member = total_rewards // len(member_data)
                embed.add_field(name="💰 Coins Per Member", value=f"{coins_per_member} coins", inline=True)
                embed.set_footer(text=f"🎁 Each of the {len(member_data)} party members received their own loot drops!")
        else:
            embed.add_field(name="💰 Total Coins", value=f"{total_rewards} coins", inline=True)
        
        if items_obtained:
            items_display = "\n".join(items_obtained[:10])
            if len(items_obtained) > 10:
                items_display += f"\n... and {len(items_obtained) - 10} more items!"
            embed.add_field(name="🎁 Your Loot", value=items_display, inline=False)
        else:
            embed.add_field(name="🎁 Your Loot", value="No items dropped this time!", inline=False)
        
        embed.add_field(name="⭐ XP Gained", value=f"{xp_rewards} XP", inline=True)
        
        self.dungeon_view.stop()
        self.stop()
        
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        
        try:
            await interaction.edit_original_response(embed=embed, view=self)
        except:
            if interaction.message:
                await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=self)
        
        await self.bot.db.increment_dungeon_stats(
            self.user_id,
            total_runs=1,
            secrets_found=self.dungeon_view.secrets_found,
            total_deaths=self.dungeon_view.death_count,
            catacombs_xp=xp_rewards
        )
        
        dungeon_stats_row = await self.bot.db.get_dungeon_stats(self.user_id)
        if dungeon_stats_row:
            from utils.data.skills import calculate_level_from_xp as skills_calculate_level
            current_cata_xp = dungeon_stats_row['catacombs_xp'] or 0
            current_cata_level = dungeon_stats_row['catacombs_level'] or 0
            new_cata_level = skills_calculate_level('dungeoneering', current_cata_xp)
            if new_cata_level != current_cata_level:
                await self.bot.db.update_dungeon_stats(self.user_id, catacombs_level=new_cata_level)
        
        dungeon_stats_row = await self.bot.db.get_dungeon_stats(self.user_id)
        if dungeon_stats_row:
            dungeon_stats = dict(dungeon_stats_row)
            from utils.systems.achievement_system import AchievementSystem
            total_dungeons = dungeon_stats.get('total_runs', 0)
            await AchievementSystem.check_dungeon_achievements(self.bot.db, interaction, self.user_id, total_dungeons)
            
            if score >= 300:
                await AchievementSystem.unlock_action_achievement(self.bot.db, interaction, self.user_id, 'dungeon_s_rank')
            
            if self.dungeon_view.death_count == 0:
                await AchievementSystem.unlock_action_achievement(self.bot.db, interaction, self.user_id, 'dungeon_no_death')
        
        stats_row = await self.bot.db.get_dungeon_stats(self.user_id)
        stats = dict(stats_row) if stats_row else {}
        if not stats or score > stats.get('best_score', 0):
            await self.bot.db.update_dungeon_stats(self.user_id, best_score=score)
        
        from utils.systems.badge_system import BadgeSystem
        if dungeon_stats_row:
            dungeon_stats = dict(dungeon_stats_row)
            total_runs = dungeon_stats.get('total_runs', 0)
            if total_runs == 1:
                await BadgeSystem.unlock_badge(self.bot.db, self.user_id, 'first_dungeon')
            elif total_runs >= 100:
                await BadgeSystem.unlock_badge(self.bot.db, self.user_id, 'dungeon_master')
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                await PartySystem.end_dungeon(self.bot.db, self.party_id)
    
    async def handle_continue(self, interaction: discord.Interaction):
        from components.views.dungeon_view import DungeonView
        
        new_view = DungeonView(
            self.bot,
            self.user_id,
            self.dungeon_view.floor_name,
            self.dungeon_view.floor_data,
            self.dungeon_view.party_id
        )
        
        new_view.rooms_cleared = self.dungeon_view.rooms_cleared
        new_view.total_rooms = self.dungeon_view.total_rooms
        new_view.current_health = self.dungeon_view.current_health
        new_view.max_health = self.dungeon_view.max_health
        new_view.keys = self.dungeon_view.keys
        new_view.wither_doors_unlocked = self.dungeon_view.wither_doors_unlocked
        new_view.blood_doors_unlocked = self.dungeon_view.blood_doors_unlocked
        new_view.total_damage = self.dungeon_view.total_damage
        new_view.secrets_found = self.dungeon_view.secrets_found
        new_view.max_secrets = self.dungeon_view.max_secrets
        new_view.crypts_opened = self.dungeon_view.crypts_opened
        new_view.puzzles_failed = self.dungeon_view.puzzles_failed
        new_view.death_count = self.dungeon_view.death_count
        new_view.room_history = self.dungeon_view.room_history
        new_view.coins_gained_in_run = self.dungeon_view.coins_gained_in_run
        new_view.current_puzzle = self.dungeon_view.current_puzzle
        new_view.party_size = self.dungeon_view.party_size
        new_view.player_stats = self.dungeon_view.player_stats
        
        self.dungeon_view.stop()
        
        embed = discord.Embed(
            title=f"🏰 {new_view.floor_name} - Room {new_view.rooms_cleared}/{new_view.total_rooms}",
            description="Continue exploring the dungeon!",
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ Health", value=f"{new_view.current_health or 0}/{new_view.max_health or 0}", inline=True)
        embed.add_field(name="🗝️ Keys", value=str(new_view.keys), inline=True)
        embed.add_field(name="✨ Secrets", value=f"{new_view.secrets_found}/{new_view.max_secrets}", inline=True)
        embed.add_field(name="💀 Deaths", value=str(new_view.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{new_view.wither_doors_unlocked} B:{new_view.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(new_view.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=new_view)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Only the dungeon author can use combat buttons!", ephemeral=True)
            return False
        return True
