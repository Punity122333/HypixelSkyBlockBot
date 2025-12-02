import discord
from discord.ext import commands
from discord import app_commands
import time

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

class MerchantMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.page = 0
        self.deals = []
    
    async def load_deals(self):
        self.deals = await self.bot.db.get_active_merchant_deals()
    
    async def get_embed(self):
        embed = discord.Embed(
            title="🏪 Traveling Merchants",
            description="Limited time deals from traveling merchants!",
            color=discord.Color.purple()
        )
        
        if not self.deals:
            embed.description = "No merchants are available right now. Check back later!"
            return embed
        
        per_page = 3
        start = self.page * per_page
        end = start + per_page
        page_deals = self.deals[start:end]
        
        for deal in page_deals:
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
                value += f"Deal ID: {deal['id']}"
            else:
                title = f"💰 {deal['npc_name']} is SELLING"
                value = f"**{item.name}** x{deal['quantity']}\n"
                value += f"Price: {deal['price']:,} coins\n"
                value += f"Expires in: {hours}h {minutes}m\n"
                value += f"Deal ID: {deal['id']}"
            
            embed.add_field(
                name=title,
                value=value,
                inline=False
            )
        
        total_pages = (len(self.deals) + per_page - 1) // per_page if self.deals else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Use commands to accept deals")
        return embed
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=0)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        per_page = 3
        total_pages = (len(self.deals) + per_page - 1) // per_page
        if self.page < total_pages - 1:
            self.page += 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.blurple, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await self.load_deals()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="✅ Accept Deal", style=discord.ButtonStyle.green, row=1)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(MerchantDealModal(self.bot))

class MerchantCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="merchants", description="View and interact with traveling merchants")
    async def merchants(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = MerchantMenuView(self.bot, interaction.user.id)
        await view.load_deals()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(MerchantCommands(bot))
