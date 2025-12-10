import discord
import time
from components.modals.merchant_deal_modal import MerchantDealModal
from components.buttons.merchant_buttons import (
    MerchantPreviousButton,
    MerchantNextButton,
    MerchantRefreshButton,
    MerchantAcceptButton
)

class MerchantMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.page = 0
        self.deals = []
        
        self.add_item(MerchantPreviousButton(self))
        self.add_item(MerchantNextButton(self))
        self.add_item(MerchantRefreshButton(self))
        self.add_item(MerchantAcceptButton(self))
    
    async def load_deals(self):
        self.deals = await self.bot.db.get_active_merchant_deals()
    
    async def get_embed(self):
        embed = discord.Embed(
            title="🏪 Traveling Merchants",
            description="Limited time deals from traveling merchants!",
            color=discord.Color.purple()
        )
        
        if not self.deals:
            embed.description = "No merchants are available right now. Check back later!"
            return embed
        
        per_page = 3
        start = self.page * per_page
        end = start + per_page
        page_deals = self.deals[start:end]
        
        for deal_row in page_deals:
            deal = dict(deal_row)
            item = await self.bot.game_data.get_item(deal['item_id'])
            if not item:
                continue
            
            created_at = deal.get('created_at', int(time.time()))
            duration = deal.get('duration', 3600)
            expires_at = created_at + duration
            time_left = expires_at - int(time.time())
            
            if time_left <= 0:
                continue
            
            hours = time_left // 3600
            minutes = (time_left % 3600) // 60
            
            deal_type = deal.get('deal_type', 'sell')
            npc_name = deal.get('npc_name', 'Merchant')
            quantity = deal.get('stock', 1)
            deal_id = deal.get('id', 0)
            
            if deal_type == 'buy':
                title = f"🛒 {npc_name} is BUYING"
                value = f"**{item.name}** x{quantity}\n"
                value += f"Offering: {deal['price']:,} coins\n"
                value += f"Expires in: {hours}h {minutes}m\n"
                value += f"Deal ID: {deal_id}"
            else:
                title = f"💰 {npc_name} is SELLING"
                value = f"**{item.name}** x{quantity}\n"
                value += f"Price: {deal['price']:,} coins\n"
                value += f"Expires in: {hours}h {minutes}m\n"
                value += f"Deal ID: {deal_id}"
            
            embed.add_field(
                name=title,
                value=value,
                inline=False
            )
        
        total_pages = (len(self.deals) + per_page - 1) // per_page if self.deals else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Use commands to accept deals")
        return embed

