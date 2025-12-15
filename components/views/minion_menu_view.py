import discord
from discord.ui import Button, View
import math
import json
import time
from utils.helper import get_minion_data_from_db
from components.buttons.minion_buttons import (
    MinionPreviousButton,
    MinionNextButton,
    MinionRefreshButton,
    MinionCollectButton,
    MinionPlaceButton,
    MinionRemoveButton,
    MinionUpgradeButton,
    MinionFuelButton,
    MinionSkinButton
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
        self.add_item(MinionCollectButton(self))
        self.add_item(MinionPlaceButton(self))
        self.add_item(MinionRemoveButton(self))
        self.add_item(MinionUpgradeButton(self))
        self.add_item(MinionFuelButton(self))
        self.add_item(MinionSkinButton(self))
    
    async def get_embed(self):
        embed = discord.Embed(
            title="🤖 Your Minions",
            description=f"You have {len(self.minions)} minions working for you",
            color=discord.Color.blue()
        )
        
        if len(self.minions) == 0:
            embed.add_field(
                name="No Minions Placed",
                value="Use the **📦 Place Minion** button to place a minion from your inventory!",
                inline=False
            )
        else:
            start_idx = self.page * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(self.minions))
            
            for i, minion in enumerate(self.minions[start_idx:end_idx], start=start_idx + 1):
                minion_type = minion['minion_type']
                tier = minion['tier']
                storage = minion.get('storage', 0)
                
                minion_info = await get_minion_data_from_db(self.bot.game_data, minion_type)
                produces = minion_info.get('produces', minion_type)
                base_speed = minion_info.get('speed', 60)
                
                upgrades = await self.bot.db.minion_upgrades.get_minion_upgrades(minion['id'])
                
                speed = base_speed / tier
                if 'fuel' in upgrades and upgrades['fuel'].get('expires_at', 0) > time.time():
                    speed_boost = upgrades['fuel'].get('speed_boost', 0)
                    speed = speed * speed_boost
                
                upgrade_text = ""
                if 'fuel' in upgrades and upgrades['fuel'].get('expires_at', 0) > time.time():
                    fuel_name = upgrades['fuel'].get('fuel_id', 'Unknown')
                    time_left = upgrades['fuel'].get('expires_at', 0) - time.time()
                    hours_left = time_left / 3600
                    upgrade_text += f"\n⛽ Fuel: {fuel_name.replace('_', ' ').title()} ({hours_left:.1f}h left)"
                
                if 'skin' in upgrades:
                    skin_name = upgrades['skin'].get('skin_name', 'Unknown')
                    upgrade_text += f"\n🎨 Skin: {skin_name}"
                
                embed.add_field(
                    name=f"{i}. {minion_type.title()} Minion (Tier {tier})",
                    value=f"Produces: {produces.replace('_', ' ').title()}\nSpeed: {speed:.1f}s per action\nStorage: {storage} items{upgrade_text}",
                    inline=False
                )
        
        total_pages = math.ceil(len(self.minions) / self.items_per_page) if len(self.minions) > 0 else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Use buttons to manage minions")
        
        return embed
