import discord

class MinionFuelSelectView(discord.ui.View):
    def __init__(self, bot, user_id, minions, fuels):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.minions = minions
        self.fuels = fuels

        minion_options = []
        for i, minion in enumerate(minions[:25]):
            minion_options.append(
                discord.SelectOption(
                    label=f"{minion['minion_type'].title()} Minion (Tier {minion['tier']})",
                    description=f"Slot {minion.get('island_slot', i+1)}",
                    value=str(i)
                )
            )
        
        minion_select = discord.ui.Select(
            placeholder="Select a minion...",
            options=minion_options,
            custom_id="minion_select_for_fuel",
            row=0
        )
        minion_select.callback = self.minion_callback
        self.add_item(minion_select)

        fuel_options = []
        for i, fuel in enumerate(fuels[:25]):
            duration_hours = fuel.get('duration', 0) / 3600
            speed_boost = fuel.get('speed_boost', 1.0)
            speed_percent = (1.0 - speed_boost) * 100
            fuel_options.append(
                discord.SelectOption(
                    label=f"{fuel['name']}",
                    description=f"{speed_percent:.0f}% faster | {duration_hours:.1f}h | Qty: {fuel['amount']}",
                    value=str(i)
                )
            )
        
        fuel_select = discord.ui.Select(
            placeholder="Select fuel to apply...",
            options=fuel_options,
            custom_id="fuel_select",
            row=1
        )
        fuel_select.callback = self.fuel_callback
        self.add_item(fuel_select)

        self.selected_minion_idx = None
        self.selected_fuel_idx = None

    async def minion_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        

        values = interaction.data.get('values') if interaction.data else None
        if not values:
            await interaction.response.send_message(
                "❌ No minion selected. Please try again.",
                ephemeral=True
            )
            return

        self.selected_minion_idx = int(values[0])
        
        if self.selected_fuel_idx is not None:
            await self.apply_fuel(interaction)
        else:
            await interaction.response.send_message(
                "✅ Minion selected! Now select a fuel.",
                ephemeral=True
            )
    
    async def fuel_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return

        values = interaction.data.get('values') if interaction.data else None
        if not values:
            await interaction.response.send_message(
                "❌ No fuel selected. Please try again.",
                ephemeral=True
            )
            return

        self.selected_fuel_idx = int(values[0])
        
        if self.selected_minion_idx is not None:
            await self.apply_fuel(interaction)
        else:
            await interaction.response.send_message(
                "✅ Fuel selected! Now select a minion.",
                ephemeral=True
            )
    
    async def apply_fuel(self, interaction: discord.Interaction):
        minion = self.minions[self.selected_minion_idx]
        fuel = self.fuels[self.selected_fuel_idx]
        
        try:
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
                self.stop()
            else:
                await interaction.response.send_message(
                    "❌ Failed to apply fuel. Make sure you have the fuel in your inventory!",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error applying fuel: {str(e)}",
                ephemeral=True
            )
