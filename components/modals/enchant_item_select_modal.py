import discord
from utils.event_effects import EventEffects
from utils.systems.achievement_system import AchievementSystem

class EnchantItemSelectModal(discord.ui.Modal, title="Choose Item"):
    item_number = discord.ui.TextInput(
        label="Item Number",
        placeholder="Enter the number of the item you want to enchant",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, items, enchantment, level, enchant_data, cost, xp_gained):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.items = items
        self.enchantment = enchantment
        self.level = level
        self.enchant_data = enchant_data
        self.cost = cost
        self.xp_gained = xp_gained
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            idx = int(self.item_number.value) - 1
            if idx < 0 or idx >= len(self.items):
                await interaction.response.send_message(
                    f"❌ Invalid item number! Please choose between 1 and {len(self.items)}.",
                    ephemeral=True
                )
                return
            
            item = self.items[idx]
            inventory_item_id = item['id']
            
            # Apply the enchantment
            await self.bot.db.add_enchantment_to_item(inventory_item_id, self.enchantment, self.level)
            
            # Award XP
            event_effects = EventEffects(self.bot)
            xp_multiplier = await event_effects.get_xp_multiplier('enchanting')
            final_xp = int(self.xp_gained * xp_multiplier)
            
            skills = await self.bot.db.get_skills(self.user_id)
            enchanting_skill = next((s for s in skills if s['skill_name'] == 'enchanting'), None)
            new_level = enchanting_skill['level'] if enchanting_skill else 0
            
            if enchanting_skill:
                new_xp = enchanting_skill['xp'] + final_xp
                new_level = await self.bot.game_data.calculate_level_from_xp('enchanting', new_xp)
                await self.bot.db.update_skill(self.user_id, 'enchanting', xp=new_xp, level=new_level)

            await AchievementSystem.check_skill_achievements(
                self.bot.db, interaction, self.user_id, 'enchanting', new_level
            )
            
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, self.user_id, 'skill', skill_name='enchanting', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.bot.db, self.user_id, 'skill_50')

            progression = await self.bot.db.get_player_progression(self.user_id)
            if not progression or not progression.get('first_enchant_date'):
                import time
                await self.bot.db.update_progression(
                    self.user_id,
                    first_enchant_date=int(time.time())
                )
                await AchievementSystem.unlock_single_achievement(
                    self.bot.db, interaction, self.user_id, 'first_enchant'
                )

            stats = await self.bot.db.get_player_stats(self.user_id)
            if stats:
                total_enchants = stats.get('total_enchants', 0) + 1
                await self.bot.db.update_player_stats(self.user_id, total_enchants=total_enchants)

                from utils.achievement_tracker import AchievementTracker
                enchant_achievements = await AchievementTracker.check_value_based_achievements(
                    self.bot.db, self.user_id, 'enchants', total_enchants
                )
                await AchievementSystem.check_and_notify(
                    self.bot.db, interaction, self.user_id, enchant_achievements
                )

            if self.level >= self.enchant_data['max_level']:
                await AchievementSystem.unlock_single_achievement(
                    self.bot.db, interaction, self.user_id, 'enchant_max'
                )
            
            embed = discord.Embed(
                title="✨ Enchanted!",
                description=f"Applied {self.enchant_data['name']} {self.level} to {item['name']}!",
                color=discord.Color.purple()
            )
            embed.add_field(name="Cost", value=f"{self.cost:,} coins", inline=True)
            embed.add_field(name="Effect", value=self.enchant_data['description'], inline=True)
            embed.add_field(name="XP Gained", value=f"+{final_xp} Enchanting XP", inline=True)
            
            if xp_multiplier > 1.0:
                event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n{event_text}"
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number!",
                ephemeral=True
            )
