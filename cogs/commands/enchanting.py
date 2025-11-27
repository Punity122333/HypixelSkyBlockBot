import discord
from discord.ext import commands
from discord import app_commands

class EnchantingAdvanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        enchanting_skill = next((s for s in skills if s['skill_name'] == 'enchanting'), None)
        
        if enchanting_skill:
            new_xp = enchanting_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('enchanting', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'enchanting', xp=new_xp, level=new_level)
        
        embed = discord.Embed(
            title="✨ Enchanted!",
            description=f"Applied {enchant_data['name']} {level} to {item}!",
            color=discord.Color.purple()
        )
        embed.add_field(name="Cost", value=f"{cost:,} coins", inline=True)
        embed.add_field(name="Effect", value=enchant_data['description'], inline=True)
        embed.add_field(name="XP Gained", value=f"+{xp_gained} Enchanting XP", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="anvil", description="Combine items in the anvil")
    async def anvil(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔨 Anvil",
            description="Combine and repair items!",
            color=discord.Color.dark_gray()
        )
        
        embed.add_field(
            name="Functions",
            value="• Combine enchantments\n• Repair items\n• Apply books\n• Rename items",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EnchantingAdvanced(bot))
