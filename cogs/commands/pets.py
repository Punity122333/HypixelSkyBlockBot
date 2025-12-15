import discord
from discord.ext import commands
from discord import app_commands
from database.misc import get_pet_stats
from utils.autocomplete import pet_autocomplete
from components.views.pet_menu_view import PetMenuView

class PetCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pets", description="View your pet collection")
    async def pets(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = PetMenuView(self.bot, interaction.user.id)
        await view.load_pets()
        embed = await view.get_embed()
        await interaction.followup.send(embed=embed, view=view)
    

    @app_commands.command(name="pet_info", description="View detailed info about a pet")
    @app_commands.describe(pet_type="The type of pet")
    async def pet_info(self, interaction: discord.Interaction, pet_type: str):
        await interaction.response.defer()
        
        pet_type = pet_type.lower()
        
        all_pets = await self.bot.game_data.get_all_pet_stats()

        matching_pets = {k: v for k, v in all_pets.items() if v['pet_type'] == pet_type}
        
        if not matching_pets:
            PET_STATS = await get_pet_stats()
            if pet_type not in PET_STATS:
                await interaction.followup.send(f"❌ Unknown pet type: {pet_type}", ephemeral=True)
                return
        
        embed = discord.Embed(
            title=f"🐾 {pet_type.title()} Pet Info",
            description=f"All available rarities for {pet_type.title()}",
            color=discord.Color.blue()
        )
        
        if matching_pets:
            for pet_id, pet_data in matching_pets.items():
                rarity = pet_data['rarity']
                stats = pet_data.get('stats', {})
                stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in stats.items()])
                embed.add_field(
                    name=f"{rarity} (Level 1)",
                    value=stats_str,
                    inline=False
                )
        else:
            PET_STATS = await get_pet_stats()
            for rarity, stats in PET_STATS[pet_type].items():
                stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in stats.items()])
                embed.add_field(
                    name=f"{rarity} (Level 1)",
                    value=stats_str,
                    inline=False
                )
        
        embed.set_footer(text="Stats scale with pet level (up to +100% at level 100)")
        
        await interaction.followup.send(embed=embed)
        
    
    @pet_info.autocomplete('pet_type')
    async def pet_info_autocomplete(self, interaction: discord.Interaction, current: str):
        return await pet_autocomplete(interaction, current)

async def setup(bot):
    await bot.add_cog(PetCommands(bot))
