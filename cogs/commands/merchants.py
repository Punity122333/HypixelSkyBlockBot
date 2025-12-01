import discord
from discord.ext import commands
from discord import app_commands
import time
from utils.systems.economy_system import EconomySystem

class MerchantCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="merchants", description="View available merchant deals")
    async def merchants(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        deals = await self.bot.db.get_active_merchant_deals()
        
        embed = discord.Embed(
            title="🏪 Traveling Merchants",
            description="Limited time deals from traveling merchants!",
            color=discord.Color.purple()
        )
        
        if not deals:
            embed.description = "No merchants are available right now. Check back later!"
        else:
            for deal in deals:
                item = await self.bot.game_data.get_item(deal['item_id'])
                if not item:
                    continue
                
                time_left = deal['expires_at'] - int(time.time())
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                
                if deal['deal_type'] == 'buy':
                    title = f"🛒 {deal['npc_name']} is BUYING"
                    value = f"**{item.name}** x{deal['quantity']}\n"
                    value += f"Offering: {deal['price']:,} coins\n"
                    value += f"Expires in: {hours}h {minutes}m\n"
                    value += f"Use `/merchant_sell {deal['id']}`"
                else:
                    title = f"💰 {deal['npc_name']} is SELLING"
                    value = f"**{item.name}** x{deal['quantity']}\n"
                    value += f"Price: {deal['price']:,} coins\n"
                    value += f"Expires in: {hours}h {minutes}m\n"
                    value += f"Use `/merchant_buy {deal['id']}`"
                
                embed.add_field(
                    name=title,
                    value=value,
                    inline=False
                )
        
        embed.set_footer(text="Merchant deals refresh periodically with new offers!")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="merchant_buy", description="Buy from a merchant")
    @app_commands.describe(deal_id="The deal ID to accept")
    async def merchant_buy(self, interaction: discord.Interaction, deal_id: int):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        success = await self.bot.db.claim_merchant_deal(deal_id, interaction.user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ Deal Completed!",
                description="You successfully purchased from the merchant!",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Failed to complete deal! Deal may have expired or you don't have enough coins.", ephemeral=True)

    @app_commands.command(name="merchant_sell", description="Sell to a merchant")
    @app_commands.describe(deal_id="The deal ID to accept")
    async def merchant_sell(self, interaction: discord.Interaction, deal_id: int):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        success = await self.bot.db.claim_merchant_deal(deal_id, interaction.user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ Deal Completed!",
                description="You successfully sold to the merchant!",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Failed to complete deal! You may not have the required items.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MerchantCommands(bot))
