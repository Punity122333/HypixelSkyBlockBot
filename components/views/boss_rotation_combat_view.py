import discord
from typing import TYPE_CHECKING, Dict, Any, Optional
from discord.ui import View, Button
import random
import time
from utils.systems.combat_system import CombatSystem
from utils.stat_calculator import StatCalculator
from utils.event_effects import EventEffects
from utils.compat import roll_loot as compat_roll_loot
from components.buttons.slayer_combat_buttons import (
    SlayerCombatAttackButton,
    SlayerCombatDefendButton,
    SlayerCombatAbilityButton,
    SlayerCombatRunButton
)

if TYPE_CHECKING:
    from main import SkyblockBot
    from discord import Interaction, Message


class BossRotationCombatView(View):
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
        coop_session: Dict[str, Any]
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
        self.coop_session = coop_session
        self.start_time = int(time.time())
        
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
    
    async def interaction_check(self, interaction: "Interaction") -> bool:
        if interaction.user.id not in self.coop_session['member_ids']:
            await interaction.response.send_message("You're not part of this boss fight!", ephemeral=True)
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
    
    async def handle_victory(self, interaction: "Interaction", damage_dealt: int):
        self.fight_in_progress = False
        
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        
        from utils.systems.cooperative_boss_system import CooperativeBossSystem
        
        await CooperativeBossSystem.record_member_damage(
            self.coop_session, interaction.user.id, damage_dealt
        )
        
        rewards = await CooperativeBossSystem.calculate_rewards(
            self.coop_session, self.coins_reward, self.xp_reward
        )
        
        loot_items = []
        for _ in range(random.randint(1, 3)):
            item_id = random.choice(['iron_ingot', 'diamond', 'emerald', 'gold_ingot'])
            amount = random.randint(1, 5)
            loot_items.append((item_id, amount))
        
        member_loot = await CooperativeBossSystem.distribute_loot(
            self.bot.db, self.coop_session, loot_items
        )
        
        await CooperativeBossSystem.complete_boss_session(
            self.bot.db, self.coop_session, rewards
        )
        
        time_taken = int(time.time()) - self.start_time
        await self.bot.db.boss_rotation.record_boss_kill(
            interaction.user.id,
            self.coop_session['boss_id'],
            damage_dealt,
            time_taken
        )
        
        mvp_id = CooperativeBossSystem.get_mvp(self.coop_session)
        
        embed = discord.Embed(
            title=f"🎉 {self.mob_name} Defeated!",
            description=f"Victory! The {self.mob_name} has been defeated!",
            color=discord.Color.green()
        )
        
        if len(self.coop_session['member_ids']) > 1:
            embed.add_field(
                name="👥 Party Victory!",
                value=f"MVP: <@{mvp_id}> ({self.coop_session['member_damage'][mvp_id]:,} damage)",
                inline=False
            )
            
            rewards_text = ""
            for member_id, reward_data in rewards.items():
                contribution_pct = int(reward_data['contribution'] * 100)
                rewards_text += f"<@{member_id}>: {reward_data['coins']:,} coins ({contribution_pct}%)\n"
            
            embed.add_field(name="💰 Rewards Distribution", value=rewards_text, inline=False)
            
            loot_text = ""
            for member_id, items in member_loot.items():
                if items:
                    item_str = ", ".join([f"{amt}x {iid}" for iid, amt in items])
                    loot_text += f"<@{member_id}>: {item_str}\n"
            
            if loot_text:
                embed.add_field(name="🎁 Loot Distribution", value=loot_text, inline=False)
        else:
            reward = rewards[interaction.user.id]
            embed.add_field(
                name="💰 Rewards",
                value=f"+{reward['coins']:,} coins\n+{reward['xp']:,} Combat XP",
                inline=True
            )
            
            if member_loot.get(interaction.user.id):
                loot_str = ", ".join([f"{amt}x {iid}" for iid, amt in member_loot[interaction.user.id]])
                embed.add_field(name="🎁 Loot", value=loot_str, inline=True)
        
        embed.add_field(name="⏱️ Time Taken", value=f"{time_taken}s", inline=True)
        embed.set_footer(text="Congratulations on your victory!")
        
        if self.message:
            await interaction.followup.edit_message(self.message.id, embed=embed, view=self)
        else:
            await interaction.followup.send(embed=embed, view=self)
