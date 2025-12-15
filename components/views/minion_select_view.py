import discord

class MinionSelectView(discord.ui.View):
    def __init__(self, bot, user_id, minions):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.minions = minions

        options = []
        for i, minion in enumerate(minions[:25]):
            options.append(
                discord.SelectOption(
                    label=f"{minion['name']}",
                    description=f"Amount: {minion['amount']}",
                    value=str(i)
                )
            )
        
        select = discord.ui.Select(
            placeholder="Select a minion to place...",
            options=options,
            custom_id="minion_select"
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return

        # Fix: Check if interaction.data and values are present
        if not interaction.data or not interaction.data.get('values'):
            await interaction.response.send_message(
                "❌ Could not process your selection. Please try again.",
                ephemeral=True
            )
            return

        idx = int(interaction.data['values'][0])
        minion = self.minions[idx]
        item_id = minion['item_id']
        minion_type = item_id.replace('_minion', '')
        
        try:
            await self.bot.db.inventory.remove_item(self.user_id, item_id, 1)
            
            existing_minions = await self.bot.db.get_user_minions(self.user_id)
            next_slot = len(existing_minions) + 1
            
            await self.bot.db.add_minion(self.user_id, minion_type, 1, next_slot)
            
            await interaction.response.send_message(
                f"✅ Successfully placed **{minion['name']}** in slot {next_slot}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error placing minion: {str(e)}",
                ephemeral=True
            )
