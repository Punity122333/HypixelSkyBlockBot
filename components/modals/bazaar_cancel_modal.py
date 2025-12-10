import discord

class BazaarCancelModal(discord.ui.Modal, title="Cancel Order"):
    order_id = discord.ui.TextInput(label="Order ID", placeholder="Enter order ID to cancel", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            order_id = int(self.order_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid order ID!", ephemeral=True)
            return
        
        await self.bot.db.cancel_bazaar_order(order_id)
        
        embed = discord.Embed(title="✅ Order Cancelled!", description=f"Order #{order_id} has been cancelled", color=discord.Color.green())
        await interaction.followup.send(embed=embed, ephemeral=True)
