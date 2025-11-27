import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from collections import defaultdict
import math

class InventoryView(View):
    def __init__(self, items_dict, user_id, username, bot):
        super().__init__(timeout=180)
        self.items_dict = items_dict
        self.user_id = user_id
        self.username = username
        self.bot = bot
        self.page = 0
        self.items_per_page = 15
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        total_pages = math.ceil(len(self.items_dict) / self.items_per_page)
        
        if self.page > 0:
            prev_button = Button(label="◀️ Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if self.page < total_pages - 1:
            next_button = Button(label="Next ▶️", style=discord.ButtonStyle.gray)
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page -= 1
        self.add_buttons()
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page += 1
        self.add_buttons()
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def create_embed(self):
        embed = discord.Embed(
            title=f"🎒 {self.username}'s Inventory",
            description=f"Total unique items: {len(self.items_dict)}",
            color=discord.Color.blue()
        )
        
        items_list = sorted(self.items_dict.items(), key=lambda x: x[1], reverse=True)
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(items_list))
        
        rarity_emojis = {
            'COMMON': '⬜',
            'UNCOMMON': '🟩',
            'RARE': '🟦',
            'EPIC': '🟪',
            'LEGENDARY': '🟧',
            'MYTHIC': '🟥',
            'DIVINE': '🌟'
        }
        
        for item_id, count in items_list[start_idx:end_idx]:
            item = await self.bot.game_data.get_item(item_id)
            if item:
                rarity_emoji = rarity_emojis.get(item.rarity, '⬜')
                item_name = f"{rarity_emoji} {item.name}"
                item_type = f"{item.type.lower()} • `{item_id}`"
            else:
                item_name = item_id.replace('_', ' ').title()
                item_type = f"`{item_id}`"
            
            embed.add_field(
                name=f"{item_name} x{count:,}",
                value=item_type if item_type else "\u200b",
                inline=True
            )
        
        total_pages = math.ceil(len(items_list) / self.items_per_page)
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages if total_pages > 0 else 1} • Total items: {sum(self.items_dict.values()):,}")
        
        return embed

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="View your inventory")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        items = await self.bot.db.get_inventory(interaction.user.id)
        
        if not items:
            embed = discord.Embed(
                title=f"🎒 {interaction.user.name}'s Inventory",
                description="Your inventory is empty!\n\nUse `/starter_pack` to get some items, or start gathering with:\n• `/mine` - Mining\n• `/farm` - Farming\n• `/forage` - Foraging\n• `/fish` - Fishing\n• `/combat_mobs` - Combat",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            return
        
        item_counts = defaultdict(int)
        for item_data in items:
            item_counts[item_data['item_id']] += 1
        
        view = InventoryView(dict(item_counts), interaction.user.id, interaction.user.name, self.bot)
        embed = await view.create_embed()
        
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="enderchest", description="View your ender chest")
    async def enderchest(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        async with self.bot.db.conn.execute(
            'SELECT * FROM enderchest WHERE user_id = ?', (interaction.user.id,)
        ) as cursor:
            items = await cursor.fetchall()
        
        embed = discord.Embed(
            title=f"📦 {interaction.user.name}'s Ender Chest",
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
            for item_id, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
                item_obj = await self.bot.game_data.get_item(item_id)
                if item_obj:
                    items_text += f"• {item_obj.name}: {count}x\n"
                else:
                    items_text += f"• {item_id}: {count}x\n"
            
            if items_text:
                embed.add_field(name="Items", value=items_text, inline=False)
        else:
            embed.add_field(name="Storage", value="0/54 slots used\nYour ender chest is empty!", inline=False)
        
        embed.set_footer(text="Ender chest keeps items safe even if you lose them!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="wardrobe", description="View and manage your wardrobe")
    async def wardrobe(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        async with self.bot.db.conn.execute(
            'SELECT * FROM wardrobe WHERE user_id = ? ORDER BY slot', (interaction.user.id,)
        ) as cursor:
            wardrobe_items = await cursor.fetchall()
        
        embed = discord.Embed(
            title=f"👔 {interaction.user.name}'s Wardrobe",
            description="Quickly swap between armor sets!",
            color=discord.Color.green()
        )
        
        if wardrobe_items:
            slots_used = len(set([item[1] // 4 for item in wardrobe_items]))
            embed.add_field(name="Sets", value=f"{slots_used}/9 wardrobe slots used", inline=False)
        else:
            embed.add_field(
                name="Empty Wardrobe",
                value="You don't have any armor sets saved!\n\nSave armor sets to quickly switch between them.",
                inline=False
            )
        
        embed.set_footer(text="Use armor to save sets to your wardrobe")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="accessories", description="View your accessory bag")
    async def accessories(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        async with self.bot.db.conn.execute(
            'SELECT * FROM accessory_bag WHERE user_id = ?', (interaction.user.id,)
        ) as cursor:
            accessories = await cursor.fetchall()
        
        embed = discord.Embed(
            title=f"💎 {interaction.user.name}'s Accessories",
            description="Your accessory bag and talismans",
            color=discord.Color.gold()
        )
        
        if accessories:
            embed.add_field(name="Accessories", value=f"{len(accessories)}/54 slots used", inline=True)
            
            total_stats = defaultdict(int)
            item_counts = defaultdict(int)
            rarity_counts = defaultdict(int)
            
            for acc in accessories:
                item_id = acc[2]
                item = await self.bot.game_data.get_item(item_id)
                if item:
                    item_counts[item.name] += 1
                    rarity_counts[item.rarity] += 1
                    for stat, value in item.stats.items():
                        total_stats[stat] += value
            
            if total_stats:
                stats_text = "\n".join([f"+{value} {stat.replace('_', ' ').title()}" for stat, value in total_stats.items()])
                embed.add_field(name="Total Stats", value=stats_text, inline=True)
            
            if rarity_counts:
                for rarity in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY']:
                    if rarity in rarity_counts:
                        items_of_rarity = []
                        for item_id in item_counts.keys():
                            item_obj = await self.bot.game_data.get_item(item_id)
                            if item_obj and item_obj.rarity == rarity:
                                items_of_rarity.append(item_obj.name)
                        
                        if items_of_rarity:
                            embed.add_field(
                                name=f"{rarity.title()} ({rarity_counts[rarity]})",
                                value="\n".join(items_of_rarity[:5]),
                                inline=True
                            )
        else:
            embed.add_field(
                name="Empty Bag",
                value="You don't have any accessories!\n\nAccessories provide permanent stat bonuses.",
                inline=False
            )
        
        embed.set_footer(text="Accessories provide permanent stat boosts!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))

