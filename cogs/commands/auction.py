import discord
from discord.ext import commands
from discord import app_commands
import time
from utils.autocomplete import item_autocomplete
from utils.systems.economy_system import EconomySystem

class AuctionCreateModal(discord.ui.Modal, title="Create Auction"):
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount (default: 1)", required=False, default="1")
    starting_bid = discord.ui.TextInput(label="Starting Bid", placeholder="Enter starting bid", required=True)
    duration_hours = discord.ui.TextInput(label="Duration (hours)", placeholder="1-48 hours", required=True)
    bin_price = discord.ui.TextInput(label="BIN Price (optional)", placeholder="Buy it now price", required=False)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value) if self.amount.value else 1
            starting_bid = int(self.starting_bid.value)
            duration_hours = int(self.duration_hours.value)
            bin_price = int(self.bin_price.value) if self.bin_price.value else 0
        except ValueError:
            await interaction.followup.send("❌ Invalid input values!", ephemeral=True)
            return
        # Fix: Use a local variable for normalized item_id
        item_id_normalized = self.item_id.value.lower().replace(" ", "_")
        item = await self.bot.game_data.get_item(item_id_normalized)
        if not item:
            await interaction.followup.send("❌ Invalid item!", ephemeral=True)
            return
        
        if duration_hours < 1 or duration_hours > 48:
            await interaction.followup.send("❌ Duration must be between 1 and 48 hours!", ephemeral=True)
            return
        
        item_count = await self.bot.db.get_item_count(interaction.user.id, item_id_normalized)
        if item_count < amount:
            await interaction.followup.send(f"❌ You don't have enough {item.name}!", ephemeral=True)
            return
        
        result = await EconomySystem.create_auction(self.bot.db, interaction.user.id, item_id_normalized, amount, starting_bid, duration_hours, bin_price if bin_price > 0 else None)
        
        if result['success']:
            await self.bot.db.remove_item_from_inventory(interaction.user.id, item_id_normalized, amount)
            embed = discord.Embed(title="✅ Auction Created!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{amount}x {item.name}", inline=True)
            embed.add_field(name="Starting Bid", value=f"{starting_bid:,} coins", inline=True)
            if bin_price > 0:
                embed.add_field(name="BIN Price", value=f"{bin_price:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Failed to create auction')}", ephemeral=True)

class AuctionBidModal(discord.ui.Modal, title="Place Bid"):
    auction_id = discord.ui.TextInput(label="Auction ID", placeholder="Enter auction ID", required=True)
    bid_amount = discord.ui.TextInput(label="Bid Amount", placeholder="Enter your bid", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            auction_id = int(self.auction_id.value)
            bid_amount = int(self.bid_amount.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid input values!", ephemeral=True)
            return
        
        result = await EconomySystem.place_bid(self.bot.db, interaction.user.id, auction_id, bid_amount)
        
        if result['success']:
            embed = discord.Embed(title="✅ Bid Placed!", color=discord.Color.green())
            embed.add_field(name="Auction", value=f"#{auction_id}", inline=True)
            embed.add_field(name="Bid Amount", value=f"{bid_amount:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Bid failed')}", ephemeral=True)

class AuctionBINModal(discord.ui.Modal, title="Buy Instantly"):
    auction_id = discord.ui.TextInput(label="Auction ID", placeholder="Enter auction ID", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            auction_id = int(self.auction_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid auction ID!", ephemeral=True)
            return
        
        result = await EconomySystem.buy_bin(self.bot.db, interaction.user.id, auction_id)
        
        if result['success']:
            embed = discord.Embed(title="✅ Purchase Successful!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{result['amount']}x {result['item_id'].replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Price", value=f"{result['price']:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Purchase failed')}", ephemeral=True)

class AuctionMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.auctions = []
        self.current_view = 'browse'
    
    async def load_auctions(self):
        self.auctions = await self.bot.db.get_active_auctions(50)
    
    async def get_embed(self):
        if self.current_view == 'browse':
            return await self.get_browse_embed()
        elif self.current_view == 'my_auctions':
            return await self.get_my_auctions_embed()
        else:
            return await self.get_browse_embed()
    
    async def get_browse_embed(self):
        embed = discord.Embed(
            title="🔨 Auction House",
            description=f"Browse and interact with auctions",
            color=discord.Color.gold()
        )
        
        start = self.current_page * 5
        end = start + 5
        page_auctions = self.auctions[start:end]
        
        if not page_auctions:
            embed.description = "No active auctions! Create one to get started."
        else:
            for auction in page_auctions:
                item = await self.bot.game_data.get_item(auction['item_id'])
                if not item:
                    continue
                
                time_left = auction['end_time'] - int(time.time())
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                
                value = f"Current Bid: {auction['current_bid']:,} coins\n"
                value += f"Ends in: {hours}h {minutes}m\n"
                if auction['bin']:
                    value += f"BIN: {auction['buy_now_price']:,} coins"
                
                embed.add_field(
                    name=f"#{auction['id']} - {auction['amount']}x {item.name}",
                    value=value,
                    inline=False
                )
        
        total_pages = (len(self.auctions) + 4) // 5
        embed.set_footer(text=f"Page {self.current_page + 1}/{max(1, total_pages)}")
        return embed
    
    async def get_my_auctions_embed(self):
        if self.bot.db.conn:
            async with self.bot.db.conn.execute('''
                SELECT ah.*, ai.item_id, ai.amount
                FROM auction_house ah
                JOIN auction_items ai ON ah.id = ai.auction_id
                WHERE ah.seller_id = ? AND ah.ended = 0
                ORDER BY ah.created_at DESC
            ''', (self.user_id,)) as cursor:
                my_auctions = await cursor.fetchall()
        else:
            my_auctions = []
        
        embed = discord.Embed(
            title="📜 Your Auctions",
            description=f"You have {len(my_auctions)} active auctions",
            color=discord.Color.blue()
        )
        
        if not my_auctions:
            embed.description = "No active auctions! Use commands to create one."
        else:
            for auction in my_auctions[:10]:
                item = await self.bot.game_data.get_item(auction['item_id'])
                if item:
                    value = f"Current Bid: {auction['current_bid']:,} coins"
                    if auction['bin']:
                        value += f"\nBIN: {auction['buy_now_price']:,} coins"
                    embed.add_field(name=f"#{auction['id']} - {auction['amount']}x {item.name}", value=value, inline=False)
        
        return embed
    
    @discord.ui.button(label="🔨 Browse", style=discord.ButtonStyle.blurple, row=0)
    async def browse_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'browse'
        self.current_page = 0
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="📜 My Auctions", style=discord.ButtonStyle.green, row=0)
    async def my_auctions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'my_auctions'
        self.current_page = 0
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = (len(self.auctions) + 4) // 5
        if self.current_page < total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="➕ Create", style=discord.ButtonStyle.green, row=2)
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AuctionCreateModal(self.bot))
    
    @discord.ui.button(label="💰 Bid", style=discord.ButtonStyle.blurple, row=2)
    async def bid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AuctionBidModal(self.bot))
    
    @discord.ui.button(label="⚡ Buy Now", style=discord.ButtonStyle.red, row=2)
    async def bin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AuctionBINModal(self.bot))

class AuctionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auction", description="Access the Auction House")
    async def auction(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = AuctionMenuView(self.bot, interaction.user.id)
        await view.load_auctions()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AuctionCommands(bot))
