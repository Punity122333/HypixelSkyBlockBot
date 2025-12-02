import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict

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
        async with self.bot.db.conn.execute(
            'SELECT * FROM wardrobe WHERE user_id = ? ORDER BY slot', (self.user_id,)
        ) as cursor:
            wardrobe_items = await cursor.fetchall()
        
        embed = discord.Embed(
            title=f"👔 {self.username}'s Wardrobe",
            description="Quickly swap between armor sets!",
            color=discord.Color.green()
        )
        
        if wardrobe_items:
            slots_used = len(set([item[1] // 4 for item in wardrobe_items]))
            embed.add_field(name="Sets", value=f"{slots_used}/9 wardrobe slots used", inline=False)
        else:
            embed.add_field(
                name="Empty Wardrobe",
                value="You don't have any armor sets saved!",
                inline=False
            )
        
        embed.set_footer(text="Save armor sets to quickly switch")
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
        
        self.add_item(self.inventory_button)
        self.add_item(self.enderchest_button)
        self.add_item(self.wardrobe_button)
        self.add_item(self.accessories_button)
        
        if self.current_view == 'inventory' and self.total_pages > 1:
            self.add_item(self.prev_button)
            self.add_item(self.next_button)
    
    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.blurple, row=0)
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'inventory'
        self.page = 0
        embed = await self.get_embed()
        self._update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📦 Ender Chest", style=discord.ButtonStyle.gray, row=0)
    async def enderchest_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'enderchest'
        self.page = 0
        embed = await self.get_embed()
        self._update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👔 Wardrobe", style=discord.ButtonStyle.green, row=0)
    async def wardrobe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'wardrobe'
        self.page = 0
        embed = await self.get_embed()
        self._update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="💎 Accessories", style=discord.ButtonStyle.gray, row=0)
    async def accessories_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_view = 'accessories'
        self.page = 0
        embed = await self.get_embed()
        self._update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            embed = await self.get_embed()
            self._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.page < self.total_pages - 1:
            self.page += 1
            embed = await self.get_embed()
            self._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="View your inventory and storage")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = InventoryMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        view._update_buttons()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))
