import discord

class MinionRemoveView(discord.ui.View):
    def __init__(self, bot, user_id, minions):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.minions = minions

        options = []
        for i, minion in enumerate(minions[:25]):
            options.append(
                discord.SelectOption(
                    label=f"{minion['minion_type'].title()} Minion (Tier {minion['tier']})",
                    description=f"Slot {minion.get('island_slot', i+1)} - Returns to inventory",
                    value=str(i)
                )
            )
        
        select = discord.ui.Select(
            placeholder="Select a minion to remove...",
            options=options,
            custom_id="minion_remove_select"
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return

        if not interaction.data or not interaction.data.get('values'):
            await interaction.response.send_message(
                "❌ Could not determine which minion to remove.",
                ephemeral=True
            )
            return

        idx = int(interaction.data['values'][0])
        minion = self.minions[idx]
        minion_type = minion['minion_type']
        tier = minion['tier']
        
        try:
            collected_items = await self.bot.db.collect_minion(minion['id'])
            
            item_id = f"{minion_type}_minion"
            await self.bot.db.add_item_to_inventory(self.user_id, item_id, 1)
            
            await self.bot.db.execute(
                'DELETE FROM player_minions WHERE id = ?',
                (minion['id'],)
            )
            await self.bot.db.commit()
            
            collected_text = ""
            if collected_items:
                items_list = [f"{item['item_id'].replace('_', ' ').title()} x{item['amount']}" for item in collected_items]
                collected_text = f"\n\n📦 Collected: {', '.join(items_list)}"
            
            await interaction.response.send_message(
                f"✅ Successfully removed **{minion_type.title()} Minion (Tier {tier})**!\n"
                f"It has been returned to your inventory.{collected_text}",
                ephemeral=True
            )
            self.stop()
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error removing minion: {str(e)}",
                ephemeral=True
            )
