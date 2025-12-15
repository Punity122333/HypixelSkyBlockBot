import discord

class MinionFuelModal(discord.ui.Modal, title="Add Fuel to Minion"):
    minion_number = discord.ui.TextInput(
        label="Minion Number",
        placeholder="Enter the minion number",
        required=True,
        max_length=3
    )
    
    fuel_number = discord.ui.TextInput(
        label="Fuel Number",
        placeholder="Enter the fuel number from your inventory",
        required=True,
        max_length=3
    )
    
    def __init__(self, bot, user_id, minions, fuels):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.minions = minions
        self.fuels = fuels
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            minion_idx = int(self.minion_number.value) - 1
            fuel_idx = int(self.fuel_number.value) - 1
            
            if minion_idx < 0 or minion_idx >= len(self.minions):
                await interaction.response.send_message(
                    f"❌ Invalid minion number! Please choose between 1 and {len(self.minions)}.",
                    ephemeral=True
                )
                return
            
            if fuel_idx < 0 or fuel_idx >= len(self.fuels):
                await interaction.response.send_message(
                    f"❌ Invalid fuel number! Please choose between 1 and {len(self.fuels)}.",
                    ephemeral=True
                )
                return
            
            minion = self.minions[minion_idx]
            fuel = self.fuels[fuel_idx]
            
            success = await self.bot.db.minion_upgrades.apply_fuel(minion['id'], fuel['item_id'])
            
            if success:
                duration_hours = fuel.get('duration', 0) / 3600
                speed_boost = fuel.get('speed_boost', 1.0)
                speed_percent = (1.0 - speed_boost) * 100
                await interaction.response.send_message(
                    f"✅ Successfully added **{fuel['name']}** to **{minion['minion_type'].title()} Minion**!\n"
                    f"⚡ Speed boost: {speed_percent:.0f}% faster\n"
                    f"⏰ Duration: {duration_hours:.1f} hours",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Failed to apply fuel. Make sure you have the fuel in your inventory!",
                    ephemeral=True
                )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter valid numbers!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error applying fuel: {str(e)}",
                ephemeral=True
            )
