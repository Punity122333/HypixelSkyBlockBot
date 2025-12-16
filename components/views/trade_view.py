import discord
from discord.ui import Button, View, Select
from typing import Dict, List, Optional
from components.modals.trade_modals import TradeOfferModal, TradeCoinsModal

class TradeView(View):
    def __init__(self, bot, trade_id: int, initiator_id: int, receiver_id: int, initiator_name: str, receiver_name: str):
        super().__init__(timeout=300)
        self.bot = bot
        self.trade_id = trade_id
        self.initiator_id = initiator_id
        self.receiver_id = receiver_id
        self.initiator_name = initiator_name
        self.receiver_name = receiver_name
    
    async def get_trade_embed(self) -> discord.Embed:
        trade = await self.bot.db.trading.get_trade(self.trade_id)
        if not trade:
            return discord.Embed(title="Trade Not Found", color=discord.Color.red())
        
        initiator_items = await self.bot.db.trading.get_trade_items(self.trade_id, self.initiator_id)
        receiver_items = await self.bot.db.trading.get_trade_items(self.trade_id, self.receiver_id)
        
        initiator_stats = await self.bot.db.trading.get_trading_stats(self.initiator_id)
        receiver_stats = await self.bot.db.trading.get_trading_stats(self.receiver_id)
        
        initiator_rep = initiator_stats['trading_reputation']
        receiver_rep = receiver_stats['trading_reputation']
        
        def get_rep_badge(rep):
            if rep == 0:
                return "🆕"
            elif rep < 10:
                return "🌱"
            elif rep < 50:
                return "💼"
            elif rep < 100:
                return "🏆"
            elif rep < 250:
                return "👑"
            else:
                return "⭐"
        
        embed = discord.Embed(
            title="🤝 Player Trade",
            description=f"**{self.initiator_name}** {get_rep_badge(initiator_rep)} ⇄ {get_rep_badge(receiver_rep)} **{self.receiver_name}**",
            color=discord.Color.blue()
        )
        
        initiator_offer = []
        if trade['initiator_coins'] > 0:
            initiator_offer.append(f"💰 {trade['initiator_coins']:,} coins")
        for item in initiator_items:
            initiator_offer.append(f"• {item['item_id']} x{item['amount']}")
        
        receiver_offer = []
        if trade['receiver_coins'] > 0:
            receiver_offer.append(f"💰 {trade['receiver_coins']:,} coins")
        for item in receiver_items:
            receiver_offer.append(f"• {item['item_id']} x{item['amount']}")
        
        initiator_status = "✅ Ready" if trade['initiator_ready'] else "⏳ Not Ready"
        receiver_status = "✅ Ready" if trade['receiver_ready'] else "⏳ Not Ready"
        
        embed.add_field(
            name=f"{self.initiator_name}'s Offer {initiator_status}",
            value=("\n".join(initiator_offer) if initiator_offer else "Nothing offered") + f"\n\n📊 Rep: {initiator_rep} | Trades: {initiator_stats['total_trades']}",
            inline=True
        )
        embed.add_field(
            name=f"{self.receiver_name}'s Offer {receiver_status}",
            value=("\n".join(receiver_offer) if receiver_offer else "Nothing offered") + f"\n\n📊 Rep: {receiver_rep} | Trades: {receiver_stats['total_trades']}",
            inline=True
        )
        
        embed.set_footer(text="Both players must click 'Accept Trade' to complete | Trade safely!")
        return embed
    
    @discord.ui.button(label="Add Items", style=discord.ButtonStyle.primary, emoji="📦")
    async def add_items_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("❌ This isn't your trade!", ephemeral=True)
            return
        
        modal = TradeOfferModal(self, interaction.user.id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Add Coins", style=discord.ButtonStyle.primary, emoji="💰")
    async def add_coins_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("❌ This isn't your trade!", ephemeral=True)
            return
        
        modal = TradeCoinsModal(self, interaction.user.id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Accept Trade", style=discord.ButtonStyle.success, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("❌ This isn't your trade!", ephemeral=True)
            return
        
        await self.bot.db.trading.set_ready(self.trade_id, interaction.user.id, True)
        
        trade = await self.bot.db.trading.get_trade(self.trade_id)
        
        if trade and trade['initiator_ready'] and trade['receiver_ready']:
            success = await self.bot.db.trading.complete_trade(self.trade_id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Trade Completed!",
                    description=f"Trade between **{self.initiator_name}** and **{self.receiver_name}** was successful!",
                    color=discord.Color.green()
                )
                
                from utils.systems.badge_system import BadgeSystem
                await BadgeSystem.unlock_badge(self.bot.db, self.initiator_id, 'first_trade')
                await BadgeSystem.unlock_badge(self.bot.db, self.receiver_id, 'first_trade')
                
                self.stop()
                for child in self.children:
                    if isinstance(child, (Button, Select)):
                        child.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ Failed to complete trade!", ephemeral=True)
        else:
            embed = await self.get_trade_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Cancel Trade", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("❌ This isn't your trade!", ephemeral=True)
            return
        
        await self.bot.db.trading.cancel_trade(self.trade_id)
        
        embed = discord.Embed(
            title="❌ Trade Cancelled",
            description=f"The trade was cancelled by {interaction.user.name}.",
            color=discord.Color.red()
        )
        
        self.stop()
        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def add_item_to_trade(self, interaction: discord.Interaction, user_id: int, item_id: str, amount: int):
        inventory = await self.bot.db.inventory.get_inventory(user_id)
        
        user_item = None
        for item in inventory:
            if item['item_id'] == item_id:
                user_item = item
                break
        
        if not user_item or user_item['amount'] < amount:
            await interaction.response.send_message(f"❌ You don't have {amount}x {item_id}!", ephemeral=True)
            return
        
        await self.bot.db.trading.add_trade_item(self.trade_id, user_id, item_id, amount, user_item['id'])
        await self.bot.db.trading.set_ready(self.trade_id, user_id, False)
        
        embed = await self.get_trade_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def set_trade_coins(self, interaction: discord.Interaction, user_id: int, coins: int):
        player = await self.bot.db.players.get_player(user_id)
        
        if not player or player.get('coins', 0) < coins:
            await interaction.response.send_message(f"❌ You don't have {coins:,} coins!", ephemeral=True)
            return
        
        await self.bot.db.trading.set_trade_coins(self.trade_id, user_id, coins)
        
        embed = await self.get_trade_embed()
        await interaction.response.edit_message(embed=embed, view=self)
