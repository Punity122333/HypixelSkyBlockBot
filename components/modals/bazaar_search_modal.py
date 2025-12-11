import discord
from utils.normalize import normalize_item_id
import time

class BazaarSearchModal(discord.ui.Modal, title="Search Bazaar Item"):
    item_name = discord.ui.TextInput(label="Item Name or ID", placeholder="Enter item name or ID", required=True)
    
    def __init__(self, bot, view):
        super().__init__()
        self.bot = bot
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        search_query = normalize_item_id(self.item_name.value)
        
        if not self.view.items_list:
            await self.view.load_items()
        
        matching_items = [
            item for item in self.view.items_list
            if search_query in normalize_item_id(item['name']) or search_query in item['id']
        ]
        
        if not matching_items:
            await interaction.followup.send(f"❌ No items found matching '{self.item_name.value}'", ephemeral=True)
            return
        
        if len(matching_items) == 1:
            item = matching_items[0]
            embed = discord.Embed(
                title=f"🔍 {item['name']}",
                description=f"Item ID: `{item['id']}`",
                color=discord.Color.gold()
            )
            embed.add_field(name="Buy Price", value=f"{item['buy_price']:.1f} coins", inline=True)
            embed.add_field(name="Sell Price", value=f"{item['sell_price']:.1f} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title=f"🔍 Search Results for '{self.item_name.value}'",
                description=f"Found {len(matching_items)} matching items:",
                color=discord.Color.gold()
            )
            for item in matching_items[:10]:
                embed.add_field(
                    name=item['name'],
                    value=f"Buy: {item['buy_price']:.1f} | Sell: {item['sell_price']:.1f}\n`{item['id']}`",
                    inline=False
                )
            if len(matching_items) > 10:
                embed.set_footer(text=f"Showing 10 of {len(matching_items)} results")
            await interaction.followup.send(embed=embed, ephemeral=True)
