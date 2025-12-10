import random
from typing import Optional, TYPE_CHECKING
import discord
from discord.ui import View, Button
from utils.stat_calculator import StatCalculator
from utils.systems.combat_system import CombatSystem
from utils.compat import roll_loot as compat_roll_loot
from utils.event_effects import EventEffects
from utils.normalize import normalize_item_id
from components.buttons.combat_buttons import (
    CombatAttackButton,
    CombatDefendButton,
    CombatAbilityButton,
    CombatRunButton
)

if TYPE_CHECKING:
    from main import SkyblockBot

class CombatView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, mob_name: str, mob_health: int, mob_damage: int, coins_reward: int, xp_reward: int):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.mob_name = mob_name
        self.mob_health = mob_health
        self.mob_max_health = mob_health
        self.mob_damage = mob_damage
        self.coins_reward = coins_reward
        self.xp_reward = xp_reward
        self.player_health: Optional[int] = None
        self.player_max_health: Optional[int] = None
        self.player_damage: int = 50
        self.player_stats: Optional[dict] = None
        self.message: Optional[discord.Message] = None
        self.event_effects = EventEffects(bot)
        
        self.add_item(CombatAttackButton(self))
        self.add_item(CombatDefendButton(self))
        self.add_item(CombatAbilityButton(self))
        self.add_item(CombatRunButton(self))
    
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