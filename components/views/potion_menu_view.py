import discord
import time
from utils.systems.potion_system import PotionSystem
from components.buttons.potion_menu_buttons import (
    PotionMainButton,
    PotionActiveButton,
    PotionInventoryButton,
    PotionPreviousButton,
    PotionNextButton,
    PotionUseButton
)

class PotionMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.page = 0
        self.items_per_page = 10
        self.potions_list = []
        self.active_list = []
        
        self.main_button = PotionMainButton(self)
        self.active_button = PotionActiveButton(self)
        self.inventory_button = PotionInventoryButton(self)
        self.prev_button = PotionPreviousButton(self)
        self.next_button = PotionNextButton(self)
        self.use_button = PotionUseButton(self)
        
        self._update_buttons()
    
    async def load_potions(self):
        inventory = await self.bot.db.get_inventory(self.user_id)
        
        self.potions_list = []
        for item in inventory:
            item_id = item['item_id']
            if item_id in PotionSystem.POTION_EFFECTS:
                game_item = await self.bot.db.get_game_item(item_id)
                if game_item:
                    self.potions_list.append({
                        'item_id': item_id,
                        'name': game_item['name'],
                        'rarity': game_item['rarity'],
                        'amount': item.get('amount', 1)
                    })
    
    async def load_active_potions(self):
        self.active_list = await PotionSystem.get_active_potions(self.bot.db, self.user_id)
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'active':
            return await self.get_active_embed()
        elif self.current_view == 'inventory':
            return await self.get_inventory_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        active_potions = await PotionSystem.get_active_potions(self.bot.db, self.user_id)
        
        embed = discord.Embed(
            title="🧪 Potions",
            description="Manage your potions and active effects",
            color=discord.Color.green()
        )
        
        if active_potions:
            embed.add_field(name="Active Effects", value=f"{len(active_potions)} potion effect(s) active", inline=False)
        else:
            embed.add_field(name="Active Effects", value="No active potion effects", inline=False)
        
        embed.set_footer(text="Use buttons below to manage your potions")
        return embed
    
    async def get_active_embed(self):
        if not self.active_list:
            await self.load_active_potions()
        
        embed = discord.Embed(
            title="✨ Active Potion Effects",
            description=f"You have {len(self.active_list)} active potion effect(s)",
            color=discord.Color.blue()
        )
        
        if not self.active_list:
            embed.description = "No active potion effects!"
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.active_list))
            page_potions = self.active_list[start:end]
            
            current_time = int(time.time())
            
            for potion_data in page_potions:
                potion_id = potion_data['potion_id']
                expires_at = potion_data['expires_at']
                time_left = expires_at - current_time
                minutes_left = time_left // 60
                seconds_left = time_left % 60
                
                if potion_id in PotionSystem.POTION_EFFECTS:
                    effect = PotionSystem.POTION_EFFECTS[potion_id]
                    stat_name = effect.get('stat', 'unknown').replace('_', ' ').title()
                    potion_name = potion_id.replace('_', ' ').title()
                    
                    embed.add_field(
                        name=f"🧪 {potion_name}",
                        value=f"+{effect.get('amount', 0)} {stat_name}\nTime left: {minutes_left}m {seconds_left}s",
                        inline=False
                    )
        
        total_pages = (len(self.active_list) + self.items_per_page - 1) // self.items_per_page if self.active_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    async def get_inventory_embed(self):
        if not self.potions_list:
            await self.load_potions()
        
        embed = discord.Embed(
            title="🧪 My Potions",
            description=f"You have {len(self.potions_list)} potion(s) in your inventory",
            color=discord.Color.gold()
        )
        
        if not self.potions_list:
            embed.description = "No potions in your inventory!"
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.potions_list))
            page_potions = self.potions_list[start:end]
            
            rarity_emojis = {
                'COMMON': '⬜',
                'UNCOMMON': '🟩',
                'RARE': '🟦',
                'EPIC': '🟪',
                'LEGENDARY': '🟧',
                'MYTHIC': '🟥'
            }
            
            for idx, potion in enumerate(page_potions, start + 1):
                rarity_emoji = rarity_emojis.get(potion['rarity'], '⬜')
                amount_text = f" (x{potion['amount']})" if potion.get('amount', 1) > 1 else ""
                
                effect = PotionSystem.POTION_EFFECTS.get(potion['item_id'], {})
                if effect.get('type') == 'instant_heal':
                    effect_text = f"💗 Heals {effect['amount']} HP"
                elif effect.get('type') == 'god':
                    effect_text = "✨ All stat bonuses!"
                else:
                    stat_name = effect.get('stat', 'unknown').replace('_', ' ').title()
                    effect_text = f"⚡ +{effect.get('amount', 0)} {stat_name}"
                
                embed.add_field(
                    name=f"{idx}. {rarity_emoji} {potion['name']}{amount_text}",
                    value=effect_text,
                    inline=False
                )
        
        total_pages = (len(self.potions_list) + self.items_per_page - 1) // self.items_per_page if self.potions_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.active_button)
        self.add_item(self.inventory_button)
        
        data_list = []
        if self.current_view == 'inventory':
            data_list = self.potions_list
        elif self.current_view == 'active':
            data_list = self.active_list
        
        if data_list:
            total_pages = (len(data_list) + self.items_per_page - 1) // self.items_per_page
            if total_pages > 1:
                self.add_item(self.prev_button)
                self.add_item(self.next_button)
        
        self.add_item(self.use_button)
