import discord
from discord.ext import commands
from discord import app_commands
from utils.event_effects import EventEffects
from utils.autocomplete import item_autocomplete

class EnchantingAdvanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_effects = EventEffects(bot)

    @app_commands.command(name="enchant", description="Enchant an item")
    @app_commands.describe(
        item="Item to enchant",
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
        
        cost = level * 1000
        player = await self.bot.db.get_player(interaction.user.id)
        
        if player['coins'] < cost:
            await interaction.response.send_message(
                f"❌ You need {cost:,} coins to enchant this item!",
                ephemeral=True
            )
            return
        
        await self.bot.player_manager.remove_coins(interaction.user.id, cost)
        
        xp_gained = level * 20
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('enchanting')
        xp_gained = int(xp_gained * xp_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        enchanting_skill = next((s for s in skills if s['skill_name'] == 'enchanting'), None)
        
        if enchanting_skill:
            new_xp = enchanting_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('enchanting', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'enchanting', xp=new_xp, level=new_level)
            
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='enchanting', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        
        embed = discord.Embed(
            title="✨ Enchanted!",
            description=f"Applied {enchant_data['name']} {level} to {item}!",
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

async def setup(bot):
    await bot.add_cog(EnchantingAdvanced(bot))
