import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
from typing import List, Dict

class BazaarPaginationView(discord.ui.View):
    def __init__(self, items_list: List[Dict], items_per_page: int = 24):
        super().__init__(timeout=180)
        self.items_list = items_list
        self.items_per_page = items_per_page
        self.current_page = 0
        self.max_page = (len(items_list) - 1) // items_per_page
        
    def get_page_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="🏪 Bazaar Items",
            description="Available items on the bazaar",
            color=discord.Color.gold()
        )
        
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.items_list))
        
        for item_data in self.items_list[start_idx:end_idx]:
            price_indicator = "📊" if item_data['source'] == "live" else "🏷️"
            embed.add_field(
                name=f"{price_indicator} {item_data['name']}",
                value=f"Buy: {item_data['buy_price']:.1f}\nSell: {item_data['sell_price']:.1f}",
                inline=True
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.max_page + 1} | Showing {start_idx + 1}-{end_idx} of {len(self.items_list)} items | 📊 = Live Price | 🏷️ = Default Price")
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.primary, custom_id="prev_page")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary, custom_id="next_page")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_page:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.defer()

class BazaarCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bz_prices", description="View bazaar prices for an item")
    @app_commands.describe(item_id="The item ID to check")
    async def bz_prices(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer()
        
        item = await self.bot.game_data.get_item(item_id)
        if not item:
            await interaction.followup.send("❌ Invalid item ID!", ephemeral=True)
            return
        
        product = await self.bot.db.get_bazaar_product(item_id)
        
        if not product:
            await interaction.followup.send("❌ This item is not on the bazaar!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🏪 {item.name}",
            description="Current Bazaar Prices",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="💵 Buy Price", value=f"{product['buy_price']:.1f} coins", inline=True)
        embed.add_field(name="💸 Sell Price", value=f"{product['sell_price']:.1f} coins", inline=True)
        embed.add_field(name="📊 Spread", value=f"{(product['buy_price'] - product['sell_price']):.1f} coins", inline=True)
        
        embed.add_field(name="📈 Buy Orders", value=f"{product['buy_volume']:,}", inline=True)
        embed.add_field(name="📉 Sell Orders", value=f"{product['sell_volume']:,}", inline=True)
        embed.add_field(name="🏷️ Base Price", value=f"{item.default_bazaar_price:.1f} coins", inline=True)
        
        history = await self.bot.db.get_market_history(item_id, 10)
        if history:
            avg_price = sum(h['price'] for h in history) / len(history)
            embed.add_field(name="📊 Avg Price (10)", value=f"{avg_price:.1f} coins", inline=True)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="bz_buy", description="Instantly buy items from bazaar")
    @app_commands.describe(item_id="Item to buy", amount="Amount to buy")
    async def bz_buy(self, interaction: discord.Interaction, item_id: str, amount: int):
        item_id = item_id.lower().replace(" ", "_")
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        success, message = await self.bot.market_system.instant_buy(interaction.user.id, item_id, amount)
        
        if success:
            item_obj = await self.bot.game_data.get_item(item_id)
            item_name = item_obj.name if item_obj and getattr(item_obj, "name", None) else item_id.replace("_", " ").title()
            item_name = f"**{item_name}**"
            embed = discord.Embed(
                title=f"✅ Purchase Complete!",
                description=f"You bought **{amount}x** {item_name} from the bazaar.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Purchase Failed!",
                description=message,
                color=discord.Color.red()
            )
        await interaction.followup.send(embed=embed, ephemeral=not success)
    
    @app_commands.command(name="bz_sell", description="Instantly sell items to bazaar")
    @app_commands.describe(item_id="Item to sell", amount="Amount to sell")
    async def bz_sell(self, interaction: discord.Interaction, item_id: str, amount: int):
        item_id = item_id.lower().replace(" ", "_")
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        success, message = await self.bot.market_system.instant_sell(interaction.user.id, item_id, amount)
        
        if success:
            item_obj = await self.bot.game_data.get_item(item_id)
            item_name = item_obj.name if item_obj and getattr(item_obj, "name", None) else item_id.replace("_", " ").title()
            item_name = f"**{item_name}**"
            embed = discord.Embed(
                title="✅ Sale Complete!",
                description=f"You sold **{amount}x** {item_name} to the bazaar.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Sale Failed!",
                description=message,
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=not success)
    
    @app_commands.command(name="bz_order_buy", description="Place a buy order")
    @app_commands.describe(item_id="Item to buy", price="Price per item", amount="Amount to buy")
    async def bz_order_buy(self, interaction: discord.Interaction, item_id: str, price: float, amount: int):
        item_id = item_id.lower().replace(" ", "_")
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        item = await self.bot.game_data.get_item(item_id)
        if not item:
            await interaction.followup.send("❌ Invalid item ID!", ephemeral=True)
            return
        
        item_name = item.name if getattr(item, "name", None) else item_id.replace("_", " ").title()
        item_name = f"**{item_name}**"
        success, message = await self.bot.market_system.create_buy_order(interaction.user.id, item_id, price, amount)
        
        if success:
            embed = discord.Embed(
                title="✅ Buy Order Created!",
                description=f"You placed a buy order for **{amount}x** {item_name} at {price:.1f} coins each.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Order Failed!",
                description=message,
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=not success)
    
    @app_commands.command(name="bz_order_sell", description="Place a sell order")
    @app_commands.describe(item_id="Item to sell", price="Price per item", amount="Amount to sell")
    async def bz_order_sell(self, interaction: discord.Interaction, item_id: str, price: float, amount: int):
        await interaction.response.defer()
        item_id = item_id.lower().replace(" ", "_")
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        item = await self.bot.game_data.get_item(item_id)
        if not item:
            await interaction.followup.send("❌ Invalid item ID!", ephemeral=True)
            return
        
        item_name = item.name if getattr(item, "name", None) else item_id.replace("_", " ").title()
        item_name = f"**{item_name}**"
        success, message = await self.bot.market_system.create_sell_order(interaction.user.id, item_id, price, amount)
        
        if success:
            embed = discord.Embed(
                title="✅ Sell Order Created!",
                description=f"You placed a sell order for **{amount}x** {item_name} at {price:.1f} coins each.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Order Failed!",
                description=message,
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=not success)
    
    @app_commands.command(name="bz_myorders", description="View your active orders")
    async def bz_myorders(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        orders = await self.bot.db.get_user_bazaar_orders(interaction.user.id)
        
        embed = discord.Embed(
            title=f"📊 {interaction.user.name}'s Bazaar Orders",
            description=f"You have {len(orders)} active orders",
            color=discord.Color.blue()
        )
        
        if not orders:
            embed.description = "No active orders!"
        else:
            buy_orders = [o for o in orders if o['order_type'] == 'BUY']
            sell_orders = [o for o in orders if o['order_type'] == 'SELL']
            
            if buy_orders:
                buy_text = ""
                for order in buy_orders[:5]:
                    item = await self.bot.game_data.get_item(order['product_id'])
                    if item:
                        buy_text += f"#{order['id']}: {order['amount']}x {item.name} @ **{order['price']:.1f}** each\n"
                if buy_text:
                    embed.add_field(name="💵 Buy Orders", value=buy_text, inline=False)
            
            if sell_orders:
                sell_text = ""
                for order in sell_orders[:5]:
                    item = await self.bot.game_data.get_item(order['product_id'])
                    if item:
                        sell_text += f"#{order['id']}: {order['amount']}x {item.name} @ **{order['price']:.1f}** each\n"
                if sell_text:
                    embed.add_field(name="💸 Sell Orders", value=sell_text, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="bz_cancel", description="Cancel an order")
    @app_commands.describe(order_id="The order ID to cancel")
    async def bz_cancel(self, interaction: discord.Interaction, order_id: int):
        await interaction.response.defer()
        
        await self.bot.db.cancel_bazaar_order(order_id)
        
        embed = discord.Embed(
            title="✅ Order Cancelled!",
            description=f"Order #{order_id} has been cancelled",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="bz_list", description="List bazaar items")
    async def bz_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Get all items from database (now dicts)
        all_items = await self.bot.game_data.get_all_items()

        # Get all bazaar products
        bazaar_products = await self.bot.db.get_all_bazaar_products()
        bazaar_dict = {p['product_id']: p for p in bazaar_products}

        items_list = []
        for item in all_items:
            item_id = item.get("item_id")
            item_type = item.get("type")

            # skip non-tradeables
            if item_type in ["PET", "MINION"]:
                continue
            name = item.get("name", "")
            if "from" in name.lower():
                continue

            # bazaar live prices
            if item_id in bazaar_dict:
                product = bazaar_dict[item_id]
                buy_price = product["buy_price"]
                sell_price = product["sell_price"]
                price_source = "live"
            else:
                # fallback
                base = item.get("default_bazaar_price", 0)
                buy_price = base * 1.1
                sell_price = base * 0.9
                price_source = "default"

            items_list.append({
                "name": item.get("name"),
                "id": item_id,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "source": price_source
            })

        # sort by buy price
        items_list.sort(key=lambda x: x["buy_price"])

        # send paginated embed
        if items_list:
            view = BazaarPaginationView(items_list)
            await interaction.followup.send(embed=view.get_page_embed(), view=view)
        else:
            embed = discord.Embed(
                title="🏪 Bazaar Items",
                description="No items available on the bazaar",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BazaarCommands(bot))
