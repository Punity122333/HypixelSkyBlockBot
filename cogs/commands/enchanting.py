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
        item="Item to enchant (name or ID)",
        enchantment="Enchantment to apply",
        level="Enchantment level"
    )
    async def enchant(self, interaction: discord.Interaction, item: str, enchantment: str, level: int):
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
        
        cost = level * 1000
        player = await self.bot.db.get_player(interaction.user.id)
        
        if player['coins'] < cost:
            await interaction.response.send_message(
                f"❌ You need {cost:,} coins to enchant this item!",
                ephemeral=True
            )
            return

        inventory = await self.bot.db.get_inventory(interaction.user.id)
        if not inventory:
            await interaction.response.send_message(
                "❌ Your inventory is empty!",
                ephemeral=True
            )
            return

        matching_items = []
        item_search = item.lower().strip()
        valid_types = enchant_data.get('applies_to', [])
        
        for inv_item in inventory:
            item_obj = await self.bot.game_data.get_item(inv_item['item_id'])
            if item_obj:

                item_name = item_obj.name if hasattr(item_obj, 'name') else ''
                if (inv_item['item_id'].lower() == item_search or 
                    item_name.lower() == item_search or
                    item_search in inv_item['item_id'].lower() or
                    item_search in item_name.lower()):

                    item_type = item_obj.type if hasattr(item_obj, 'type') else ''
                    item_type_lower = item_type.lower()
                    if item_type_lower in valid_types:
                        matching_items.append({
                            'id': inv_item['id'],
                            'item_id': inv_item['item_id'],
                            'name': item_obj.name if hasattr(item_obj, 'name') else inv_item['item_id'],
                            'rarity': item_obj.rarity if hasattr(item_obj, 'rarity') else 'COMMON',
                            'amount': inv_item.get('amount', 1)
                        })
        
        if not matching_items:
            await interaction.response.send_message(
                f"❌ Could not find '{item}' in your inventory that can be enchanted with {enchant_data['name']}!",
                ephemeral=True
            )
            return

        await self.bot.player_manager.remove_coins(interaction.user.id, cost)

        xp_gained = level * 20

        if len(matching_items) == 1:
            inventory_item_id = matching_items[0]['id']
            item_name = matching_items[0]['name']
            
            await self.bot.db.add_enchantment_to_item(inventory_item_id, enchantment.lower(), level)
            
            xp_multiplier = await self.event_effects.get_xp_multiplier('enchanting')
            final_xp = int(xp_gained * xp_multiplier)
            
            skills = await self.bot.db.get_skills(interaction.user.id)
            enchanting_skill = next((s for s in skills if s['skill_name'] == 'enchanting'), None)
            new_level = enchanting_skill['level'] if enchanting_skill else 0
            
            if enchanting_skill:
                new_xp = enchanting_skill['xp'] + final_xp
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
                description=f"Applied {enchant_data['name']} {level} to {item_name}!",
                color=discord.Color.purple()
            )
            embed.add_field(name="Cost", value=f"{cost:,} coins", inline=True)
            embed.add_field(name="Effect", value=enchant_data['description'], inline=True)
            embed.add_field(name="XP Gained", value=f"+{final_xp} Enchanting XP", inline=True)
            
            if xp_multiplier > 1.0:
                event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n{event_text}"
            
            await interaction.response.send_message(embed=embed)
        else:

            from components.views.enchant_item_select_view import EnchantItemSelectView
            
            view = EnchantItemSelectView(
                self.bot, interaction.user.id, matching_items, 
                enchantment.lower(), level, enchant_data, cost, xp_gained
            )
            
            embed = discord.Embed(
                title=f"✨ Select Item to Enchant",
                description=f"Found {len(matching_items)} items matching '{item}'\n\nClick '✨ Choose Item' and enter the number.",
                color=discord.Color.purple()
            )
            
            for idx, match in enumerate(matching_items[:20], 1):
                amount_text = f" (x{match['amount']})" if match.get('amount', 1) > 1 else ""
                embed.add_field(
                    name=f"{idx}. {match['name']}{amount_text}",
                    value=f"✨ {match['rarity']}",
                    inline=False
                )
            
            embed.set_footer(text=f"Cost: {cost:,} coins | {enchant_data['name']} Level {level}")
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

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
