import discord
from components.buttons.economy_buttons import (
    EconomyMainButton,
    EconomyFlipsButton,
    EconomyTrendsButton,
    EconomyAuctionsButton,
    EconomyStocksButton,
    EconomyPreviousButton,
    EconomyNextButton
)

class EconomyMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.page = 0
        self.items_per_page = 5
        
        self.main_button = EconomyMainButton(self)
        self.flips_button = EconomyFlipsButton(self)
        self.trends_button = EconomyTrendsButton(self)
        self.auctions_button = EconomyAuctionsButton(self)
        self.stocks_button = EconomyStocksButton(self)
        self.prev_button = EconomyPreviousButton(self)
        self.next_button = EconomyNextButton(self)
        
        self._update_buttons()
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'flips':
            return await self.get_flips_embed()
        elif self.current_view == 'trends':
            return await self.get_trends_embed()
        elif self.current_view == 'auctions':
            return await self.get_auctions_embed()
        elif self.current_view == 'stocks':
            return await self.get_stocks_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        player = await self.bot.db.get_player(self.user_id)
        
        embed = discord.Embed(
            title="🌐 SkyBlock Economy Overview",
            description="Complete economic statistics",
            color=discord.Color.gold()
        )
        
        if player:
            embed.add_field(
                name="💰 Your Balance",
                value=f"{player.get('coins', 0):,} coins\nBank: {player.get('bank', 0):,} coins",
                inline=True
            )
            
            total_wealth = player.get('coins', 0) + player.get('bank', 0)
            embed.add_field(
                name="💎 Net Worth",
                value=f"{total_wealth:,} coins",
                inline=True
            )
            
            trading_rep = player.get('trading_reputation', 0)
            merchant_level = player.get('merchant_level', 1)
            embed.add_field(
                name="📊 Trading Stats",
                value=f"Rep: {trading_rep}\nMerchant Level: {merchant_level}",
                inline=True
            )
        
        stocks = await self.bot.db.get_all_stocks()
        total_market_cap = sum(s.get('market_cap', 0) for s in stocks) if stocks else 0
        embed.add_field(
            name="📈 Stock Market",
            value=f"Total Market Cap: {total_market_cap:,} coins\n{len(stocks)} listed companies",
            inline=True
        )
        
        auctions = await self.bot.db.get_active_auctions(1000)
        total_auction_volume = sum(a.get('current_bid', 0) for a in auctions) if auctions else 0
        embed.add_field(
            name="🔨 Auction House",
            value=f"{len(auctions)} active auctions\n{total_auction_volume:,} coins in bids",
            inline=True
        )
        
        deals = await self.bot.db.get_active_merchant_deals()
        embed.add_field(
            name="🏪 Merchant Deals",
            value=f"{len(deals)} active deals",
            inline=True
        )
        
        embed.set_footer(text="Use buttons below to view detailed statistics")
        return embed
    
    async def get_flips_embed(self):
        player = await self.bot.db.get_player(self.user_id)
        
        embed = discord.Embed(
            title="💹 Bazaar Flip Statistics",
            description="Your bazaar flipping performance",
            color=discord.Color.gold()
        )
        
        if player:
            embed.add_field(
                name="Total Earned",
                value=f"{player.get('total_earned', 0):,} coins",
                inline=True
            )
            embed.add_field(
                name="Total Spent",
                value=f"{player.get('total_spent', 0):,} coins",
                inline=True
            )
            net = player.get('total_earned', 0) - player.get('total_spent', 0)
            embed.add_field(
                name="Net Profit",
                value=f"{net:,} coins",
                inline=True
            )
        
        top_flippers = await self.bot.db.get_top_flippers(10)
        
        if top_flippers:
            leaderboard = ""
            for i, flipper in enumerate(top_flippers[:10], 1):
                user_id = flipper.get('user_id')
                profit = flipper.get('total_profit', 0)
                if user_id == self.user_id:
                    leaderboard += f"**{i}. You - {profit:,} coins**\n"
                else:
                    leaderboard += f"{i}. <@{user_id}> - {profit:,} coins\n"
            
            embed.add_field(
                name="🏆 Top Flippers",
                value=leaderboard or "No data yet",
                inline=False
            )
        
        embed.set_footer(text="Keep flipping to climb the leaderboard!")
        return embed
    
    async def get_trends_embed(self):
        embed = discord.Embed(
            title="📊 Market Trends Analysis",
            description="Current supply and demand trends",
            color=discord.Color.blue()
        )
        
        rising_items = []
        falling_items = []
        
        if hasattr(self.bot, 'market_system') and self.bot.market_system.supply_demand:
            for item_id, sd in self.bot.market_system.supply_demand.items():
                if sd.get('trend') == 'rising':
                    ratio = sd.get('demand', 1.0) / sd.get('supply', 1.0)
                    rising_items.append((item_id, ratio))
                elif sd.get('trend') == 'falling':
                    ratio = sd.get('demand', 1.0) / sd.get('supply', 1.0)
                    falling_items.append((item_id, ratio))
            
            rising_items.sort(key=lambda x: x[1], reverse=True)
            falling_items.sort(key=lambda x: x[1])
        
        if rising_items:
            rising_text = ""
            for item_id, ratio in rising_items[:5]:
                item_name = item_id.replace('_', ' ').title()
                rising_text += f"📈 {item_name} (D/S: {ratio:.2f})\n"
            embed.add_field(name="Rising Items", value=rising_text, inline=False)
        
        if falling_items:
            falling_text = ""
            for item_id, ratio in falling_items[:5]:
                item_name = item_id.replace('_', ' ').title()
                falling_text += f"📉 {item_name} (D/S: {ratio:.2f})\n"
            embed.add_field(name="Falling Items", value=falling_text, inline=False)
        
        if not rising_items and not falling_items:
            embed.add_field(
                name="No Data",
                value="Market trends will appear as trades occur",
                inline=False
            )
        
        embed.set_footer(text="Buy low, sell high! Use trends to maximize profits.")
        return embed
    
    async def get_auctions_embed(self):
        embed = discord.Embed(
            title="🔨 Auction House Insights",
            description="Real-time auction market analysis",
            color=discord.Color.purple()
        )
        
        auctions = await self.bot.db.get_active_auctions(100)
        
        total_volume = sum(a.get('current_bid', 0) for a in auctions) if auctions else 0
        avg_price = total_volume / len(auctions) if auctions else 0
        
        embed.add_field(name="Active Auctions", value=str(len(auctions)), inline=True)
        embed.add_field(name="Total Volume", value=f"{total_volume:,} coins", inline=True)
        embed.add_field(name="Avg Price", value=f"{int(avg_price):,} coins", inline=True)
        
        bin_auctions = [a for a in auctions if a.get('bin')]
        embed.add_field(name="BIN Listings", value=str(len(bin_auctions)), inline=True)
        
        auction_bots = await self.bot.db.get_auction_bots()
        embed.add_field(name="Active Bot Traders", value=str(len(auction_bots)), inline=True)
        
        if auction_bots:
            bot_info = "**Trading Bots:**\n"
            for bot in auction_bots[:5]:
                bot_name = bot.get('bot_name', 'Unknown')
                trades = bot.get('trades_completed', 0)
                bot_info += f"🤖 {bot_name} - {trades} trades\n"
            embed.add_field(name="Bot Activity", value=bot_info, inline=False)
        
        embed.set_footer(text="Bot traders compete in the market just like players!")
        return embed
    
    async def get_stocks_embed(self):
        embed = discord.Embed(
            title="📈 Stock Market Overview",
            description="Your portfolio and market performance",
            color=discord.Color.green()
        )
        
        player_stocks = await self.bot.db.get_player_stocks(self.user_id)
        
        if player_stocks:
            portfolio_value = 0
            stocks_text = ""
            
            for stock in player_stocks[:10]:
                symbol = stock.get('stock_symbol', stock.get('symbol', 'N/A'))
                shares = stock.get('shares', 0)
                current_price = stock.get('current_price', 0)
                value = shares * current_price
                portfolio_value += value
                
                stocks_text += f"**{symbol}**: {shares} shares @ {current_price:.2f} = {value:,.0f} coins\n"
            
            embed.add_field(
                name=f"Your Portfolio ({len(player_stocks)} stocks)",
                value=stocks_text or "No stocks owned",
                inline=False
            )
            
            embed.add_field(
                name="Portfolio Value",
                value=f"{portfolio_value:,} coins",
                inline=True
            )
        else:
            embed.add_field(
                name="Your Portfolio",
                value="No stocks owned yet. Use `/stocks` to buy!",
                inline=False
            )
        
        all_stocks = await self.bot.db.get_all_stocks()
        if all_stocks:
            market_text = ""
            for stock in all_stocks[:5]:
                symbol = stock.get('symbol', 'N/A')
                company = stock.get('company_name', 'Unknown')
                price = stock.get('current_price', 0)
                change = stock.get('change_percent', 0)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➖"
                market_text += f"{emoji} **{symbol}** ({company}): {price:.2f} ({change:+.1f}%)\n"
            
            embed.add_field(
                name="Market Overview",
                value=market_text,
                inline=False
            )
        
        embed.set_footer(text="Trade stocks with /stocks command")
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.flips_button)
        self.add_item(self.trends_button)
        self.add_item(self.auctions_button)
        self.add_item(self.stocks_button)
