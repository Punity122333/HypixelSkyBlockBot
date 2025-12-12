import discord
from utils.normalize import normalize_item_id


class MuseumDonateModal(discord.ui.Modal, title="Donate to Museum"):
    slot = discord.ui.TextInput(
        label="Inventory Slot Number",
        placeholder="Enter the slot number of the item to donate",
        required=True,
        max_length=5
    )
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            slot_num = int(self.slot.value)
        except ValueError:
            await interaction.response.send_message("❌ Invalid slot number!", ephemeral=True)
            return
        
        inventory = await self.bot.db.inventory.get_inventory(interaction.user.id)
        
        if slot_num < 0 or slot_num >= len(inventory):
            await interaction.response.send_message(
                f"❌ Invalid slot! You have {len(inventory)} items (slots 0-{len(inventory)-1}).",
                ephemeral=True
            )
            return
        
        item_data = inventory[slot_num]
        item_id = item_data['item_id']
        
        game_item = await self.bot.game_data.get_item(item_id)
        if not game_item:
            await interaction.response.send_message("❌ Item not found in game data!", ephemeral=True)
            return
        
        rarity = game_item.get('rarity', 'COMMON')
        item_name = game_item.get('name', item_id.replace('_', ' ').title())
        
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
