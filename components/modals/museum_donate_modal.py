import discord
from utils.normalize import normalize_item_id


class MuseumDonateModal(discord.ui.Modal, title="Donate to Museum"):
    item_id_input = discord.ui.TextInput(
        label="Item ID",
        placeholder="Enter the item ID to donate (e.g., wooden_sword)",
        required=True,
        max_length=100
    )
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        item_id = normalize_item_id(self.item_id_input.value)
        
        inventory = await self.bot.db.inventory.get_inventory(interaction.user.id)
        
        has_item = False
        for inv_item in inventory:
            if inv_item['item_id'] == item_id:
                has_item = True
                break
        
        if not has_item:
            await interaction.response.send_message(
                f"❌ You don't have any **{item_id}** in your inventory!",
                ephemeral=True
            )
            return
        
        game_item = await self.bot.game_data.get_item(item_id)
        if not game_item:
            await interaction.response.send_message("❌ Item not found in game data!", ephemeral=True)
            return
        
        rarity = game_item.rarity
        item_name = game_item.name
        
        result = await self.bot.db.museum.donate_item(interaction.user.id, item_id, rarity)
        
        if not result['success']:
            await interaction.response.send_message(
                f"❌ {result.get('error', 'Cannot donate this item')}",
                ephemeral=True
            )
            return
        
        await self.bot.db.inventory.remove_item_from_inventory(interaction.user.id, item_id, 1)
        
        embed = discord.Embed(
            title="🏛️ Item Donated!",
            description=f"You donated **{item_name}** to your museum!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Rarity", value=rarity, inline=True)
        embed.add_field(name="Points Earned", value=str(result['points']), inline=True)
        embed.add_field(name="Total Items", value=str(result['total_donations']), inline=True)
        embed.add_field(name="Total Points", value=f"{result['total_points']:,}", inline=True)
        
        if result.get('milestone_reward'):
            milestone_reward = result['milestone_reward']
            embed.add_field(
                name="🎉 Milestone Reached!",
                value=f"**{milestone_reward['title']}**\n{milestone_reward['coins']:,} coins awarded!",
                inline=False
            )
            await self.bot.player_manager.add_coins(interaction.user.id, milestone_reward['coins'])
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await self.parent_view.load_data()
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        
        if hasattr(interaction, 'message') and interaction.message:
            await interaction.message.edit(embed=embed, view=self.parent_view)
