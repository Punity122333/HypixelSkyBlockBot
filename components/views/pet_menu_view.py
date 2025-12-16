import discord
from database.misc import get_pet_stats
from components.buttons.pet_buttons import (
    PetListButton,
    PetPreviousButton,
    PetNextButton,
    PetEquipButton,
    PetUnequipButton
)
import math

class PetMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'list'
        self.page = 0
        self.items_per_page = 10
        self.pets = []
        
        self.add_item(PetListButton(self))
        self.add_item(PetPreviousButton(self))
        self.add_item(PetNextButton(self))
        self.add_item(PetEquipButton(self))
        self.add_item(PetUnequipButton(self))
    
    async def load_pets(self):
        self.pets = await self.bot.db.get_user_pets(self.user_id)
    
    async def get_embed(self):
        if self.current_view == 'list':
            return await self.get_list_embed()
        elif self.current_view == 'info':
            return await self.get_info_embed()
        return await self.get_list_embed()
    
    async def get_list_embed(self):
        active_pet = next((p for p in self.pets if p['active']), None)
        
        embed = discord.Embed(
            title="🐾 Your Pets",
            description=f"You have {len(self.pets)} pets",
            color=discord.Color.orange()
        )
        
        if not self.pets:
            embed.description = "You don't have any pets yet!\n\nPets can be obtained from:\n• Fishing (rare drops)\n• Combat (mob drops)\n• Events\n• Crafting"
            return embed
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.pets))
        
        for pet in self.pets[start_idx:end_idx]:
            pet_type = pet['pet_type']
            rarity = pet['rarity']
            level = pet['level']
            xp = pet['xp']
            is_active = pet['active']
            
            pet_data = await self.bot.game_data.get_game_pet(f"{pet_type}_{rarity}")
            if pet_data:
                stats = pet_data.get('stats', {})
            else:
                PET_STATS = await get_pet_stats()
                stats = PET_STATS.get(pet_type, {}).get(rarity, {})
            
            level_multiplier = 1 + (level / 100)
            scaled_stats = {k: int(v * level_multiplier) for k, v in stats.items()}
            
            stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in scaled_stats.items()])
            
            status = "✅ ACTIVE" if is_active else ""
            next_level_xp = level * 1000
            
            embed.add_field(
                name=f"{'✅ ' if is_active else ''}{pet_type.title()} [{rarity}] Lvl {level}",
                value=f"{stats_str}\nXP: {xp}/{next_level_xp} {status}",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.page + 1}/{max(1, math.ceil(len(self.pets) / self.items_per_page))}")
        return embed
    
    async def get_info_embed(self):
        embed = discord.Embed(
            title="🐾 Pet Info",
            description="Select a pet to view info or use /pet_info command",
            color=discord.Color.blue()
        )
        return embed

