import discord
from collections import defaultdict
import json
from components.buttons.equip_item_button import EquipItemButton
from components.buttons.unequip_item_button import UnequipItemButton
from components.buttons.inventory_buttons import (
    InventoryButton,
    EnderchestButton,
    WardrobeButton,
    AccessoriesButton,
    InventoryPreviousButton,
    InventoryNextButton
)

class InventoryMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_view = 'inventory'
        self.page = 0
        self.items_per_page = 10
        self.total_pages = 1
        self.wardrobe_page = 1
        
        self.inventory_btn = InventoryButton(self)
        self.enderchest_btn = EnderchestButton(self)
        self.wardrobe_btn = WardrobeButton(self)
        self.accessories_btn = AccessoriesButton(self)
        self.prev_btn = InventoryPreviousButton(self)
        self.next_btn = InventoryNextButton(self)
        
        self._update_buttons()  # Initialize wardrobe page
    
    async def get_embed(self):
        if self.current_view == 'inventory':
            return await self.get_inventory_embed()
        elif self.current_view == 'enderchest':
            return await self.get_enderchest_embed()
        elif self.current_view == 'wardrobe':
            return await self.get_wardrobe_embed()
        elif self.current_view == 'accessories':
            return await self.get_accessories_embed()
        else:
            return await self.get_inventory_embed()
    
    async def get_inventory_embed(self):
        items = await self.bot.db.get_inventory(self.user_id)
        
        if not items:
            self.total_pages = 1
            embed = discord.Embed(
                title=f"🎒 {self.username}'s Inventory",
                description="Your inventory is empty!\n\nUse `/starter_pack` to get some items, or start gathering!",
                color=discord.Color.blue()
            )
            return embed
        
        item_counts = defaultdict(int)
        for item_data in items:
            item_counts[item_data['item_id']] += 1
        
        embed = discord.Embed(
            title=f"🎒 {self.username}'s Inventory",
            description=f"Total unique items: {len(item_counts)}",
            color=discord.Color.blue()
        )
        
        items_list = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        page_items = items_list[start:end]
        
        rarity_emojis = {
            'COMMON': '⬜',
            'UNCOMMON': '🟩',
            'RARE': '🟦',
            'EPIC': '🟪',
            'LEGENDARY': '🟧',
            'MYTHIC': '🟥',
            'DIVINE': '🌟'
        }
        
        for item_id, count in page_items:
            item = await self.bot.game_data.get_item(item_id)
            if item:
                rarity_emoji = rarity_emojis.get(item.rarity, '⬜')
                item_name = f"{rarity_emoji} {item.name}"
            else:
                item_name = item_id.replace('_', ' ').title()
            
            embed.add_field(
                name=f"{item_name} x{count:,}",
                value=f"`{item_id}`",
                inline=True
            )
        
        self.total_pages = (len(items_list) + self.items_per_page - 1) // self.items_per_page if items_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{self.total_pages} • Use buttons to navigate")
        return embed
    
    async def get_enderchest_embed(self):
        self.total_pages = 1
        async with self.bot.db.conn.execute(
            'SELECT * FROM enderchest WHERE user_id = ?', (self.user_id,)
        ) as cursor:
            items = await cursor.fetchall()
        
        embed = discord.Embed(
            title=f"📦 {self.username}'s Ender Chest",
            description="Secure storage for valuable items",
            color=discord.Color.purple()
        )
        
        if items:
            embed.add_field(name="Storage", value=f"{len(items)}/54 slots used", inline=False)
            
            item_counts = defaultdict(int)
            for item in items:
                item_id = item[2]
                item_counts[item_id] += 1
            
            items_text = ""
            for item_id, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                item_obj = await self.bot.game_data.get_item(item_id)
                if item_obj:
                    items_text += f"• {item_obj.name}: {count}x\n"
                else:
                    items_text += f"• {item_id}: {count}x\n"
            
            if items_text:
                embed.add_field(name="Items", value=items_text, inline=False)
        else:
            embed.add_field(name="Storage", value="0/54 slots used\nYour ender chest is empty!", inline=False)
        
        embed.set_footer(text="Ender chest keeps items safe!")
        return embed
    
    async def get_wardrobe_embed(self):
        self.total_pages = 1
        
        equipped = await self.bot.db.get_equipped_items(self.user_id)
        
        embed = discord.Embed(
            title=f"👔 {self.username}'s Wardrobe",
            description="Equip armor, weapons, and tools to enhance your stats!",
            color=discord.Color.green()
        )
        
        # All equipment slots in one view
        equipment_emojis = {
            'helmet': '🪖',
            'chestplate': '🦺',
            'leggings': '👖',
            'boots': '👢',
            'sword': '🗡️',
            'bow': '🏹',
            'pickaxe': '⛏️',
            'axe': '🪓',
            'hoe': '🌾',
            'fishing_rod': '🎣'
        }
        
        for slot, emoji in equipment_emojis.items():
            item = equipped.get(slot)
            if item and 'name' in item:
                item_id = item.get('item_id')
                item_type = item.get('item_type')
                
                stat_display = ""
                if item_type in ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']:
                    armor_stats = await self.bot.db.get_armor_stats(item_id)
                    if armor_stats:
                        top_stats = [(k, v) for k, v in armor_stats.items() if k not in ['item_id'] and v > 0]
                        top_stats.sort(key=lambda x: x[1], reverse=True)
                        stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in top_stats[:3]])
                elif item_type in ['SWORD', 'BOW']:
                    weapon_stats = await self.bot.db.get_weapon_stats(item_id)
                    if weapon_stats:
                        top_stats = [(k, v) for k, v in weapon_stats.items() if k not in ['item_id'] and v > 0]
                        top_stats.sort(key=lambda x: x[1], reverse=True)
                        stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in top_stats[:3]])
                elif item_type in ['PICKAXE', 'AXE', 'HOE', 'SHOVEL', 'FISHING_ROD']:
                    tool_stats = await self.bot.db.get_tool_stats(item_id)
                    if tool_stats:
                        top_stats = [(k, v) for k, v in tool_stats.items() if k not in ['item_id', 'tool_type', 'durability'] and v > 0 and v != 1.0]
                        top_stats.sort(key=lambda x: x[1], reverse=True)
                        stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in top_stats[:3]])
                
                if not stat_display:
                    stats = json.loads(item.get('stats', '{}'))
                    stat_display = '\n'.join([f"{k}: {v}" for k, v in list(stats.items())[:3]])
                
                embed.add_field(
                    name=f"{emoji} {slot.title()}",
                    value=f"**{item['name']}**\n{stat_display if stat_display else 'No stats'}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"{emoji} {slot.title()}",
                    value="*Empty*\n\nClick button to equip",
                    inline=True
                )
        
        embed.set_footer(text="Use the buttons below to equip or unequip items")
        return embed
    
    async def get_accessories_embed(self):
        self.total_pages = 1
        async with self.bot.db.conn.execute(
            'SELECT * FROM accessory_bag WHERE user_id = ?', (self.user_id,)
        ) as cursor:
            accessories = await cursor.fetchall()
        
        embed = discord.Embed(
            title=f"💎 {self.username}'s Accessories",
            description="Your accessory bag and talismans",
            color=discord.Color.gold()
        )
        
        if accessories:
            embed.add_field(name="Accessories", value=f"{len(accessories)}/54 slots used", inline=True)
            
            total_stats = defaultdict(int)
            rarity_counts = defaultdict(int)
            
            for acc in accessories:
                item_id = acc[2]
                item = await self.bot.game_data.get_item(item_id)
                if item:
                    rarity_counts[item.rarity] += 1
                    for stat, value in item.stats.items():
                        total_stats[stat] += value
            
            if total_stats:
                stats_text = "\n".join([f"+{value} {stat.replace('_', ' ').title()}" for stat, value in list(total_stats.items())[:5]])
                embed.add_field(name="Total Stats", value=stats_text, inline=True)
        else:
            embed.add_field(name="Empty Bag", value="No accessories equipped!", inline=False)
        
        embed.set_footer(text="Accessories provide permanent stat bonuses")
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.inventory_btn)
        self.add_item(self.enderchest_btn)
        self.add_item(self.wardrobe_btn)
        self.add_item(self.accessories_btn)
        
        if self.current_view == 'inventory' and self.total_pages > 1:
            self.add_item(self.prev_btn)
            self.add_item(self.next_btn)