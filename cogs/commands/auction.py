import discord
from discord.ext import commands
from discord import app_commands
import time
import json

class AuctionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ah_create", description="Create an auction")
    @app_commands.describe(
        item_id="The item to auction",
        starting_bid="Starting bid amount",
        duration_hours="Duration in hours (1-48)",
        bin_price="Buy it now price (optional)"
    )
    async def ah_create(self, interaction: discord.Interaction, item_id: str, starting_bid: int, duration_hours: int, bin_price: int = 0):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        item = await self.bot.game_data.get_item(item_id)
        if not item:
            await interaction.followup.send("❌ Invalid item ID!", ephemeral=True)
            return
        
        if duration_hours < 1 or duration_hours > 48:
            await interaction.followup.send("❌ Duration must be between 1 and 48 hours!", ephemeral=True)
            return
        
        item_count = await self.bot.db.get_item_count(interaction.user.id, item_id)
        if item_count < 1:
            await interaction.followup.send(f"❌ You don't have any {item.name}!", ephemeral=True)
            return
        
        await self.bot.db.remove_item_from_inventory(interaction.user.id, item_id, 1)
        
        duration_seconds = duration_hours * 3600
        auction_id = await self.bot.db.create_auction(
            interaction.user.id, item_id, {'count': 1}, starting_bid, duration_seconds, bin_price if bin_price > 0 else None
        )
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_auction_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_auction_date=int(time.time())
            )
        
        embed = discord.Embed(
            title="✅ Auction Created!",
            description=f"Your {item.name} is now listed!",
            color=discord.Color.green()
        )
        embed.add_field(name="Starting Bid", value=f"{starting_bid:,} coins", inline=True)
        embed.add_field(name="Duration", value=f"{duration_hours} hours", inline=True)
        if bin_price > 0:
            embed.add_field(name="BIN Price", value=f"{bin_price:,} coins", inline=True)
        embed.add_field(name="Auction ID", value=f"#{auction_id}", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @ah_create.autocomplete('item_id')
    async def ah_create_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            inventory = await self.bot.db.get_inventory(interaction.user.id)
            
            if not inventory:
                return []
            
            from collections import defaultdict
            item_counts = defaultdict(int)
            for item_data in inventory:
                item_counts[item_data['item_id']] += 1
            
            choices = []
            for item_id, count in item_counts.items():
                item = await self.bot.game_data.get_item(item_id)
                if item and item.type not in ['PET', 'MINION']:
                    if current.lower() in item.name.lower() or current.lower() in item_id.lower():
                        choices.append(
                            app_commands.Choice(
                                name=f"{item.name} (x{count})",
                                value=item_id
                            )
                        )
            
            choices.sort(key=lambda x: x.name)
            return choices[:25]
        except Exception as e:
            print(f"Error in ah_create autocomplete: {e}")
            return []
    
    @app_commands.command(name="ah_browse", description="Browse active auctions")
    async def ah_browse(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        auctions = await self.bot.db.get_active_auctions(20)
        
        embed = discord.Embed(
            title="🔨 Auction House",
            description=f"Showing {len(auctions)} active auctions",
            color=discord.Color.gold()
        )
        
        if not auctions:
            embed.description = "No active auctions! Use `/ah_create` to list an item."
        else:
            for auction in auctions[:10]:
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
                    name=f"#{auction['id']} - {item.name}",
                    value=value,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ah_bid", description="Place a bid on an auction")
    @app_commands.describe(auction_id="The auction ID", bid_amount="Your bid amount")
    async def ah_bid(self, interaction: discord.Interaction, auction_id: int, bid_amount: int):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if player['coins'] < bid_amount:
            await interaction.followup.send(f"❌ Not enough coins! You need {bid_amount:,} coins.", ephemeral=True)
            return
        
        await self.bot.db.update_player(interaction.user.id, coins=player['coins'] - bid_amount)
        
        success = await self.bot.db.place_bid(interaction.user.id, auction_id, bid_amount)
        
        if not success:
            await self.bot.db.update_player(interaction.user.id, coins=player['coins'])
            await interaction.followup.send("❌ Failed to place bid! Auction may have ended or your bid is too low.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ Bid Placed!",
            description=f"You bid {bid_amount:,} coins on auction #{auction_id}",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ah_bin", description="Buy an auction instantly")
    @app_commands.describe(auction_id="The auction ID to buy")
    async def ah_bin(self, interaction: discord.Interaction, auction_id: int):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        success = await self.bot.db.buy_bin(interaction.user.id, auction_id, 0)
        
        if not success:
            await interaction.followup.send("❌ Failed to buy! Auction may not be a BIN or you don't have enough coins.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ Purchase Complete!",
            description=f"You bought auction #{auction_id}!",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ah_my", description="View your auctions")
    async def ah_my(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        auctions = await self.bot.db.get_user_auctions(interaction.user.id)
        
        embed = discord.Embed(
            title=f"📜 {interaction.user.name}'s Auctions",
            description=f"You have {len(auctions)} active auctions",
            color=discord.Color.blue()
        )
        
        if not auctions:
            embed.description = "No active auctions! Use `/ah_create` to list an item."
        else:
            for auction in auctions:
                item = await self.bot.game_data.get_item(auction['item_id'])
                if not item:
                    continue
                
                time_left = auction['end_time'] - int(time.time())
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                
                value = f"Current Bid: {auction['current_bid']:,} coins\n"
                value += f"Ends in: {hours}h {minutes}m"
                
                embed.add_field(
                    name=f"#{auction['id']} - {item.name}",
                    value=value,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuctionCommands(bot))
