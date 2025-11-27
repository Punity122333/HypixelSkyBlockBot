import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import time
import math

MINION_DATA = {
    'wheat': {'produces': 'wheat', 'speed': 30, 'max_tier': 11, 'category': 'farming'},
    'carrot': {'produces': 'carrot', 'speed': 30, 'max_tier': 11, 'category': 'farming'},
    'potato': {'produces': 'potato', 'speed': 30, 'max_tier': 11, 'category': 'farming'},
    'pumpkin': {'produces': 'pumpkin', 'speed': 40, 'max_tier': 11, 'category': 'farming'},
    'melon': {'produces': 'melon', 'speed': 35, 'max_tier': 11, 'category': 'farming'},
    'cobblestone': {'produces': 'cobblestone', 'speed': 25, 'max_tier': 11, 'category': 'mining'},
    'coal': {'produces': 'coal', 'speed': 35, 'max_tier': 11, 'category': 'mining'},
    'iron': {'produces': 'iron_ingot', 'speed': 45, 'max_tier': 11, 'category': 'mining'},
    'gold': {'produces': 'gold_ingot', 'speed': 60, 'max_tier': 11, 'category': 'mining'},
    'diamond': {'produces': 'diamond', 'speed': 90, 'max_tier': 11, 'category': 'mining'},
    'oak': {'produces': 'oak_wood', 'speed': 30, 'max_tier': 11, 'category': 'foraging'},
    'jungle': {'produces': 'jungle_wood', 'speed': 35, 'max_tier': 11, 'category': 'foraging'},
    'slime': {'produces': 'slime_ball', 'speed': 50, 'max_tier': 11, 'category': 'combat'},
    'zombie': {'produces': 'rotten_flesh', 'speed': 40, 'max_tier': 11, 'category': 'combat'},
    'skeleton': {'produces': 'bone', 'speed': 45, 'max_tier': 11, 'category': 'combat'},
    'spider': {'produces': 'string', 'speed': 45, 'max_tier': 11, 'category': 'combat'},
    'blaze': {'produces': 'blaze_rod', 'speed': 60, 'max_tier': 11, 'category': 'combat'},
    'enderman': {'produces': 'ender_pearl', 'speed': 70, 'max_tier': 11, 'category': 'combat'},
    'snow': {'produces': 'snow_block', 'speed': 25, 'max_tier': 11, 'category': 'mining'},
    'clay': {'produces': 'clay', 'speed': 35, 'max_tier': 11, 'category': 'mining'},
}

async def get_minion_data_from_db(game_data_manager, minion_type: str):
    minion_data = await game_data_manager.get_minion_data(minion_type)
    if minion_data:
        return {
            'produces': minion_data['produces'],
            'speed': minion_data['base_speed'],
            'max_tier': minion_data['max_tier'],
            'category': minion_data['category']
        }
    return MINION_DATA.get(minion_type, {})

class MinionView(View):
    def __init__(self, minions, user_id, bot):
        super().__init__(timeout=180)
        self.minions = minions
        self.user_id = user_id
        self.bot = bot
        self.page = 0
        self.items_per_page = 5
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        if self.page > 0:
            prev_button = Button(label="◀️ Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        total_pages = math.ceil(len(self.minions) / self.items_per_page)
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
            title="🤖 Your Minions",
            description=f"You have {len(self.minions)} minions working for you",
            color=discord.Color.blue()
        )
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.minions))
        
        for minion in self.minions[start_idx:end_idx]:
            minion_type = minion['minion_type']
            tier = minion['tier']
            slot = minion['island_slot']
            storage = minion['storage']
            
            minion_info = await get_minion_data_from_db(self.bot.game_data, minion_type)
            produces = minion_info.get('produces', minion_type)
            base_speed = minion_info.get('speed', 60)
            
            speed = base_speed / tier
            
            from collections import defaultdict
            storage_counts = defaultdict(int)
            for item in storage:
                storage_counts[item.get('item_id', 'unknown')] += item.get('amount', 1)
            
            storage_text = ""
            if storage_counts:
                for item_id, count in list(storage_counts.items())[:3]:
                    storage_text += f"{count}x {item_id.replace('_', ' ').title()}, "
                storage_text = storage_text.rstrip(', ')
            else:
                storage_text = "Empty"
            
            embed.add_field(
                name=f"Slot {slot}: {minion_type.title()} Minion (Tier {tier})",
                value=f"Produces: {produces.replace('_', ' ').title()}\nSpeed: {speed:.1f}s per action\nStorage: {storage_text}\nID: {minion['id']}",
                inline=False
            )
        
        total_pages = math.ceil(len(self.minions) / self.items_per_page)
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages if total_pages > 0 else 1} • Use /minion_collect <id> to collect")
        
        return embed

class MinionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="minion_place", description="Place a minion on your island")
    @app_commands.describe(minion_type="Type of minion to place", slot="Island slot (1-25)")
    async def minion_place(self, interaction: discord.Interaction, minion_type: str, slot: int):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if slot < 1 or slot > 25:
            await interaction.followup.send("❌ Slot must be between 1 and 25!", ephemeral=True)
            return
        
        minion_type = minion_type.lower()
        minion_item_id = f"{minion_type}_minion"
        
        inventory = await self.bot.db.get_inventory(interaction.user.id)
        has_minion = any(item['item_id'] == minion_item_id for item in inventory)
        
        if not has_minion:
            await interaction.followup.send(f"❌ You don't have a {minion_type.title()} Minion! Craft one first with `/craft {minion_item_id}`", ephemeral=True)
            return
        
        existing_minions = await self.bot.db.get_user_minions(interaction.user.id)
        if any(m['island_slot'] == slot for m in existing_minions):
            await interaction.followup.send(f"❌ Slot {slot} is already occupied! Use a different slot or remove the existing minion first.", ephemeral=True)
            return
        
        await self.bot.db.remove_item_from_inventory(interaction.user.id, minion_item_id, 1)
        
        await self.bot.db.add_minion(interaction.user.id, minion_type, tier=1, island_slot=slot)
        
        embed = discord.Embed(
            title="🤖 Minion Placed!",
            description=f"You placed a **{minion_type.title()} Minion** in slot {slot}!",
            color=discord.Color.green()
        )
        
        minion_info = await get_minion_data_from_db(self.bot.game_data, minion_type)
        if minion_info:
            embed.add_field(
                name="Info",
                value=f"Produces: {minion_info['produces'].replace('_', ' ').title()}\nSpeed: {minion_info['speed']}s per action\nMax Storage: 64 items",
                inline=False
            )
        
        embed.set_footer(text="Your minion will now produce resources automatically!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="minion_collect", description="Collect resources from a minion")
    @app_commands.describe(minion_id="Minion ID to collect from")
    async def minion_collect(self, interaction: discord.Interaction, minion_id: int):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        minion = await self.bot.db.get_minion(minion_id)
        
        if not minion or minion['user_id'] != interaction.user.id:
            await interaction.followup.send("❌ Minion not found or doesn't belong to you!", ephemeral=True)
            return
        
        storage = minion['storage']
        
        if not storage:
            await interaction.followup.send("❌ This minion's storage is empty! Wait for it to produce resources.", ephemeral=True)
            return
        
        from collections import defaultdict
        collected_items = defaultdict(int)
        
        for item in storage:
            item_id = item.get('item_id')
            amount = item.get('amount', 1)
            collected_items[item_id] += amount
            await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
        
        await self.bot.db.update_minion_storage(minion_id, [])
        
        embed = discord.Embed(
            title="📦 Collected from Minion!",
            description=f"**{minion['minion_type'].title()} Minion** (Tier {minion['tier']})",
            color=discord.Color.green()
        )
        
        items_text = "\n".join([f"• {amount}x {item_id.replace('_', ' ').title()}" for item_id, amount in collected_items.items()])
        embed.add_field(name="Items Collected", value=items_text, inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="minion_upgrade", description="Upgrade a minion to the next tier")
    @app_commands.describe(minion_id="Minion ID to upgrade")
    async def minion_upgrade(self, interaction: discord.Interaction, minion_id: int):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        minion = await self.bot.db.get_minion(minion_id)
        
        if not minion or minion['user_id'] != interaction.user.id:
            await interaction.followup.send("❌ Minion not found or doesn't belong to you!", ephemeral=True)
            return
        
        minion_type = minion['minion_type']
        current_tier = minion['tier']
        
        minion_info = await get_minion_data_from_db(self.bot.game_data, minion_type)
        max_tier = minion_info.get('max_tier', 11)
        
        if current_tier >= max_tier:
            await interaction.followup.send(f"❌ This minion is already at max tier ({max_tier})!", ephemeral=True)
            return
        
        required_minions = 2
        minion_item_id = f"{minion_type}_minion"
        
        inventory = await self.bot.db.get_inventory(interaction.user.id)
        minion_count = sum(1 for item in inventory if item['item_id'] == minion_item_id)
        
        if minion_count < required_minions:
            await interaction.followup.send(f"❌ You need {required_minions}x {minion_type.title()} Minion to upgrade! (You have {minion_count})", ephemeral=True)
            return
        
        await self.bot.db.remove_item_from_inventory(interaction.user.id, minion_item_id, required_minions)
        
        await self.bot.db.upgrade_minion(minion_id)
        
        embed = discord.Embed(
            title="⬆️ Minion Upgraded!",
            description=f"**{minion_type.title()} Minion** upgraded to Tier {current_tier + 1}!",
            color=discord.Color.gold()
        )
        
        old_speed = minion_info.get('speed', 60) / current_tier
        new_speed = minion_info.get('speed', 60) / (current_tier + 1)
        
        embed.add_field(
            name="Improvements",
            value=f"Speed: {old_speed:.1f}s → {new_speed:.1f}s per action\nProduction increased by {((old_speed / new_speed - 1) * 100):.1f}%",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="minion_remove", description="Remove a minion from your island")
    @app_commands.describe(minion_id="Minion ID to remove")
    async def minion_remove(self, interaction: discord.Interaction, minion_id: int):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        minion = await self.bot.db.get_minion(minion_id)
        
        if not minion or minion['user_id'] != interaction.user.id:
            await interaction.followup.send("❌ Minion not found or doesn't belong to you!", ephemeral=True)
            return
        
        if minion['storage']:
            await interaction.followup.send("❌ Collect items from this minion before removing it! Use `/minion_collect`", ephemeral=True)
            return
        
        await self.bot.db.delete_minion(minion_id, interaction.user.id)
        
        minion_item_id = f"{minion['minion_type']}_minion"
        await self.bot.db.add_item_to_inventory(interaction.user.id, minion_item_id, 1)
        
        embed = discord.Embed(
            title="🗑️ Minion Removed",
            description=f"**{minion['minion_type'].title()} Minion** (Tier {minion['tier']}) has been returned to your inventory.",
            color=discord.Color.red()
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MinionCommands(bot))
