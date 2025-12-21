import discord
from typing import TYPE_CHECKING, Dict, Any, Optional
from discord.ui import View, Button
from utils.event_effects import EventEffects
from components.buttons.slayer_combat_buttons import (
    SlayerCombatAttackButton,
    SlayerCombatDefendButton,
    SlayerCombatAbilityButton,
    SlayerCombatRunButton
)
from components.buttons.use_potion_button import UsePotionButton

if TYPE_CHECKING:
    from main import SkyblockBot
    from discord import Interaction, Message

class SlayerCombatView(View):
    def __init__(
        self,
        bot: "SkyblockBot",
        user_id: int,
        mob_name: str,
        mob_health: int,
        mob_damage: int,
        coins_reward: int,
        xp_reward: int,
        loot_table: Dict[str, Any],
    ):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.mob_name = mob_name
        self.mob_health = mob_health
        self.mob_max_health = mob_health
        self.mob_damage = mob_damage
        self.coins_reward = coins_reward
        self.xp_reward = xp_reward
        self.loot_table = loot_table
        
        self.player_health: Optional[int] = None
        self.player_max_health: Optional[int] = None
        self.player_stats: Optional[Dict[str, Any]] = None
        self.message: Optional["Message"] = None
        self.event_effects = EventEffects(bot)
        self.fight_in_progress = True
        
        self.add_item(SlayerCombatAttackButton(self))
        self.add_item(SlayerCombatDefendButton(self))
        self.add_item(SlayerCombatAbilityButton(self))
        self.add_item(SlayerCombatRunButton(self))
        self.add_item(UsePotionButton(self))
    
    async def interaction_check(self, interaction: "Interaction") -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your slayer fight!", ephemeral=True)
            return False
        return self.fight_in_progress

    def _create_health_bar(self, current: int, maximum: int) -> str:
        percentage = current / maximum if maximum > 0 else 0
        filled = int(percentage * 20)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}]"
        
    async def on_timeout(self):
        if self.fight_in_progress and self.message:
            self.fight_in_progress = False
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            
            embed = discord.Embed(
                title="⌛ Fight Timed Out",
                description=f"The fight against the {self.mob_name} ended due to inactivity. You gain no rewards.",
                color=discord.Color.red()
            )
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass