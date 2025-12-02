import discord
from discord.ext import commands
from discord import app_commands
from utils.autocomplete import item_autocomplete
from utils.systems.economy_system import EconomySystem

class BazaarBuyModal(discord.ui.Modal, title="Buy from Bazaar"):
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to buy", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid amount!", ephemeral=True)
            return
        
        result = await EconomySystem.instant_buy_bazaar(self.bot.db, interaction.user.id, self.item_id.value, amount)
        
        if result['success']:
            embed = discord.Embed(title="✅ Purchase Successful!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{amount}x {self.item_id.value.replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Total Cost", value=f"{result['total_cost']:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Transaction failed')}", ephemeral=True)

class BazaarSellModal(discord.ui.Modal, title="Sell to Bazaar"):
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to sell", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid amount!", ephemeral=True)
            return
        
        result = await EconomySystem.instant_sell_bazaar(self.bot.db, interaction.user.id, self.item_id.value, amount)
        
        if result['success']:
            embed = discord.Embed(title="✅ Sale Successful!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{amount}x {self.item_id.value.replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Total Value", value=f"{result['total_value']:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Transaction failed')}", ephemeral=True)

class BazaarOrderModal(discord.ui.Modal, title="Place Bazaar Order"):
    order_type = discord.ui.TextInput(label="Order Type (BUY or SELL)", placeholder="BUY or SELL", required=True)
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    price = discord.ui.TextInput(label="Price per item", placeholder="Enter price", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value)
            price = float(self.price.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid amount or price!", ephemeral=True)
            return
        
        order_type = self.order_type.value.upper()
        if order_type not in ['BUY', 'SELL']:
            await interaction.followup.send("❌ Order type must be BUY or SELL!", ephemeral=True)
            return
        
        result = await EconomySystem.create_bazaar_order(self.bot.db, interaction.user.id, self.item_id.value, order_type, amount, price)
        
        if result['success']:
            embed = discord.Embed(title="✅ Order Placed!", color=discord.Color.green())
            embed.add_field(name="Type", value=order_type, inline=True)
            embed.add_field(name="Item", value=f"{amount}x {self.item_id.value.replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Price", value=f"{price:.1f} coins each", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Order failed')}", ephemeral=True)

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

class BazaarMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.page = 0
        self.items_per_page = 10
        self.items_list = []
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
                buy_price = base * 1.1
                sell_price = base * 0.9
            
            self.items_list.append({
                "name": item.get("name"),
                "id": item_id,
                "buy_price": buy_price,
                "sell_price": sell_price
            })
        
        self.items_list.sort(key=lambda x: x["buy_price"])
    
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
            title="🏪 Bazaar Items",
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
                inline=True
            )
        
        total_pages = (len(self.items_list) + self.items_per_page - 1) // self.items_per_page if self.items_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    async def get_orders_embed(self):
        orders = await self.bot.db.get_user_bazaar_orders(self.user_id)
        
        embed = discord.Embed(
            title=f"📊 Your Bazaar Orders",
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
        
        return embed
    
    @discord.ui.button(label="🏠 Main", style=discord.ButtonStyle.blurple, row=0)
    async def main_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'main'
        self.page = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="📋 Browse", style=discord.ButtonStyle.green, row=0)
    async def browse_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'browse'
        self.page = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="📊 My Orders", style=discord.ButtonStyle.gray, row=0)
    async def orders_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'orders'
        self.page = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.browse_button)
        self.add_item(self.orders_button)
        
        if self.current_view == 'browse' and self.items_list:
            total_pages = (len(self.items_list) + self.items_per_page - 1) // self.items_per_page
            if total_pages > 1:
                self.add_item(self.prev_button)
                self.add_item(self.next_button)
        
        self.add_item(self.buy_button)
        self.add_item(self.sell_button)
        self.add_item(self.order_button)
        self.add_item(self.cancel_button)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            self._update_buttons()
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.current_view == 'browse' and self.items_list:
            total_pages = (len(self.items_list) + self.items_per_page - 1) // self.items_per_page
            if self.page < total_pages - 1:
                self.page += 1
                self._update_buttons()
                await interaction.response.edit_message(embed=await self.get_embed(), view=self)
                return
        
        await interaction.response.defer()
    
    @discord.ui.button(label="💰 Buy", style=discord.ButtonStyle.green, row=2)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarBuyModal(self.bot))
    
    @discord.ui.button(label="💸 Sell", style=discord.ButtonStyle.red, row=2)
    async def sell_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarSellModal(self.bot))
    
    @discord.ui.button(label="📝 Order", style=discord.ButtonStyle.blurple, row=2)
    async def order_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarOrderModal(self.bot))
    
    @discord.ui.button(label="❌ Cancel Order", style=discord.ButtonStyle.gray, row=2)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarCancelModal(self.bot))

class BazaarCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bazaar", description="Access the Bazaar with all features")
    async def bazaar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = BazaarMenuView(self.bot, interaction.user.id)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BazaarCommands(bot))
