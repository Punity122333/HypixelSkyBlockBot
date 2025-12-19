import discord
from discord.ext import commands
from discord import app_commands
from utils.event_effects import EventEffects
from utils.autocomplete import item_autocomplete
from utils.systems.achievement_system import AchievementSystem

class EnchantingAdvanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_effects = EventEffects(bot)

    @app_commands.command(name="enchant", description="Enchant an item")
    @app_commands.describe(
        item="Item to enchant",
        slot="Inventory slot of the item to enchant",
        enchantment="Enchantment to apply",
        level="Enchantment level"
    )
    async def enchant(self, interaction: discord.Interaction, item: str, slot: int, enchantment: str, level: int):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        enchant_data = await self.bot.game_data.get_enchantment(enchantment.lower())
        
        if not enchant_data:
            await interaction.response.send_message("❌ Invalid enchantment!", ephemeral=True)
            return
        
        if level > enchant_data['max_level']:
            await interaction.response.send_message(
                f"❌ Max level for {enchant_data['name']} is {enchant_data['max_level']}!",
                ephemeral=True
            )
            return
        
        if level < 1:
            await interaction.response.send_message(
                "❌ Level must be at least 1!",
                ephemeral=True
            )
            return
        
        inventory_item = await self.bot.db.get_inventory_item_by_slot(interaction.user.id, slot)
        if not inventory_item:
            await interaction.response.send_message(
                f"❌ No item found in slot {slot}!",
                ephemeral=True
            )
            return
        
        item_data = await self.bot.game_data.get_item(inventory_item['item_id'])
        if not item_data:
            await interaction.response.send_message("❌ Item not found!", ephemeral=True)
            return
        
        valid_types = enchant_data.get('applies_to', [])
        item_type_lower = item_data.get('item_type', '').lower()
        if item_type_lower not in valid_types:
            await interaction.response.send_message(
                f"❌ This enchantment cannot be applied to {item_data['name']}!",
                ephemeral=True
            )
            return
        
        cost = level * 1000
        player = await self.bot.db.get_player(interaction.user.id)
        
        if player['coins'] < cost:
            await interaction.response.send_message(
                f"❌ You need {cost:,} coins to enchant this item!",
                ephemeral=True
            )
            return
        
        await self.bot.player_manager.remove_coins(interaction.user.id, cost)
        
        await self.bot.db.add_enchantment_to_item(inventory_item['id'], enchantment.lower(), level)
        
        xp_gained = level * 20
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('enchanting')
        xp_gained = int(xp_gained * xp_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        enchanting_skill = next((s for s in skills if s['skill_name'] == 'enchanting'), None)
        new_level = enchanting_skill['level'] if enchanting_skill else 0
        
        if enchanting_skill:
            new_xp = enchanting_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('enchanting', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'enchanting', xp=new_xp, level=new_level)

        await AchievementSystem.check_skill_achievements(
            self.bot.db, interaction, interaction.user.id, 'enchanting', new_level
        )
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='enchanting', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')

        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_enchant_date'):
            import time
            await self.bot.db.update_progression(
                interaction.user.id,
                first_enchant_date=int(time.time())
            )
            await AchievementSystem.unlock_single_achievement(
                self.bot.db, interaction, interaction.user.id, 'first_enchant'
            )

        stats = await self.bot.db.get_player_stats(interaction.user.id)
        if stats:
            total_enchants = stats.get('total_enchants', 0) + 1
            await self.bot.db.update_player_stats(interaction.user.id, total_enchants=total_enchants)

            from utils.achievement_tracker import AchievementTracker
            enchant_achievements = await AchievementTracker.check_value_based_achievements(
                self.bot.db, interaction.user.id, 'enchants', total_enchants
            )
            await AchievementSystem.check_and_notify(
                self.bot.db, interaction, interaction.user.id, enchant_achievements
            )

        if level >= enchant_data['max_level']:
            await AchievementSystem.unlock_single_achievement(
                self.bot.db, interaction, interaction.user.id, 'enchant_max'
            )
        
        embed = discord.Embed(
            title="✨ Enchanted!",
            description=f"Applied {enchant_data['name']} {level} to {item_data['name']}!",
            color=discord.Color.purple()
        )
        embed.add_field(name="Cost", value=f"{cost:,} coins", inline=True)
        embed.add_field(name="Effect", value=enchant_data['description'], inline=True)
        embed.add_field(name="XP Gained", value=f"+{xp_gained} Enchanting XP", inline=True)
        
        if xp_multiplier > 1.0:
            event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}"
        
        await interaction.response.send_message(embed=embed)

    @enchant.autocomplete('item')
    async def enchant_item_autocomplete(self, interaction: discord.Interaction, current: str):
        return await item_autocomplete(interaction, current)

    @app_commands.command(name="anvil", description="Combine items in the anvil")
    @app_commands.describe(
        item1="First item to combine",
        item2="Second item to combine"
    )
    async def anvil(self, interaction: discord.Interaction, item1: str, item2: str):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        player = await self.bot.db.get_player(interaction.user.id)
        
        base_cost = 500
        level_penalty = 100
        
        total_cost = base_cost
        
        if player['coins'] < total_cost:
            await interaction.followup.send(
                f"❌ You need {total_cost:,} coins to use the anvil!",
                ephemeral=True
            )
            return
        
        await self.bot.player_manager.remove_coins(interaction.user.id, total_cost)
        
        result_item = f"{item1} (Enhanced)"
        durability_bonus = 50
        enchant_transfer = True
        
        embed = discord.Embed(
            title="🔨 Anvil - Item Combined!",
            description=f"Successfully combined items in the anvil!",
            color=discord.Color.dark_gray()
        )
        
        embed.add_field(
            name="Result",
            value=f"**{result_item}**\n+{durability_bonus}% Durability\nEnchantments transferred",
            inline=False
        )
        
        embed.add_field(name="Cost", value=f"{total_cost:,} coins", inline=True)
        
        xp_gained = 50
        xp_multiplier = await self.event_effects.get_xp_multiplier('enchanting')
        xp_gained = int(xp_gained * xp_multiplier)
        
        embed.add_field(name="XP Gained", value=f"+{xp_gained} Enchanting XP", inline=True)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        enchanting_skill = next((s for s in skills if s['skill_name'] == 'enchanting'), None)
        
        if enchanting_skill:
            new_xp = enchanting_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('enchanting', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'enchanting', xp=new_xp, level=new_level)
        
        await interaction.followup.send(embed=embed)

    @anvil.autocomplete('item1')
    async def anvil_item1_autocomplete(self, interaction: discord.Interaction, current: str):
        return await item_autocomplete(interaction, current)

    @anvil.autocomplete('item2')
    async def anvil_item2_autocomplete(self, interaction: discord.Interaction, current: str):
        return await item_autocomplete(interaction, current)

    @app_commands.command(name="enchantments", description="View available enchantments for an item type")
    @app_commands.describe(item_type="Type of item to view enchantments for")
    @app_commands.choices(item_type=[
        app_commands.Choice(name="Sword", value="sword"),
        app_commands.Choice(name="Bow", value="bow"),
        app_commands.Choice(name="Axe", value="axe"),
        app_commands.Choice(name="Pickaxe", value="pickaxe"),
        app_commands.Choice(name="Shovel", value="shovel"),
        app_commands.Choice(name="Helmet", value="helmet"),
        app_commands.Choice(name="Chestplate", value="chestplate"),
        app_commands.Choice(name="Leggings", value="leggings"),
        app_commands.Choice(name="Boots", value="boots"),
    ])
    async def enchantments(self, interaction: discord.Interaction, item_type: str):
        await interaction.response.defer()
        
        all_enchants = await self.bot.game_data.get_all_enchantments()
        
        applicable_enchants = []
        for enchant in all_enchants:
            applies_to = enchant.get('applies_to', [])
            if item_type.lower() in applies_to:
                applicable_enchants.append(enchant)
        
        if not applicable_enchants:
            await interaction.followup.send(
                f"❌ No enchantments found for {item_type}!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"✨ {item_type.title()} Enchantments",
            description=f"Available enchantments for {item_type}s",
            color=discord.Color.purple()
        )
        
        for enchant in sorted(applicable_enchants, key=lambda x: x['name'])[:25]:
            value = f"{enchant.get('description', 'No description')}\nMax Level: {enchant['max_level']}"
            embed.add_field(
                name=enchant['name'],
                value=value,
                inline=True
            )
        
        if len(applicable_enchants) > 25:
            embed.set_footer(text=f"Showing 25 of {len(applicable_enchants)} enchantments")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EnchantingAdvanced(bot))
