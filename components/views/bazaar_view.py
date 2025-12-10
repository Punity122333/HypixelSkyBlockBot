import discord
from components.buttons.bazaar_buttons import (
    BazaarSearchButton,
    BazaarMainButton,
    BazaarBrowseButton,
    BazaarOrdersButton,
    BazaarPreviousButton,
    BazaarNextButton,
    BazaarBuyButton,
    BazaarSellButton,
    BazaarOrderButton,
    BazaarCancelButton
)

class BazaarMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.page = 0
        self.items_per_page = 5
        self.items_list = []
        self.orders_list = []
        
        self.main_button = BazaarMainButton(self)
        self.browse_button = BazaarBrowseButton(self)
        self.orders_button = BazaarOrdersButton(self)
        self.prev_button = BazaarPreviousButton(self)
        self.next_button = BazaarNextButton(self)
        self.buy_button = BazaarBuyButton(self)
        self.sell_button = BazaarSellButton(self)
        self.order_button = BazaarOrderButton(self)
        self.cancel_button = BazaarCancelButton(self)
        
        self._update_buttons()
    
    async def load_items(self):
        all_items = await self.bot.game_data.get_all_items()
        bazaar_products = await self.bot.db.get_all_bazaar_products()
        bazaar_dict = {p['product_id']: p for p in bazaar_products}
        
        self.items_list = []
        for item in all_items:
            item_id = item.get("item_id")
            item_type = item.get("type")
            
            if item_type in ["PET", "MINION"]:
                continue
            name = item.get("name", "")
            if "from" in name.lower():
                continue
            
            if item_id in bazaar_dict:
                product = bazaar_dict[item_id]
                buy_price = product["buy_price"]
                sell_price = product["sell_price"]
            else:
                base = item.get("default_bazaar_price", 0)
                if base <= 0:
                    continue
                buy_price = base * 1.1
                sell_price = base * 0.9
            
            self.items_list.append({
                "name": item.get("name"),
                "id": item_id,
                "buy_price": buy_price,
                "sell_price": sell_price
            })
        
        self.items_list.sort(key=lambda x: x["buy_price"])
        
    async def load_orders(self):
        orders = await self.bot.db.get_user_bazaar_orders(self.user_id)
        
        product_ids = {o['product_id'] for o in orders}
        item_names = {}
        for product_id in product_ids:
            item = await self.bot.game_data.get_item(product_id)
            if item:
                item_names[product_id] = item.name
            else:
                item_names[product_id] = product_id.replace('_', ' ').title()
            
        self.orders_list = []
        for order in orders:
            order['item_name'] = item_names[order['product_id']]
            self.orders_list.append(order)
            
        self.orders_list.sort(key=lambda x: (x['order_type'] != 'BUY', x['id']))

    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'browse':
            return await self.get_browse_embed()
        elif self.current_view == 'orders':
            return await self.get_orders_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        orders = await self.bot.db.get_user_bazaar_orders(self.user_id)
        
        embed = discord.Embed(
            title="🏪 Bazaar",
            description="Trade items instantly or place orders",
            color=discord.Color.gold()
        )
        
        if orders:
            buy_orders = [o for o in orders if o['order_type'] == 'BUY']
            sell_orders = [o for o in orders if o['order_type'] == 'SELL']
            embed.add_field(name="Active Orders", value=f"{len(buy_orders)} Buy | {len(sell_orders)} Sell", inline=False)
        else:
            embed.add_field(name="Active Orders", value="No active orders", inline=False)
        
        embed.set_footer(text="Use buttons below to interact with the bazaar")
        return embed
    
    async def get_browse_embed(self):
        if not self.items_list:
            await self.load_items()
        
        embed = discord.Embed(
            title="📋 Bazaar Items",
            description="Available items on the bazaar",
            color=discord.Color.gold()
        )
        
        start = self.page * self.items_per_page
        end = min(start + self.items_per_page, len(self.items_list))
        page_items = self.items_list[start:end]
        
        for item_data in page_items:
            name = item_data["name"]
            buy = item_data["buy_price"]
            sell = item_data["sell_price"]
            item_id = item_data["id"]
            embed.add_field(
                name=name,
                value=f"Buy: {buy:.1f} | Sell: {sell:.1f}\n`{item_id}`",
                inline=False
            )
        
        total_pages = (len(self.items_list) + self.items_per_page - 1) // self.items_per_page if self.items_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    async def get_orders_embed(self):
        if not self.orders_list:
            await self.load_orders()
        
        embed = discord.Embed(
            title=f"📊 Your Bazaar Orders",
            description=f"You have {len(self.orders_list)} active orders",
            color=discord.Color.blue()
        )
        
        if not self.orders_list:
            embed.description = "No active orders!"
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.orders_list))
            page_orders = self.orders_list[start:end]
            
            buy_text = ""
            sell_text = ""
            
            for order in page_orders:
                line = f"#{order['id']}: {order['amount']}x {order['item_name']} @ **{order['price']:.1f}** each\n"
                if order['order_type'] == 'BUY':
                    buy_text += line
                elif order['order_type'] == 'SELL':
                    sell_text += line
            
            if buy_text:
                embed.add_field(name="💵 Buy Orders (Page)", value=buy_text, inline=False)
            
            if sell_text:
                embed.add_field(name="💸 Sell Orders (Page)", value=sell_text, inline=False)
        
        total_pages = (len(self.orders_list) + self.items_per_page - 1) // self.items_per_page if self.orders_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.browse_button)
        self.add_item(self.orders_button)
        
        data_list = []
        if self.current_view == 'browse':
            data_list = self.items_list
        elif self.current_view == 'orders':
            data_list = self.orders_list
            
        if data_list:
            total_pages = (len(data_list) + self.items_per_page - 1) // self.items_per_page
            if total_pages > 1:
                self.add_item(self.prev_button)
                self.add_item(self.next_button)
        
        self.add_item(self.buy_button)
        self.add_item(self.sell_button)
        self.add_item(self.order_button)
        self.add_item(self.cancel_button)
        self.add_item(BazaarSearchButton(self))