import discord
from typing import Dict, Optional


class TradeOfferModal(discord.ui.Modal, title="Add Items to Trade"):
    item_id = discord.ui.TextInput(
        label="Item ID",
        placeholder="Enter the item ID (e.g., diamond, enchanted_diamond)",
        required=True,
        max_length=100
    )
    
    amount = discord.ui.TextInput(
        label="Amount",
        placeholder="Enter the amount (default: 1)",
        required=False,
        default="1",
        max_length=10
    )
    
    def __init__(self, view, user_id: int):
        super().__init__()
        self.view = view
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.view.add_item_to_trade(
            interaction,
            self.user_id,
            str(self.item_id.value),
            int(self.amount.value)
        )


class TradeCoinsModal(discord.ui.Modal, title="Add Coins to Trade"):
    coins = discord.ui.TextInput(
        label="Coins Amount",
        placeholder="Enter the amount of coins to offer",
        required=True,
        max_length=15
    )
    
    def __init__(self, view, user_id: int):
        super().__init__()
        self.view = view
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.view.set_trade_coins(
            interaction,
            self.user_id,
            int(self.coins.value)
        )
