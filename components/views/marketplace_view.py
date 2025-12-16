import discord
from discord.ui import Button, View, Select, Modal, TextInput
from components.views.trade_view import TradeView


class TradeUserModal(Modal, title="Start Trade"):
    user_id = TextInput(
        label="User ID",
        placeholder="Enter the Discord User ID to trade with",
        required=True,
        max_length=20
    )
    
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            target_user_id = int(self.user_id.value)
            
            if target_user_id == interaction.user.id:
                await interaction.response.send_message("❌ You can't trade with yourself!", ephemeral=True)
                return
            
            try:
                user = await interaction.client.fetch_user(target_user_id)
            except:
                await interaction.response.send_message("❌ User not found!", ephemeral=True)
                return
            
            if user.bot:
                await interaction.response.send_message("❌ You can't trade with bots!", ephemeral=True)
                return
            
            await self.view.bot.player_manager.get_or_create_player(
                interaction.user.id, interaction.user.name
            )
            await self.view.bot.player_manager.get_or_create_player(
                user.id, user.name
            )
            
            trade_id = await self.view.bot.db.trading.create_trade(interaction.user.id, user.id)
            
            trade_view = TradeView(self.view.bot, trade_id, interaction.user.id, user.id, interaction.user.name, user.name)
            embed = await trade_view.get_trade_embed()
            
            await interaction.response.send_message(f"{user.mention} You have a trade request!", embed=embed, view=trade_view)
        except ValueError:
            await interaction.response.send_message("❌ Invalid User ID!", ephemeral=True)


class MarketplaceView(View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'history':
            return await self.get_history_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        stats = await self.bot.db.trading.get_trading_stats(self.user_id)
        
        reputation = stats['trading_reputation']
        if reputation == 0:
            rep_level = "New Trader 🆕"
            rep_desc = "Complete your first trade!"
        elif reputation < 10:
            rep_level = "Beginner Trader 🌱"
            rep_desc = f"{10 - reputation} trades to Experienced"
        elif reputation < 50:
            rep_level = "Experienced Trader 💼"
            rep_desc = f"{50 - reputation} trades to Expert"
        elif reputation < 100:
            rep_level = "Expert Trader 🏆"
            rep_desc = f"{100 - reputation} trades to Master"
        elif reputation < 250:
            rep_level = "Master Trader 👑"
            rep_desc = f"{250 - reputation} trades to Legend"
        else:
            rep_level = "Legendary Trader ⭐"
            rep_desc = "Maximum reputation achieved!"
        
        embed = discord.Embed(
            title="🏪 Marketplace",
            description="Trade with other players and view your trading stats",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="🏅 Reputation Level", value=rep_level, inline=False)
        embed.add_field(name="📊 Reputation Points", value=f"{reputation} ({rep_desc})", inline=False)
        
        embed.add_field(name="📦 Total Trades", value=str(stats['total_trades']), inline=True)
        embed.add_field(name="💰 Coins Traded", value=f"{stats['total_coins_traded']:,}", inline=True)
        
        if stats['total_trades'] > 0:
            avg_coins = stats['total_coins_traded'] // stats['total_trades']
            embed.add_field(name="📈 Avg Per Trade", value=f"{avg_coins:,} coins", inline=True)
        
        embed.set_footer(text="Use buttons below to interact with the marketplace")
        return embed
    
    async def get_history_embed(self):
        history = await self.bot.db.trading.get_trade_history(self.user_id, 10)
        stats = await self.bot.db.trading.get_trading_stats(self.user_id)
        
        reputation = stats['trading_reputation']
        if reputation == 0:
            rep_level = "New Trader 🆕"
            rep_desc = "Complete your first trade!"
        elif reputation < 10:
            rep_level = "Beginner Trader 🌱"
            rep_desc = f"{10 - reputation} trades to Experienced"
        elif reputation < 50:
            rep_level = "Experienced Trader 💼"
            rep_desc = f"{50 - reputation} trades to Expert"
        elif reputation < 100:
            rep_level = "Expert Trader 🏆"
            rep_desc = f"{100 - reputation} trades to Master"
        elif reputation < 250:
            rep_level = "Master Trader 👑"
            rep_desc = f"{250 - reputation} trades to Legend"
        else:
            rep_level = "Legendary Trader ⭐"
            rep_desc = "Maximum reputation achieved!"
        
        embed = discord.Embed(
            title="📜 Trade History & Reputation",
            description=f"Your trading profile and recent activity",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="🏅 Reputation Level", value=rep_level, inline=False)
        embed.add_field(name="📊 Reputation Points", value=f"{reputation} ({rep_desc})", inline=False)
        
        embed.add_field(name="📦 Total Trades", value=str(stats['total_trades']), inline=True)
        embed.add_field(name="💰 Coins Traded", value=f"{stats['total_coins_traded']:,}", inline=True)
        
        if stats['total_trades'] > 0:
            avg_coins = stats['total_coins_traded'] // stats['total_trades']
            embed.add_field(name="📈 Avg Per Trade", value=f"{avg_coins:,} coins", inline=True)
        
        if history:
            history_text = []
            for i, trade in enumerate(history[:5], 1):
                other_user_id = trade['receiver_id'] if trade['initiator_id'] == self.user_id else trade['initiator_id']
                timestamp = f"<t:{trade['completed_at']}:R>"
                my_coins = trade['initiator_coins'] if trade['initiator_id'] == self.user_id else trade['receiver_coins']
                their_coins = trade['receiver_coins'] if trade['initiator_id'] == self.user_id else trade['initiator_coins']
                
                trade_summary = []
                if my_coins > 0:
                    trade_summary.append(f"gave {my_coins:,} coins")
                if their_coins > 0:
                    trade_summary.append(f"received {their_coins:,} coins")
                
                summary_text = " & ".join(trade_summary) if trade_summary else "item exchange"
                history_text.append(f"`{i}.` <@{other_user_id}> - {summary_text} {timestamp}")
            
            embed.add_field(
                name="🕐 Recent Trades",
                value="\n".join(history_text),
                inline=False
            )
        else:
            embed.add_field(
                name="🕐 Recent Trades",
                value="No trade history yet. Use 'Start Trade' to start trading!",
                inline=False
            )
        
        embed.set_footer(text="Build your reputation by completing more trades!")
        return embed
    
    @discord.ui.button(label="Start Trade", style=discord.ButtonStyle.primary, emoji="🤝", row=0)
    async def start_trade_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your marketplace!", ephemeral=True)
            return
        
        modal = TradeUserModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Main", style=discord.ButtonStyle.secondary, emoji="🏠", row=0)
    async def main_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your marketplace!", ephemeral=True)
            return
        
        self.current_view = 'main'
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Trade History", style=discord.ButtonStyle.secondary, emoji="📜", row=0)
    async def history_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your marketplace!", ephemeral=True)
            return
        
        self.current_view = 'history'
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
