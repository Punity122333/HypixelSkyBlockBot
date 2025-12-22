import random
from typing import Optional, TYPE_CHECKING
import discord
from discord.ui import View, Button
from utils.stat_calculator import StatCalculator
from utils.systems.combat_system import CombatSystem
from utils.event_effects import EventEffects
from utils.normalize import normalize_item_id
from components.buttons.combat_buttons import (
    CombatAttackButton,
    CombatDefendButton,
    CombatAbilityButton,
    CombatRunButton
)
from components.buttons.use_potion_button import UsePotionButton

if TYPE_CHECKING:
    from main import SkyblockBot

class SeaCreatureCombatView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, creature_name: str, creature_health: int, creature_damage: int, coins_reward: int, xp_reward: int):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.mob_name = creature_name
        self.mob_health = creature_health
        self.mob_max_health = creature_health
        self.mob_damage = creature_damage
        self.coins_reward = coins_reward
        self.xp_reward = xp_reward
        self.player_health: Optional[int] = None
        self.player_max_health: Optional[int] = None
        self.current_mana: Optional[int] = None
        self.max_mana: Optional[int] = None
        self.player_damage: int = 50
        self.player_stats: Optional[dict] = None
        self.message: Optional[discord.Message] = None
        self.event_effects = EventEffects(bot)
        
        self.add_item(CombatAttackButton(self))
        self.add_item(CombatDefendButton(self))
        self.add_item(CombatAbilityButton(self))
        self.add_item(CombatRunButton(self))
        self.add_item(UsePotionButton(self))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your fight!", ephemeral=True)
            return False
        return True
    
    def _create_health_bar(self, current: int, maximum: int) -> str:
        percentage = current / maximum if maximum > 0 else 0
        filled = int(percentage * 20)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}]"
    
    async def _get_player_stats(self):
        if self.player_stats is None:
            self.player_stats = await StatCalculator.calculate_player_stats(
                self.bot.db, 
                self.bot.game_data, 
                self.user_id
            )
        return self.player_stats
    
    async def _initialize_player_health(self):
        if self.player_health is None:
            stats = await self._get_player_stats()
            self.player_max_health = stats.get('max_health', 100)
            self.player_health = self.player_max_health
            self.max_mana = stats.get('intelligence', 0)
            self.current_mana = self.max_mana
    
    async def update_embed(self, interaction: discord.Interaction, action_text: str = ""):
        await self._initialize_player_health()

        player_health = self.player_health if self.player_health is not None else 0
        player_max_health = self.player_max_health if self.player_max_health is not None else 1
        current_mana = self.current_mana if self.current_mana is not None else 0
        max_mana = self.max_mana if self.max_mana is not None else 0

        player_health_bar = self._create_health_bar(player_health, player_max_health)
        mob_health_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        mana_bar = self._create_health_bar(current_mana, max_mana) if max_mana > 0 else "[No Mana]"
        
        embed = discord.Embed(
            title=f"⚔️ Fighting {self.mob_name}!",
            description=action_text,
            color=discord.Color.blue() if self.mob_health > 0 else discord.Color.green()
        )
        
        embed.add_field(
            name=f"Your Health: {player_health}/{player_max_health}",
            value=player_health_bar,
            inline=False
        )
        
        embed.add_field(
            name=f"Your Mana: {current_mana}/{max_mana}",
            value=mana_bar,
            inline=False
        )
        
        embed.add_field(
            name=f"{self.mob_name} Health: {self.mob_health}/{self.mob_max_health}",
            value=mob_health_bar,
            inline=False
        )
        
        if self.mob_health <= 0:
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            
            embed.color = discord.Color.green()
            embed.title = f"🎉 Victory! {self.mob_name} Defeated!"
            embed.add_field(name="Rewards", value=f"💰 {self.coins_reward} coins\n⭐ {self.xp_reward} XP", inline=False)
            
            await self.bot.player_manager.add_coins(self.user_id, self.coins_reward)
            
            skills = await self.bot.db.get_skills(self.user_id)
            combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
            fishing_skill = next((s for s in skills if s['skill_name'] == 'fishing'), None)
            
            combat_level = combat_skill['level'] if combat_skill else 0
            if combat_skill:
                combat_xp = int(self.xp_reward * 0.5)
                new_combat_xp = combat_skill['xp'] + combat_xp
                combat_level = await self.bot.game_data.calculate_level_from_xp('combat', new_combat_xp)
                await self.bot.db.update_skill(self.user_id, 'combat', xp=new_combat_xp, level=combat_level)
            
            fishing_level = fishing_skill['level'] if fishing_skill else 0
            if fishing_skill:
                fishing_xp = int(self.xp_reward * 0.5)
                new_fishing_xp = fishing_skill['xp'] + fishing_xp
                fishing_level = await self.bot.game_data.calculate_level_from_xp('fishing', new_fishing_xp)
                await self.bot.db.update_skill(self.user_id, 'fishing', xp=new_fishing_xp, level=fishing_level)
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_skill_achievements(self.bot.db, interaction, self.user_id, 'combat', combat_level)
            await AchievementSystem.check_skill_achievements(self.bot.db, interaction, self.user_id, 'fishing', fishing_level)
        
        elif player_health <= 0:
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            
            embed.color = discord.Color.red()
            embed.title = "💀 Defeat!"
            embed.description = f"{action_text}\n\nYou have been defeated by the {self.mob_name}!"
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass
