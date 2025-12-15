import discord

class MinionSkinSelectView(discord.ui.View):
    def __init__(self, bot, user_id, minions, skins):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.minions = minions
        self.skins = skins

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
            custom_id="minion_select_for_skin",
            row=0
        )
        minion_select.callback = self.minion_callback
        self.add_item(minion_select)

        skin_options = []
        for i, skin in enumerate(skins[:25]):
            skin_options.append(
                discord.SelectOption(
                    label=f"{skin['name']}",
                    description=f"Type: {skin['minion_type'].title()} | {skin['rarity']} | Qty: {skin['amount']}",
                    value=str(i)
                )
            )
        
        skin_select = discord.ui.Select(
            placeholder="Select skin to apply...",
            options=skin_options,
            custom_id="skin_select",
            row=1
        )
        skin_select.callback = self.skin_callback
        self.add_item(skin_select)

        self.selected_minion_idx = None
        self.selected_skin_idx = None

    async def minion_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        values = getattr(interaction, "values", None)
        if not values:
            data = getattr(interaction, "data", None)
            values = data.get("values") if data else None
        if not values:
            await interaction.response.send_message("❌ Could not determine selected minion.", ephemeral=True)
            return

        self.selected_minion_idx = int(values[0])

        if self.selected_skin_idx is not None:
            await self.apply_skin(interaction)
        else:
            await interaction.response.send_message(
                "✅ Minion selected! Now select a skin.",
                ephemeral=True
            )
    
    async def skin_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)

        values = getattr(interaction, "values", None)
        if not values:
            data = getattr(interaction, "data", None)
            values = data.get("values") if data else None
        if not values:
            await interaction.response.send_message("❌ Could not determine selected skin.", ephemeral=True)
            return

        self.selected_skin_idx = int(values[0])

        if self.selected_minion_idx is not None:
            await self.apply_skin(interaction)
        else:
            await interaction.response.send_message(
                "✅ Skin selected! Now select a minion.",
                ephemeral=True
            )
    
    async def apply_skin(self, interaction: discord.Interaction):
        minion = self.minions[self.selected_minion_idx]
        skin = self.skins[self.selected_skin_idx]
        
        try:
            success = await self.bot.db.minion_upgrades.apply_skin(minion['id'], skin['item_id'])
            
            if success:
                await interaction.response.send_message(
                    f"✅ Successfully applied **{skin['name']}** to **{minion['minion_type'].title()} Minion**!",
                    ephemeral=True
                )
                self.stop()
            else:
                await interaction.response.send_message(
                    "❌ Failed to apply skin. Make sure the skin matches the minion type and you have it in your inventory!",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error applying skin: {str(e)}",
                ephemeral=True
            )
