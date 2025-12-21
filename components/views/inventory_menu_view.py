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
from components.buttons.talisman_pouch_buttons import (
    TalismanPouchButton,
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
        self.talisman_pouch_btn = TalismanPouchButton(self)
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
        elif self.current_view == 'talisman_pouch':
            return await self.get_talisman_pouch_embed()
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
                inventory_item_id = item.get('id')
                
                stat_display = ""
                if item_type in ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']:
                    armor_stats = await self.bot.db.get_armor_stats(item_id)
                    if armor_stats:
                        multiplier_stats = []
                        regular_stats = []
                        for k, v in armor_stats.items():
                            if k == 'item_id':
                                continue
                            if 'multiplier' in k and v != 1.0:
                                multiplier_stats.append((k, v))
                            elif v > 0:
                                regular_stats.append((k, v))
                        
                        multiplier_stats.sort(key=lambda x: x[1], reverse=True)
                        regular_stats.sort(key=lambda x: x[1], reverse=True)
                        
                        display_stats = []
                        for k, v in (multiplier_stats + regular_stats)[:3]:
                            if 'multiplier' in k:
                                display_stats.append(f"{k.replace('_', ' ').title()}: {v}x")
                            else:
                                display_stats.append(f"{k.replace('_', ' ').title()}: +{v}")
                        stat_display = '\n'.join(display_stats)
                elif item_type in ['SWORD', 'BOW']:
                    weapon_stats = await self.bot.db.get_weapon_stats(item_id)
                    if weapon_stats:
                        multiplier_stats = []
                        regular_stats = []
                        for k, v in weapon_stats.items():
                            if k == 'item_id':
                                continue
                            if 'multiplier' in k and v != 1.0:
                                multiplier_stats.append((k, v))
                            elif v > 0:
                                regular_stats.append((k, v))
                        
                        multiplier_stats.sort(key=lambda x: x[1], reverse=True)
                        regular_stats.sort(key=lambda x: x[1], reverse=True)
                        
                        display_stats = []
                        for k, v in (multiplier_stats + regular_stats)[:3]:
                            if 'multiplier' in k:
                                display_stats.append(f"{k.replace('_', ' ').title()}: {v}x")
                            else:
                                display_stats.append(f"{k.replace('_', ' ').title()}: +{v}")
                        stat_display = '\n'.join(display_stats)
                elif item_type in ['PICKAXE', 'AXE', 'HOE', 'SHOVEL', 'FISHING_ROD']:
                    tool_stats = await self.bot.db.get_tool_stats(item_id)
                    if tool_stats:
                        multiplier_stats = []
                        regular_stats = []
                        for k, v in tool_stats.items():
                            if k in ['item_id', 'tool_type', 'durability']:
                                continue
                            if 'multiplier' in k and v != 1.0:
                                multiplier_stats.append((k, v))
                            elif v > 0 and v != 1.0:
                                regular_stats.append((k, v))
                        
                        multiplier_stats.sort(key=lambda x: x[1], reverse=True)
                        regular_stats.sort(key=lambda x: x[1], reverse=True)
                        
                        display_stats = []
                        for k, v in (multiplier_stats + regular_stats)[:3]:
                            if 'multiplier' in k:
                                display_stats.append(f"{k.replace('_', ' ').title()}: {v}x")
                            else:
                                display_stats.append(f"{k.replace('_', ' ').title()}: +{v}")
                        stat_display = '\n'.join(display_stats)
                
                if not stat_display:
                    stats = json.loads(item.get('stats', '{}'))
                    stat_display = '\n'.join([f"{k}: {v}" for k, v in list(stats.items())[:3]])
                
                enchant_display = ""
                if inventory_item_id:
                    from utils.enchantment_display import format_enchantments_display, format_enchantment_stats_display
                    enchant_display = await format_enchantments_display(self.bot.db, inventory_item_id)
                    if enchant_display:
                        enchant_stats = await format_enchantment_stats_display(self.bot.db, inventory_item_id)
                        if enchant_stats:
                            stat_display = f"{stat_display}\n{enchant_stats}" if stat_display else enchant_stats
                        stat_display = f"{stat_display}\n{enchant_display}" if stat_display else enchant_display
                
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
        
        active_pet = await self.bot.db.get_active_pet(self.user_id)
        if active_pet:
            from database.misc import get_pet_stats
            pet_type = active_pet['pet_type'].lower()
            rarity = active_pet['rarity'].upper()
            level = active_pet.get('level', 1)
            
            PET_STATS = await get_pet_stats()
            pet_stats = PET_STATS.get(pet_type, {}).get(rarity, {})
            level_multiplier = 1 + (level / 100)
            scaled_stats = {k: int(v * level_multiplier) for k, v in pet_stats.items()}
            
            stat_display = '\n'.join([f"{k.replace('_', ' ').title()}: +{v}" for k, v in list(scaled_stats.items())[:3]])
            
            embed.add_field(
                name=f"🐾 Active Pet",
                value=f"**{pet_type.title()} (Lvl {level})**\n{rarity}\n{stat_display if stat_display else 'No stats'}",
                inline=True
            )
        else:
            embed.add_field(
                name=f"🐾 Active Pet",
                value="*None*\n\nEquip a pet for bonuses",
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
    
    async def get_talisman_pouch_embed(self):
        from utils.systems.talisman_pouch_system import TalismanPouchSystem
        
        talismans = await TalismanPouchSystem.get_talisman_pouch(self.bot.db, self.user_id)
        
        embed = discord.Embed(
            title=f"📿 {self.username}'s Talisman Pouch",
            description=f"Talismans provide passive stat bonuses\n{len(talismans)}/{TalismanPouchSystem.MAX_TALISMANS} slots used",
            color=discord.Color.purple()
        )
        
        if talismans:
            from collections import defaultdict
            total_stats = defaultdict(int)
            
            for talisman_data in talismans:
                talisman_id = talisman_data['talisman_id']
                item = await self.bot.game_data.get_item(talisman_id)
                if item:
                    rarity_emoji = {'COMMON': '⬜', 'UNCOMMON': '🟩', 'RARE': '🟦',
                                   'EPIC': '🟪', 'LEGENDARY': '🟧', 'MYTHIC': '🟥'}.get(item.rarity, '⬜')
                    stats_text = ', '.join([f"+{v} {k.replace('_', ' ').title()}" for k, v in item.stats.items()])
                    embed.add_field(
                        name=f"{rarity_emoji} {item.name}",
                        value=stats_text or "No stats",
                        inline=True
                    )
                    for stat, value in item.stats.items():
                        total_stats[stat] += value
            
            if total_stats:
                total_text = "\n".join([f"+{value} {stat.replace('_', ' ').title()}" for stat, value in total_stats.items()])
                embed.add_field(name="📊 Total Bonuses", value=total_text, inline=False)
        else:
            embed.add_field(name="Empty Pouch", value="Add talismans with the button below!", inline=False)
        
        embed.set_footer(text="Craft talismans with runes!")
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