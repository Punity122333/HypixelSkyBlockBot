import discord
import random
from discord.ui import Button
from typing import TYPE_CHECKING
from utils.systems.combat_system import CombatSystem
from utils.stat_calculator import StatCalculator
from utils.event_effects import EventEffects
from utils.compat import roll_loot as compat_roll_loot

if TYPE_CHECKING:
    from discord import Interaction

class SlayerCombatAttackButton(Button):
    def __init__(self, view):
        super().__init__(label="⚔️ Attack", style=discord.ButtonStyle.red, custom_id="slayer_attack")
        self.parent_view = view
    
    async def callback(self, interaction: "Interaction"):
        view = self.parent_view
        if view.player_stats is None:
            view.player_stats = await StatCalculator.calculate_player_stats(view.bot.db, view.bot.game_data, view.user_id)
        
        if view.player_health is None:
            view.player_health = int(view.player_stats['max_health'])
            view.player_max_health = int(view.player_stats['max_health'])
        
        mob_id = view.mob_name.lower().split()[0]
        mob_stats = await view.bot.db.get_mob_stats(mob_id)
        mob_defense = mob_stats.get('defense', 0) if mob_stats else 0
        
        damage_result = await CombatSystem.calculate_player_damage(view.bot.db, view.user_id, mob_defense)
        
        total_damage = int(damage_result['damage'])
        crit = damage_result['is_crit']
        
        ferocity_hits = 1 + (view.player_stats.get('ferocity', 0) // 100)
        total_damage = int(total_damage * ferocity_hits)
        view.mob_health -= total_damage
        
        embed = discord.Embed(title=f"⚔️ Slayer Boss Fight: {view.mob_name}", color=discord.Color.dark_red())
        
        if view.mob_health <= 0:
            slayer_id = view.mob_name.lower().split()[0]
            await view.bot.db.skills.update_slayer_xp(view.user_id, slayer_id, view.xp_reward)

            magic_find = view.player_stats.get('magic_find', 0)
            fortune = view.player_stats.get('looting', 0)
            drops = await compat_roll_loot(view.bot.game_data, view.loot_table, magic_find, fortune)
            
            items_obtained = []
            for item_id, amount in drops:
                await view.bot.db.add_item_to_inventory(view.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await view.bot.db.get_collection(view.user_id, item_id)
                await view.bot.db.add_collection(view.user_id, item_id, current_collection + amount)
            
            mob_id = view.mob_name.lower().replace(' ', '_')
            pet_drop = await view.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await view.bot.db.add_player_pet(view.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = view.coins_reward
            xp = view.xp_reward
            
            xp_multiplier = await view.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await view.event_effects.get_coin_multiplier()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {view.mob_name}!"
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained[:10]), inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Slayer XP"
            if xp_multiplier > 1.0 or coin_multiplier > 1.0:
                reward_text += "\n🎪 Event bonuses active!"
            embed.add_field(name="💰 Reward", value=reward_text, inline=False)
            
            await view.bot.player_manager.add_coins(view.user_id, coins)
            
            view.fight_in_progress = False
            view.stop()
            for child in view.children:
                if isinstance(child, Button):
                    child.disabled = True
            await interaction.response.edit_message(embed=embed, view=view)
            return
        
        mob_damage = random.randint(view.mob_damage - 5, view.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            view.player_stats['defense'], 
            view.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction))
        mob_damage = max(1, mob_damage)
        view.player_health = (view.player_health or 0) - mob_damage
        
        if view.player_health <= 0:
            embed.description = f"💀 You were defeated by the {view.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await view.bot.player_manager.remove_coins(view.user_id, 500)
            
            view.fight_in_progress = False
            view.stop()
            for child in view.children:
                if isinstance(child, Button):
                    child.disabled = True
            await interaction.response.edit_message(embed=embed, view=view)
            return
        
        hit_text = f"💥 **CRITICAL HIT!** You dealt {total_damage} damage!" if crit else f"⚔️ You dealt {total_damage} damage!"
        if ferocity_hits > 1:
            hit_text += f" ({ferocity_hits}x hits from Ferocity!)"
        embed.description = f"{hit_text}\n🩸 The {view.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = view._create_health_bar(view.mob_health, view.mob_max_health)
        player_hp_bar = view._create_health_bar(view.player_health or 0, view.player_max_health or 100)
        
        embed.add_field(name=f"{view.mob_name}", value=f"{mob_hp_bar}\n❤️ {view.mob_health}/{view.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {view.player_health or 0}/{view.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)

class SlayerCombatDefendButton(Button):
    def __init__(self, view):
        super().__init__(label="🛡️ Defend", style=discord.ButtonStyle.blurple, custom_id="slayer_defend")
        self.parent_view = view
    
    async def callback(self, interaction: "Interaction"):
        view = self.parent_view
        if view.player_stats is None:
            view.player_stats = await StatCalculator.calculate_player_stats(view.bot.db, view.bot.game_data, view.user_id)
        
        if view.player_health is None:
            view.player_health = int(view.player_stats['max_health'])
            view.player_max_health = int(view.player_stats['max_health'])
        
        mob_damage = random.randint(view.mob_damage - 5, view.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            view.player_stats['defense'], 
            view.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction) * 0.5)
        mob_damage = max(1, mob_damage)
        view.player_health = (view.player_health or 0) - mob_damage
        
        embed = discord.Embed(title=f"⚔️ Slayer Boss Fight: {view.mob_name}", color=discord.Color.blue())
        embed.description = f"🛡️ You defended! The {view.mob_name} dealt only {mob_damage} damage!"
        
        if view.player_health <= 0:
            embed.description = f"💀 You were defeated by the {view.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await view.bot.player_manager.remove_coins(view.user_id, 500)
            
            view.fight_in_progress = False
            view.stop()
            for child in view.children:
                if isinstance(child, Button):
                    child.disabled = True
            await interaction.response.edit_message(embed=embed, view=view)
            return
        
        mob_hp_bar = view._create_health_bar(view.mob_health, view.mob_max_health)
        player_hp_bar = view._create_health_bar(view.player_health or 0, view.player_max_health or 100)
        
        embed.add_field(name=f"{view.mob_name}", value=f"{mob_hp_bar}\n❤️ {view.mob_health}/{view.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {view.player_health or 0}/{view.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)

class SlayerCombatAbilityButton(Button):
    def __init__(self, view):
        super().__init__(label="✨ Use Ability", style=discord.ButtonStyle.green, custom_id="slayer_ability")
        self.parent_view = view
    
    async def callback(self, interaction: "Interaction"):
        view = self.parent_view
        if view.player_stats is None:
            view.player_stats = await StatCalculator.calculate_player_stats(view.bot.db, view.bot.game_data, view.user_id)
        
        if view.player_health is None:
            view.player_health = int(view.player_stats['max_health'])
            view.player_max_health = int(view.player_stats['max_health'])
        
        mana_cost = 50
        current_mana = view.player_stats.get('mana', view.player_stats['max_mana'])
        if current_mana < mana_cost:
            await interaction.response.send_message("❌ Not enough mana!", ephemeral=True)
            return
        
        combat_effects = StatCalculator.apply_combat_effects(view.player_stats, None)
        ability_multiplier = 3 + (view.player_stats.get('ability_damage', 0) / 100)
        ability_damage = int(combat_effects['base_damage'] * ability_multiplier)
        view.mob_health -= ability_damage
        
        await view.bot.db.update_player(view.user_id, mana=current_mana - mana_cost)
        
        embed = discord.Embed(title=f"⚔️ Slayer Boss Fight: {view.mob_name}", color=discord.Color.purple())
        
        if view.mob_health <= 0:
            slayer_id = view.mob_name.lower().split()[0]
            await view.bot.db.skills.update_slayer_xp(view.user_id, slayer_id, view.xp_reward)

            magic_find = view.player_stats.get('magic_find', 0)
            fortune = view.player_stats.get('looting', 0)
            drops = await compat_roll_loot(view.bot.game_data, view.loot_table, magic_find, fortune)
            
            items_obtained = []
            for item_id, amount in drops:
                await view.bot.db.add_item_to_inventory(view.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await view.bot.db.get_collection(view.user_id, item_id)
                await view.bot.db.add_collection(view.user_id, item_id, current_collection + amount)
            
            mob_id = view.mob_name.lower().replace(' ', '_')
            pet_drop = await view.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await view.bot.db.add_player_pet(view.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = view.coins_reward
            xp = view.xp_reward
            
            xp_multiplier = await view.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await view.event_effects.get_coin_multiplier()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {view.mob_name} with your ability!"
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained[:10]), inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Slayer XP"
            if xp_multiplier > 1.0 or coin_multiplier > 1.0:
                reward_text += "\n🎪 Event bonuses active!"
            embed.add_field(name="💰 Reward", value=reward_text, inline=False)
            
            await view.bot.player_manager.add_coins(view.user_id, coins)
            
            view.fight_in_progress = False
            view.stop()
            for child in view.children:
                if isinstance(child, Button):
                    child.disabled = True
            await interaction.response.edit_message(embed=embed, view=view)
            return
        
        mob_damage = random.randint(view.mob_damage - 5, view.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            view.player_stats['defense'], 
            view.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction))
        mob_damage = max(1, mob_damage)
        view.player_health = (view.player_health or 0) - mob_damage
        
        if view.player_health <= 0:
            embed.description = f"💀 You were defeated by the {view.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await view.bot.player_manager.remove_coins(view.user_id, 500)
            
            view.fight_in_progress = False
            view.stop()
            for child in view.children:
                if isinstance(child, Button):
                    child.disabled = True
            await interaction.response.edit_message(embed=embed, view=view)
            return
        
        embed.description = f"✨ Your ability dealt {ability_damage} damage! (-{mana_cost} mana)\n🩸 The {view.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = view._create_health_bar(view.mob_health, view.mob_max_health)
        player_hp_bar = view._create_health_bar(view.player_health or 0, view.player_max_health or 100)
        
        embed.add_field(name=f"{view.mob_name}", value=f"{mob_hp_bar}\n❤️ {view.mob_health}/{view.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {view.player_health or 0}/{view.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)

class SlayerCombatRunButton(Button):
    def __init__(self, view):
        super().__init__(label="🏃 Run Away", style=discord.ButtonStyle.gray, custom_id="slayer_run")
        self.parent_view = view
    
    async def callback(self, interaction: "Interaction"):
        view = self.parent_view
        embed = discord.Embed(
            title="🏃 Fled from Battle",
            description=f"You ran away from the {view.mob_name}!",
            color=discord.Color.light_gray()
        )
        view.fight_in_progress = False
        view.stop()
        for child in view.children:
            if isinstance(child, Button):
                child.disabled = True
        await interaction.response.edit_message(embed=embed, view=view)
