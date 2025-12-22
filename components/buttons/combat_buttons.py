import discord
import random
from discord.ui import Button
from utils.stat_calculator import StatCalculator
from utils.systems.combat_system import CombatSystem
from utils.normalize import normalize_item_id

class CombatAttackButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⚔️ Attack", style=discord.ButtonStyle.red, custom_id="combat_attack")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()
        
        if self.parent_view.player_stats is None:
            self.parent_view.player_stats = await StatCalculator.calculate_player_stats(self.parent_view.bot.db, self.parent_view.bot.game_data, self.parent_view.user_id)
        
        if self.parent_view.player_health is None:
            self.parent_view.player_health = int(self.parent_view.player_stats['max_health'])
            self.parent_view.player_max_health = int(self.parent_view.player_stats['max_health'])
        
        self.parent_view.player_health = await CombatSystem.apply_health_regeneration(
            self.parent_view.bot.db, self.parent_view.user_id, int(self.parent_view.player_health), int(self.parent_view.player_max_health)
        )
        
        mob_id = self.parent_view.mob_name.lower().replace(' ', '_')
        mob_stats = await self.parent_view.bot.db.get_mob_stats(mob_id)
        mob_defense = mob_stats.get('defense', 0) if mob_stats else 0
        
        damage_result = await CombatSystem.calculate_player_damage(self.parent_view.bot.db, self.parent_view.user_id, mob_defense)
        
        total_damage = int(damage_result['damage'])
        crit = damage_result['is_crit']
        combat_level = damage_result.get('combat_level', 0)
        skill_multiplier = damage_result.get('skill_multiplier', 1.0)
        
        ferocity_hits = 1 + (self.parent_view.player_stats.get('ferocity', 0) // 100)
        if ferocity_hits > 1:
            total_damage = int(total_damage * ferocity_hits)
        
        self.parent_view.mob_health -= total_damage
        
        embed = discord.Embed(title=f"⚔️ Fighting {self.parent_view.mob_name}", color=discord.Color.red())
        
        if self.parent_view.mob_health <= 0:
            mob_id = normalize_item_id(self.parent_view.mob_name)
            loot_table = await self.parent_view.bot.game_data.get_loot_table(self.parent_view.mob_name, 'mob')
            
            if not loot_table:
                loot_table = {}
            
            if 'coins' not in loot_table:
                loot_table['coins'] = (self.parent_view.coins_reward // 2, self.parent_view.coins_reward)
            if 'xp' not in loot_table:
                loot_table['xp'] = self.parent_view.xp_reward
            
            magic_find = self.parent_view.player_stats.get('magic_find', 0)
            fortune = self.parent_view.player_stats.get('looting', 0)
            drops = await CombatSystem.roll_combat_loot(
                self.parent_view.bot.game_data, 
                self.parent_view.bot.db, 
                self.parent_view.user_id, 
                loot_table, 
                magic_find, 
                fortune
            )
            
            items_obtained = []
            for item_id, amount in drops:
                await self.parent_view.bot.db.add_item_to_inventory(self.parent_view.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await self.parent_view.bot.db.get_collection(self.parent_view.user_id, item_id)
                await self.parent_view.bot.db.add_collection(self.parent_view.user_id, item_id, current_collection + amount)

            pet_drop = await self.parent_view.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await self.parent_view.bot.db.add_player_pet(self.parent_view.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = self.parent_view.coins_reward
            xp = self.parent_view.xp_reward
            
            drop_xp = await CombatSystem._calculate_drop_xp(self.parent_view.bot.db, [{'item_id': item_id, 'amount': amount} for item_id, amount in drops])
            xp += drop_xp
            
            xp_multiplier = await self.parent_view.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await self.parent_view.event_effects.get_coin_multiplier()
            magic_find_bonus = await self.parent_view.event_effects.get_magic_find_bonus()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {self.parent_view.mob_name}!"
            if combat_level > 0:
                combat_drop_multiplier = 1.0 + (combat_level * 0.05)
                embed.description += f"\n⚔️ **Combat Level {combat_level}** - {skill_multiplier:.2f}x damage, {combat_drop_multiplier:.2f}x drops"

            if items_obtained:
                items_text = "\n".join(items_obtained[:15])

                if len(items_text) > 1000:
                    items_text = "\n".join(items_obtained[:10])
                if len(items_obtained) > 15:
                    items_text += f"\n...and {len(items_obtained) - 15} more items"
                embed.add_field(name="🎁 Items Dropped", value=items_text, inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Combat XP"
            if xp_multiplier > 1.0 or coin_multiplier > 1.0:
                reward_text += "\n🎪 Event bonuses active!"
            embed.add_field(name="💰 Reward", value=reward_text, inline=False)
            
            await self.parent_view.bot.player_manager.add_coins(self.parent_view.user_id, coins)
            
            skills = await self.parent_view.bot.db.get_skills(self.parent_view.user_id)
            combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
            new_level = combat_skill['level'] if combat_skill else 0
            if combat_skill:
                new_xp = combat_skill['xp'] + xp
                new_level = await self.parent_view.bot.game_data.calculate_level_from_xp('combat', new_xp)
                await self.parent_view.bot.db.update_skill(self.parent_view.user_id, 'combat', xp=new_xp, level=new_level)
            
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.parent_view.bot.db, self.parent_view.user_id, 'skill', skill_name='combat', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.parent_view.bot.db, self.parent_view.user_id, 'skill_50')
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_skill_achievements(self.parent_view.bot.db, interaction, self.parent_view.user_id, 'combat', new_level)
            
            stats = await self.parent_view.bot.db.get_player_stats(self.parent_view.user_id)
            if stats:
                total_kills = stats.get('kills', 0) + 1
                await self.parent_view.bot.db.update_player_stats(self.parent_view.user_id, kills=total_kills)
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_combat_achievements(self.parent_view.bot.db, interaction, self.parent_view.user_id, kills=total_kills)
            
            self.parent_view.stop()
            for child in self.parent_view.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            return
        
        mob_damage = random.randint(self.parent_view.mob_damage - 5, self.parent_view.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            self.parent_view.player_stats['defense'], 
            self.parent_view.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction))
        mob_damage = max(1, mob_damage)
        self.parent_view.player_health = (self.parent_view.player_health or 0) - mob_damage
        
        if self.parent_view.player_health <= 0:
            embed.description = f"💀 You were defeated by the {self.parent_view.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.parent_view.bot.player_manager.remove_coins(self.parent_view.user_id, 500)
            
            mob_id = normalize_item_id(self.parent_view.mob_name)
            await self.parent_view.bot.db.bestiary.add_bestiary_death(self.parent_view.user_id, mob_id)
            
            from utils.systems.badge_system import BadgeSystem
            player = await self.parent_view.bot.db.get_player(self.parent_view.user_id)
            
            stats = await self.parent_view.bot.db.get_player_stats(self.parent_view.user_id)
            if stats:
                total_deaths = stats.get('deaths', 0) + 1
                await self.parent_view.bot.db.update_player_stats(self.parent_view.user_id, deaths=total_deaths)
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_death_achievements(self.parent_view.bot.db, interaction, self.parent_view.user_id, total_deaths)
            if player:
                death_count = player.get('deaths', 0) + 1
                await self.parent_view.bot.db.update_player(self.parent_view.user_id, deaths=death_count)
                await BadgeSystem.check_and_unlock_badges(self.parent_view.bot.db, self.parent_view.user_id, 'death', death_count=death_count)
            
            self.parent_view.stop()
            for child in self.parent_view.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            return
        
        hit_text = f"💥 **CRITICAL HIT!** You dealt {total_damage} damage!" if crit else f"⚔️ You dealt {total_damage} damage!"
        if ferocity_hits > 1:
            hit_text += f" ({ferocity_hits}x hits from Ferocity!)"
        if combat_level > 0:
            hit_text += f"\n⚔️ Combat Level {combat_level} ({skill_multiplier:.2f}x damage bonus)"
        embed.description = f"{hit_text}\n🩸 The {self.parent_view.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = self.parent_view._create_health_bar(self.parent_view.mob_health, self.parent_view.mob_max_health)
        player_hp_bar = self.parent_view._create_health_bar(self.parent_view.player_health or 0, self.parent_view.player_max_health or 100)
        
        current_mana = self.parent_view.current_mana if self.parent_view.current_mana is not None else 0
        max_mana = self.parent_view.max_mana if self.parent_view.max_mana is not None else 0
        mana_bar = self.parent_view._create_health_bar(current_mana, max_mana) if max_mana > 0 else "[No Mana]"
        
        embed.add_field(name=f"{self.parent_view.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.parent_view.mob_health}/{self.parent_view.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.parent_view.player_health or 0}/{self.parent_view.player_max_health or 0} HP", inline=False)
        embed.add_field(name="Your Mana", value=f"{mana_bar}\n✨ {current_mana}/{max_mana}", inline=False)
        
        await interaction.edit_original_response(embed=embed, view=self.parent_view)

class CombatDefendButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🛡️ Defend", style=discord.ButtonStyle.blurple, custom_id="combat_defend")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()
        
        if self.parent_view.player_stats is None:
            self.parent_view.player_stats = await StatCalculator.calculate_player_stats(self.parent_view.bot.db, self.parent_view.bot.game_data, self.parent_view.user_id)
        
        if self.parent_view.player_health is None:
            self.parent_view.player_health = int(self.parent_view.player_stats['max_health'])
            self.parent_view.player_max_health = int(self.parent_view.player_stats['max_health'])
            
        self.parent_view.player_health = await CombatSystem.apply_health_regeneration(
            self.parent_view.bot.db, self.parent_view.user_id, int(self.parent_view.player_health), int(self.parent_view.player_max_health)
        )
        
        mob_damage = random.randint(self.parent_view.mob_damage - 5, self.parent_view.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            self.parent_view.player_stats['defense'], 
            self.parent_view.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction) * 0.5)
        mob_damage = max(1, mob_damage)
        self.parent_view.player_health = (self.parent_view.player_health or 0) - mob_damage
        
        embed = discord.Embed(title=f"⚔️ Fighting {self.parent_view.mob_name}", color=discord.Color.blue())
        embed.description = f"🛡️ You defended! The {self.parent_view.mob_name} dealt only {mob_damage} damage!"
        
        if self.parent_view.player_health <= 0:
            embed.description = f"💀 You were defeated by the {self.parent_view.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.parent_view.bot.player_manager.remove_coins(self.parent_view.user_id, 500)   
            
            self.parent_view.stop()
            for child in self.parent_view.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            return
        
        mob_hp_bar = self.parent_view._create_health_bar(self.parent_view.mob_health, self.parent_view.mob_max_health)
        player_hp_bar = self.parent_view._create_health_bar(self.parent_view.player_health or 0, self.parent_view.player_max_health or 100)
        
        current_mana = self.parent_view.current_mana if self.parent_view.current_mana is not None else 0
        max_mana = self.parent_view.max_mana if self.parent_view.max_mana is not None else 0
        mana_bar = self.parent_view._create_health_bar(current_mana, max_mana) if max_mana > 0 else "[No Mana]"
        
        embed.add_field(name=f"{self.parent_view.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.parent_view.mob_health}/{self.parent_view.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.parent_view.player_health or 0}/{self.parent_view.player_max_health or 0} HP", inline=False)
        embed.add_field(name="Your Mana", value=f"{mana_bar}\n✨ {current_mana}/{max_mana}", inline=False)
        
        await interaction.edit_original_response(embed=embed, view=self.parent_view)

class CombatAbilityButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="✨ Use Ability", style=discord.ButtonStyle.green, custom_id="combat_ability")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()
        
        if self.parent_view.player_stats is None:
            self.parent_view.player_stats = await StatCalculator.calculate_player_stats(self.parent_view.bot.db, self.parent_view.bot.game_data, self.parent_view.user_id)
        
        if self.parent_view.player_health is None:
            self.parent_view.player_health = int(self.parent_view.player_stats['max_health'])
            self.parent_view.player_max_health = int(self.parent_view.player_stats['max_health'])
        
        if not hasattr(self.parent_view, 'current_mana'):
            self.parent_view.current_mana = self.parent_view.player_stats.get('max_mana', 100)
            self.parent_view.max_mana = self.parent_view.player_stats.get('max_mana', 100)
            
        self.parent_view.player_health = await CombatSystem.apply_health_regeneration(
            self.parent_view.bot.db, self.parent_view.user_id, int(self.parent_view.player_health), int(self.parent_view.player_max_health)
        )
        
        weapon_info = await CombatSystem.get_equipped_weapon_info(self.parent_view.bot.db, self.parent_view.user_id)
        
        from utils.systems.weapon_abilities import WeaponAbilities
        
        ability_damage = 0
        mana_cost = 50
        ability_name = "Generic Ability"
        
        if weapon_info:
            weapon_id = weapon_info['item_id']
            has_weapon_ability = await WeaponAbilities.has_ability(self.parent_view.bot.db, weapon_id)
            
            if has_weapon_ability:
                ability = await WeaponAbilities.get_ability(self.parent_view.bot.db, weapon_id)
                if ability:
                    ability_name = ability.get('ability_name', 'Weapon Ability')
                    mana_cost = ability.get('mana_cost', 50)
                    
                    weapon_damage, _ = await CombatSystem._get_equipped_weapon_damage_and_tier(self.parent_view.bot.db, self.parent_view.user_id)
                    full_stats = await StatCalculator.calculate_full_stats(self.parent_view.bot.db, self.parent_view.user_id)
                    full_stats['user_id'] = self.parent_view.user_id
                    ability_damage = int(await WeaponAbilities.calculate_ability_damage(
                        self.parent_view.bot.db, weapon_id, full_stats, weapon_damage
                    ))
        
        if ability_damage == 0:
            combat_effects = StatCalculator.apply_combat_effects(self.parent_view.player_stats, None)
            ability_multiplier = 3 + (self.parent_view.player_stats.get('ability_damage', 0) / 100)
            ability_damage = int(combat_effects['base_damage'] * ability_multiplier)
        
        if not await CombatSystem.can_use_ability(self.parent_view.current_mana, mana_cost):
            await interaction.followup.send(f"❌ Not enough mana! Need {mana_cost}, have {self.parent_view.current_mana}", ephemeral=True)
            return
        
        self.parent_view.current_mana = await CombatSystem.consume_mana(self.parent_view.current_mana, mana_cost)
        
        self.parent_view.mob_health -= ability_damage
        
        embed = discord.Embed(title=f"⚔️ Fighting {self.parent_view.mob_name}", color=discord.Color.purple())
        
        if self.parent_view.mob_health <= 0:
            mob_id = normalize_item_id(self.parent_view.mob_name)
            loot_table = await self.parent_view.bot.game_data.get_loot_table(self.parent_view.mob_name, 'mob')
            
            if not loot_table:
                loot_table = {}
            
            if 'coins' not in loot_table:
                loot_table['coins'] = (self.parent_view.coins_reward // 2, self.parent_view.coins_reward)
            if 'xp' not in loot_table:
                loot_table['xp'] = self.parent_view.xp_reward
            
            magic_find = self.parent_view.player_stats.get('magic_find', 0)
            fortune = self.parent_view.player_stats.get('looting', 0)
            drops = await CombatSystem.roll_combat_loot(
                self.parent_view.bot.game_data, 
                self.parent_view.bot.db, 
                self.parent_view.user_id, 
                loot_table, 
                magic_find, 
                fortune
            )
            
            items_obtained = []
            for item_id, amount in drops:
                await self.parent_view.bot.db.add_item_to_inventory(self.parent_view.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await self.parent_view.bot.db.get_collection(self.parent_view.user_id, item_id)
                await self.parent_view.bot.db.add_collection(self.parent_view.user_id, item_id, current_collection + amount)
            
            pet_drop = await self.parent_view.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await self.parent_view.bot.db.add_player_pet(self.parent_view.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = self.parent_view.coins_reward
            xp = self.parent_view.xp_reward
            
            drop_xp = await CombatSystem._calculate_drop_xp(self.parent_view.bot.db, [{'item_id': item_id, 'amount': amount} for item_id, amount in drops])
            xp += drop_xp
            
            xp_multiplier = await self.parent_view.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await self.parent_view.event_effects.get_coin_multiplier()
            magic_find_bonus = await self.parent_view.event_effects.get_magic_find_bonus()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {self.parent_view.mob_name} with **{ability_name}**!"

            if items_obtained:
                items_text = "\n".join(items_obtained[:15])
                if len(items_text) > 1000:
                    items_text = "\n".join(items_obtained[:10])
                if len(items_obtained) > 15:
                    items_text += f"\n...and {len(items_obtained) - 15} more items"
                embed.add_field(name="🎁 Items Dropped", value=items_text, inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Combat XP"
            if xp_multiplier > 1.0 or coin_multiplier > 1.0:
                reward_text += "\n🎪 Event bonuses active!"
            embed.add_field(name="💰 Reward", value=reward_text, inline=False)
            
            bestiary_info = await self.parent_view.bot.db.bestiary.add_bestiary_kill(self.parent_view.user_id, mob_id)
            if bestiary_info and bestiary_info.get('leveled_up'):
                bestiary_text = f"📚 Bestiary: {bestiary_info['kills']} kills (Lv {bestiary_info['new_level']})"
                if bestiary_info['new_level'] > bestiary_info['old_level']:
                    bestiary_text += f"\n🎉 **LEVEL UP!** {bestiary_info['old_level']} → {bestiary_info['new_level']}"
                embed.add_field(name="📖 Bestiary Progress", value=bestiary_text, inline=False)
            
            await self.parent_view.bot.player_manager.add_coins(self.parent_view.user_id, coins)
                
            skills = await self.parent_view.bot.db.get_skills(self.parent_view.user_id)
            combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
            new_level = combat_skill['level'] if combat_skill else 0
            if combat_skill:
                new_xp = combat_skill['xp'] + xp
                new_level = await self.parent_view.bot.game_data.calculate_level_from_xp('combat', new_xp)
                await self.parent_view.bot.db.update_skill(self.parent_view.user_id, 'combat', xp=new_xp, level=new_level)
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_skill_achievements(self.parent_view.bot.db, interaction, self.parent_view.user_id, 'combat', new_level)
            
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.parent_view.bot.db, self.parent_view.user_id, 'skill', skill_name='combat', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.parent_view.bot.db, self.parent_view.user_id, 'skill_50')
            
            self.parent_view.stop()
            for child in self.parent_view.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            return
        
        mob_damage = random.randint(self.parent_view.mob_damage - 5, self.parent_view.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            self.parent_view.player_stats['defense'], 
            self.parent_view.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction))
        mob_damage = max(1, mob_damage)
        self.parent_view.player_health = (self.parent_view.player_health or 0) - mob_damage
        
        if self.parent_view.player_health <= 0:
            mob_id = normalize_item_id(self.parent_view.mob_name)
            await self.parent_view.bot.db.bestiary.add_bestiary_death(self.parent_view.user_id, mob_id)
            
            embed.description = f"💀 You were defeated by the {self.parent_view.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.parent_view.bot.player_manager.remove_coins(self.parent_view.user_id, 500)   
            
            self.parent_view.stop()
            for child in self.parent_view.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            return
        
        embed.description = f"✨ **{ability_name}** dealt {ability_damage} damage! (-{mana_cost} mana)\n🩸 The {self.parent_view.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = self.parent_view._create_health_bar(self.parent_view.mob_health, self.parent_view.mob_max_health)
        player_hp_bar = self.parent_view._create_health_bar(self.parent_view.player_health or 0, self.parent_view.player_max_health or 100)
        
        current_mana = self.parent_view.current_mana if self.parent_view.current_mana is not None else 0
        max_mana = self.parent_view.max_mana if self.parent_view.max_mana is not None else 0
        mana_bar = self.parent_view._create_health_bar(current_mana, max_mana) if max_mana > 0 else "[No Mana]"
        
        embed.add_field(name=f"{self.parent_view.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.parent_view.mob_health}/{self.parent_view.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.parent_view.player_health or 0}/{self.parent_view.player_max_health or 0} HP", inline=False)
        embed.add_field(name="Your Mana", value=f"{mana_bar}\n✨ {current_mana}/{max_mana}", inline=False)
        
        await interaction.edit_original_response(embed=embed, view=self.parent_view)

class CombatRunButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏃 Run Away", style=discord.ButtonStyle.gray, custom_id="combat_run")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏃 Fled from Battle",
            description=f"You ran away from the {self.parent_view.mob_name}!",
            color=discord.Color.light_gray()
        )
        self.parent_view.stop()
        for child in self.parent_view.children:
            if isinstance(child, Button):
                child.disabled = True   
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
