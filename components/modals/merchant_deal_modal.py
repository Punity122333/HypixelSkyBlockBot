import discord

class MerchantDealModal(discord.ui.Modal, title="Accept Merchant Deal"):
    deal_id = discord.ui.TextInput(label="Deal ID", placeholder="Enter deal ID to accept", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            deal_id = int(self.deal_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid deal ID!", ephemeral=True)
            return
        
        success = await self.bot.db.claim_merchant_deal(deal_id, interaction.user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ Deal Completed!",
                description="You successfully completed the merchant deal!",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to complete deal! Deal may have expired or you don't have enough coins/items.", ephemeral=True)