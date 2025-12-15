import discord

class PetSelectModal(discord.ui.Modal, title="Choose Pet"):
    pet_number = discord.ui.TextInput(
        label="Pet Number",
        placeholder="Enter the number of the pet you want to equip",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, pets):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.pets = pets
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            idx = int(self.pet_number.value) - 1
            if idx < 0 or idx >= len(self.pets):
                await interaction.response.send_message(
                    f"❌ Invalid pet number! Please choose between 1 and {len(self.pets)}.",
                    ephemeral=True
                )
                return
            
            pet = self.pets[idx]
            pet_id = pet['id']
            
            await self.bot.db.equip_pet(self.user_id, pet_id)
            
            rarity_color_map = {
                'COMMON': 0xFFFFFF,
                'UNCOMMON': 0x55FF55,
                'RARE': 0x5555FF,
                'EPIC': 0xAA00AA,
                'LEGENDARY': 0xFFAA00,
                'MYTHIC': 0xFF5555
            }
            
            color = rarity_color_map.get(pet['rarity'], 0xFFFFFF)
            
            embed = discord.Embed(
                title="🐾 Pet Equipped!",
                description=f"You equipped your **{pet['rarity']} {pet['pet_type'].title()}** (Level {pet['level']})!",
                color=color
            )
            
            stats = await self.bot.db.get_pet_stats_by_type_rarity(pet['pet_type'].lower(), pet['rarity'].upper())
            if stats:
                level_multiplier = 1 + (pet['level'] / 100)
                scaled_stats = {k: int(v * level_multiplier) for k, v in stats.items()}
                
                if scaled_stats:
                    stats_text = "\n".join([f"**{k.replace('_', ' ').title()}**: +{v}" for k, v in scaled_stats.items()])
                    embed.add_field(name="Stats", value=stats_text, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number!",
                ephemeral=True
            )
