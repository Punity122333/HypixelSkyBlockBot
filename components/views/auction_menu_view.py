import discord
import time
from components.buttons.auction_buttons import (
    AuctionCreateButton,
    AuctionBidButton,
    AuctionBINButton,
    AuctionBrowseButton,
    AuctionMyAuctionsButton,
    AuctionPreviousButton,
    AuctionNextButton
)

class AuctionMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.auctions = []
        self.current_view = 'browse'
        
        self.add_item(AuctionBrowseButton(self))
        self.add_item(AuctionMyAuctionsButton(self))
        self.add_item(AuctionPreviousButton(self))
        self.add_item(AuctionNextButton(self))
        self.add_item(AuctionCreateButton(self))
        self.add_item(AuctionBidButton(self))
        self.add_item(AuctionBINButton(self))
    
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