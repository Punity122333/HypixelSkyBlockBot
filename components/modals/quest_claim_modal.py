import discord

class QuestClaimModal(discord.ui.Modal, title="Claim Quest Reward"):
    quest_input = discord.ui.TextInput(
        label="Quest ID or Serial Number",
        placeholder="Enter quest ID (e.g., mine_coal_quest) or #1, #2, etc.",
        required=True,
        max_length=100
    )
    
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        quest_input = self.quest_input.value.strip()
        
        quest_id = None
        if quest_input.startswith('#'):
            try:
                serial = int(quest_input[1:])
                for quest in self.view.user_quests_data:
                    if quest['serial'] == serial:
                        quest_id = quest['quest_id']
                        break
                if not quest_id:
                    await interaction.followup.send(f"❌ Quest #{serial} not found!", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("❌ Invalid serial number format! Use #1, #2, etc.", ephemeral=True)
                return
        else:
            quest_id = quest_input
            found = False
            for quest in self.view.user_quests_data:
                if quest['quest_id'] == quest_id or quest['name'].lower() == quest_id.lower():
                    quest_id = quest['quest_id']
                    found = True
                    break
            if not found:
                await interaction.followup.send(f"❌ Quest '{quest_input}' not found!", ephemeral=True)
                return
        
        quest = await self.view.bot.db.get_quest(self.view.user_id, quest_id)
        
        if not quest:
            await interaction.followup.send("❌ Quest not found!", ephemeral=True)
            return
        
        if not quest['completed']:
            await interaction.followup.send("❌ This quest is not completed yet!", ephemeral=True)
            return
        
        if quest['claimed']:
            await interaction.followup.send("❌ You already claimed this quest reward!", ephemeral=True)
            return
        
        quest_info = await self.view.bot.game_data.get_game_quest(quest_id)
        if not quest_info:
            await interaction.followup.send("❌ Invalid quest!", ephemeral=True)
            return
        
        await self.view.bot.player_manager.add_coins(self.view.user_id, quest_info['reward_coins'])
        
        for item_id, amount in quest_info['reward_items']:
            await self.view.bot.db.add_item_to_inventory(self.view.user_id, item_id, amount)
        
        await self.view.bot.db.claim_quest_reward(self.view.user_id, quest_id)
        
        embed = discord.Embed(
            title="🎉 Quest Completed!",
            description=f"**{quest_info['name']}**\n{quest_info['description']}",
            color=discord.Color.green()
        )
        
        rewards_text = f"💰 {quest_info['reward_coins']:,} coins"
        if quest_info['reward_items']:
            items_text = ", ".join([f"{amount}x {item_id}" for item_id, amount in quest_info['reward_items']])
            rewards_text += f"\n🎁 {items_text}"
        
        embed.add_field(name="Rewards Claimed", value=rewards_text, inline=False)
        
        await interaction.followup.send(embed=embed)
        
        await self.view.load_quests()
        self.view._update_buttons()
        view_embed = await self.view.get_embed()
        if interaction.message:
            await interaction.message.edit(embed=view_embed, view=self.view)
