import discord
from discord.ui import Button, View
import math
from utils.helper import get_minion_data_from_db
from components.buttons.minion_buttons import (
    MinionPreviousButton,
    MinionNextButton,
    MinionRefreshButton
)

class MinionMenuView(discord.ui.View):
    def __init__(self, bot, user_id, minions):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.minions = minions
        self.page = 0
        self.items_per_page = 5
        
        self.add_item(MinionPreviousButton(self))
        self.add_item(MinionNextButton(self))
        self.add_item(MinionRefreshButton(self))
    
    async def get_embed(self):
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
        
        total_pages = math.ceil(len(self.minions) / self.items_per_page) if len(self.minions) > 0 else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Use buttons to manage minions")
        
        return embed
