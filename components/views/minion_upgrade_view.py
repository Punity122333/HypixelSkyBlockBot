import discord

class MinionUpgradeView(discord.ui.View):
    def __init__(self, bot, user_id, minions):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.minions = minions

        options = []
        for i, minion in enumerate(minions[:25]):
            current_tier = minion['tier']
            upgrade_cost = 5000 * current_tier
            options.append(
                discord.SelectOption(
                    label=f"{minion['minion_type'].title()} Minion (Tier {current_tier})",
                    description=f"Upgrade to Tier {current_tier + 1} | Cost: {upgrade_cost:,} coins",
                    value=str(i)
                )
            )
        
        select = discord.ui.Select(
            placeholder="Select a minion to upgrade...",
            options=options,
            custom_id="minion_upgrade_select"
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return

        if not interaction.data or not interaction.data.get('values'):
            await interaction.response.send_message(
                "❌ No selection was made or invalid interaction data.",
                ephemeral=True
            )
            return

        idx = int(interaction.data['values'][0])
        minion = self.minions[idx]
        current_tier = minion['tier']
        
        try:
            minion_data = await self.bot.game_data.get_minion_data(minion['minion_type'])
            max_tier = minion_data['max_tier'] if minion_data else 11
            
            if current_tier >= max_tier:
                await interaction.response.send_message(
                    f"❌ This minion is already at max tier ({max_tier})!",
                    ephemeral=True
                )
                return
            
            upgrade_cost = 5000 * current_tier
            
            player = await self.bot.db.players.get_player(self.user_id)
            if player['coins'] < upgrade_cost:
                await interaction.response.send_message(
                    f"❌ You need {upgrade_cost:,} coins to upgrade this minion! (You have {player['coins']:,})",
                    ephemeral=True
                )
                return
            
            await self.bot.db.players.update_player(self.user_id, coins=player['coins'] - upgrade_cost)
            await self.bot.db.upgrade_minion(minion['id'])
            
            await interaction.response.send_message(
                f"✅ Successfully upgraded **{minion['minion_type'].title()} Minion** to Tier {current_tier + 1} for {upgrade_cost:,} coins!",
                ephemeral=True
            )
            self.stop()
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error upgrading minion: {str(e)}",
                ephemeral=True
            )
