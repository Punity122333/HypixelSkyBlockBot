import discord
from utils.data.game_constants import PET_STATS

class PetEquipModal(discord.ui.Modal, title="Equip Pet"):
    pet_type = discord.ui.TextInput(label="Pet Type", placeholder="Enter pet type (e.g. wolf)", required=True)
    rarity = discord.ui.TextInput(label="Rarity", placeholder="Enter rarity (e.g. LEGENDARY)", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        pets = await self.bot.db.get_user_pets(interaction.user.id)
        
        matching_pet = None
        for pet in pets:
            if pet['pet_type'].lower() == self.pet_type.value.lower() and pet['rarity'].upper() == self.rarity.value.upper():
                matching_pet = pet
                break
        
        if not matching_pet:
            await interaction.followup.send(f"❌ You don't have a {self.rarity.value.upper()} {self.pet_type.value.title()} pet!", ephemeral=True)
            return
        
        await self.bot.db.equip_pet(interaction.user.id, matching_pet['id'])
        
        rarity_color_hex = await self.bot.game_data.get_rarity_color(self.rarity.value.upper())
        if rarity_color_hex:
            color = int(rarity_color_hex.replace('#', ''), 16)
        else:
            rarity_colors_fallback = {
                'COMMON': 0x999999,
                'UNCOMMON': 0x55FF55,
                'RARE': 0x5555FF,
                'EPIC': 0xAA00AA,
                'LEGENDARY': 0xFFAA00,
                'MYTHIC': 0xFF55FF
            }
            color = rarity_colors_fallback.get(self.rarity.value.upper(), discord.Color.green())
        
        embed = discord.Embed(
            title="🐾 Pet Equipped!",
            description=f"You equipped your **{self.rarity.value.upper()} {self.pet_type.value.title()}** (Level {matching_pet['level']})!",
            color=color
        )
        
        stats = PET_STATS.get(self.pet_type.value.lower(), {}).get(self.rarity.value.upper(), {})
        level_multiplier = 1 + (matching_pet['level'] / 100)
        scaled_stats = {k: int(v * level_multiplier) for k, v in stats.items()}
        
        if scaled_stats:
            stats_str = "\n".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in scaled_stats.items()])
            embed.add_field(name="Stats", value=stats_str, inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)