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
            embed.set_footer(text="Merchants rotate regularly with new deals")
            return embed
        
        per_page = 3
        current_time = int(time.time())
        
        valid_deals = []
        for deal_row in self.deals:
            deal = dict(deal_row)
            created_at = deal.get('created_at', current_time)
            duration = deal.get('duration', 3600)
            expires_at = created_at + duration
            time_left = expires_at - current_time
            
            if time_left > 0 and deal.get('stock', 0) > 0:
                valid_deals.append(deal)
        
        if not valid_deals:
            embed.description = "No merchants are available right now. Check back later!"
            embed.set_footer(text="Merchants rotate regularly with new deals")
            return embed
        
        total_pages = (len(valid_deals) + per_page - 1) // per_page
        start = self.page * per_page
        end = start + per_page
        page_deals = valid_deals[start:end]
        
        valid_deals_shown = 0
        for deal in page_deals:
            item = await self.bot.game_data.get_item(deal['item_id'])
            if not item:
                continue
            
            created_at = deal.get('created_at', current_time)
            duration = deal.get('duration', 3600)
            expires_at = created_at + duration
            time_left = expires_at - current_time
            
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
            valid_deals_shown += 1
        
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Use commands to accept deals")
        return embed

