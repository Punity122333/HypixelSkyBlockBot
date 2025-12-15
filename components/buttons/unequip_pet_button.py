import discord

class UnequipPetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🐾 Unequip Pet", style=discord.ButtonStyle.red, custom_id="unequip_pet", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        bot = interaction.client
        user_id = interaction.user.id

        db = getattr(bot, "db", None)
        if db is None:
            await interaction.response.send_message(
                "❌ Database connection is not available.",
                ephemeral=True
            )
            return

        active_pet = await db.get_active_pet(user_id) 
        
        if not active_pet:
            await interaction.response.send_message(
                "❌ You don't have any pet equipped!",
                ephemeral=True
            )
            return
        
        await db.unequip_pet(user_id)
        
        await interaction.response.send_message(
            f"✅ Unequipped your **{active_pet['rarity']} {active_pet['pet_type'].title()}** (Level {active_pet['level']})!",
            ephemeral=True
        )
