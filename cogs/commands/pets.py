import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from typing import Optional
import math

PET_STATS = {
    'wolf': {
        'COMMON': {'strength': 5, 'crit_damage': 10},
        'UNCOMMON': {'strength': 10, 'crit_damage': 15},
        'RARE': {'strength': 15, 'crit_damage': 25},
        'EPIC': {'strength': 25, 'crit_damage': 35},
        'LEGENDARY': {'strength': 40, 'crit_damage': 50}
    },
    'enderman': {
        'COMMON': {'crit_damage': 5},
        'UNCOMMON': {'crit_damage': 10},
        'RARE': {'crit_damage': 15},
        'EPIC': {'crit_damage': 25, 'intelligence': 10},
        'LEGENDARY': {'crit_damage': 35, 'intelligence': 15}
    },
    'phoenix': {
        'EPIC': {'strength': 20, 'intelligence': 30},
        'LEGENDARY': {'strength': 35, 'intelligence': 50, 'health': 50}
    },
    'dragon': {
        'LEGENDARY': {'strength': 50, 'crit_damage': 50, 'crit_chance': 10, 'health': 100}
    },
    'bee': {
        'COMMON': {'farming_fortune': 5},
        'UNCOMMON': {'farming_fortune': 10},
        'RARE': {'farming_fortune': 20, 'speed': 5},
        'EPIC': {'farming_fortune': 30, 'speed': 10}
    },
    'elephant': {
        'COMMON': {'mining_fortune': 5, 'defense': 5},
        'UNCOMMON': {'mining_fortune': 10, 'defense': 10},
        'RARE': {'mining_fortune': 20, 'defense': 15},
        'EPIC': {'mining_fortune': 30, 'defense': 25, 'health': 25}
    },
    'giraffe': {
        'COMMON': {'foraging_fortune': 5},
        'UNCOMMON': {'foraging_fortune': 10},
        'RARE': {'foraging_fortune': 20, 'health': 10},
        'EPIC': {'foraging_fortune': 30, 'health': 20}
    },
    'dolphin': {
        'COMMON': {'fishing_speed': 5},
        'UNCOMMON': {'fishing_speed': 10},
        'RARE': {'fishing_speed': 15},
        'EPIC': {'fishing_speed': 25, 'sea_creature_chance': 5}
    },
    'rabbit': {
        'COMMON': {'speed': 10},
        'UNCOMMON': {'speed': 20},
        'RARE': {'speed': 30, 'health': 10},
        'EPIC': {'speed': 40, 'health': 20}
    },
    'sheep': {
        'COMMON': {'intelligence': 5},
        'UNCOMMON': {'intelligence': 10, 'ability_damage': 5},
        'RARE': {'intelligence': 15, 'ability_damage': 10},
        'EPIC': {'intelligence': 25, 'ability_damage': 15}
    },
    'pigman': {
        'EPIC': {'strength': 20, 'defense': 10, 'ferocity': 10},
        'LEGENDARY': {'strength': 35, 'defense': 20, 'ferocity': 20}
    },
    'bal': {
        'EPIC': {'mining_speed': 20, 'mining_fortune': 15},
        'LEGENDARY': {'mining_speed': 30, 'mining_fortune': 25}
    },
    'blaze': {
        'RARE': {'strength': 10, 'defense': 5},
        'EPIC': {'strength': 20, 'defense': 10, 'intelligence': 10},
        'LEGENDARY': {'strength': 30, 'defense': 20, 'intelligence': 20}
    },
    'silverfish': {
        'COMMON': {'mining_speed': 5},
        'UNCOMMON': {'mining_speed': 10, 'defense': 5},
        'RARE': {'mining_speed': 15, 'defense': 10}
    },
    'tiger': {
        'LEGENDARY': {'strength': 30, 'ferocity': 25, 'crit_chance': 5}
    },
    'lion': {
        'LEGENDARY': {'strength': 50, 'speed': 25, 'ferocity': 20}
    },
    'monkey': {
        'RARE': {'intelligence': 20, 'speed': 10},
        'EPIC': {'intelligence': 30, 'speed': 15, 'ability_damage': 10}
    },
    'parrot': {
        'EPIC': {'intelligence': 25, 'crit_damage': 15},
        'LEGENDARY': {'intelligence': 40, 'crit_damage': 25}
    },
    'turtle': {
        'RARE': {'defense': 30, 'health': 20},
        'EPIC': {'defense': 50, 'health': 40},
        'LEGENDARY': {'defense': 75, 'health': 60}
    },
    'chicken': {
        'COMMON': {'health': 10},
        'UNCOMMON': {'health': 20, 'speed': 5},
        'RARE': {'health': 30, 'speed': 10}
    }
}

class PetSelectView(View):
    def __init__(self, pets, user_id, bot):
        super().__init__(timeout=180)
        self.pets = pets
        self.user_id = user_id
        self.bot = bot
        self.page = 0
        self.items_per_page = 10
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.pets))
        
        if self.page > 0:
            prev_button = Button(label="◀️ Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if end_idx < len(self.pets):
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
        active_pet = next((p for p in self.pets if p['active']), None)
        
        embed = discord.Embed(
            title="🐾 Your Pets",
            description=f"You have {len(self.pets)} pets",
            color=discord.Color.orange()
        )
        
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
        
        embed.set_footer(text=f"Page {self.page + 1}/{math.ceil(len(self.pets) / self.items_per_page)} • Use /pet_equip to change active pet")
        return embed

class PetCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pets", description="View your pet collection")
    async def pets(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        pets = await self.bot.db.get_user_pets(interaction.user.id)
        
        if not pets:
            embed = discord.Embed(
                title="� Your Pets",
                description="You don't have any pets yet!\n\nPets can be obtained from:\n• Fishing (rare drops)\n• Combat (mob drops)\n• Events\n• Crafting",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)
            return
        
        view = PetSelectView(pets, interaction.user.id, self.bot)
        embed = await view.create_embed()
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="pet_equip", description="Equip a pet")
    @app_commands.describe(pet_type="The type of pet to equip", rarity="The rarity of the pet")
    async def pet_equip(self, interaction: discord.Interaction, pet_type: str, rarity: str):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        pets = await self.bot.db.get_user_pets(interaction.user.id)
        
        matching_pet = None
        for pet in pets:
            if pet['pet_type'].lower() == pet_type.lower() and pet['rarity'].upper() == rarity.upper():
                matching_pet = pet
                break
        
        if not matching_pet:
            await interaction.followup.send(f"❌ You don't have a {rarity.upper()} {pet_type.title()} pet!", ephemeral=True)
            return
        
        await self.bot.db.equip_pet(interaction.user.id, matching_pet['id'])
        
        rarity_color_hex = await self.bot.game_data.get_rarity_color(rarity.upper())
        if rarity_color_hex:
            color = int(rarity_color_hex.replace('#', ''), 16)
        else:
            rarity_colors_fallback = {
                'COMMON': 0x999999,
                'UNCOMMON': 0x55FF55,
                'RARE': 0x5555FF,
                'EPIC': 0xAA00AA,
                'LEGENDARY': 0xFFAA00,
                'MYTHIC': 0xFF55FF
            }
            color = rarity_colors_fallback.get(rarity.upper(), discord.Color.green())
        
        embed = discord.Embed(
            title="🐾 Pet Equipped!",
            description=f"You equipped your **{rarity.upper()} {pet_type.title()}** (Level {matching_pet['level']})!",
            color=color
        )
        
        stats = PET_STATS.get(pet_type.lower(), {}).get(rarity.upper(), {})
        level_multiplier = 1 + (matching_pet['level'] / 100)
        scaled_stats = {k: int(v * level_multiplier) for k, v in stats.items()}
        
        if scaled_stats:
            stats_str = "\n".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in scaled_stats.items()])
            embed.add_field(name="Stats", value=stats_str, inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pet_info", description="View detailed info about a pet")
    @app_commands.describe(pet_type="The type of pet")
    async def pet_info(self, interaction: discord.Interaction, pet_type: str):
        await interaction.response.defer()
        
        pet_type = pet_type.lower()
        
        all_pets = await self.bot.game_data.get_all_pet_stats()
        matching_pets = {k: v for k, v in all_pets.items() if v['pet_type'] == pet_type}
        
        if not matching_pets and pet_type not in PET_STATS:
            await interaction.followup.send(f"❌ Unknown pet type: {pet_type}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🐾 {pet_type.title()} Pet Info",
            description=f"All available rarities for {pet_type.title()}",
            color=discord.Color.blue()
        )
        
        if matching_pets:
            for pet_id, pet_data in matching_pets.items():
                rarity = pet_data['rarity']
                stats = pet_data.get('stats', {})
                stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in stats.items()])
                embed.add_field(
                    name=f"{rarity} (Level 1)",
                    value=stats_str,
                    inline=False
                )
        else:
            for rarity, stats in PET_STATS[pet_type].items():
                stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in stats.items()])
                embed.add_field(
                    name=f"{rarity} (Level 1)",
                    value=stats_str,
                    inline=False
                )
        
        embed.set_footer(text="Stats scale with pet level (up to +100% at level 100)")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pet_unequip", description="Unequip your current pet")
    async def pet_unequip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        active_pet = await self.bot.db.get_active_pet(interaction.user.id)
        
        if not active_pet:
            await interaction.followup.send("❌ You don't have any pet equipped!", ephemeral=True)
            return
        
        await self.bot.db.unequip_pet(interaction.user.id)
        
        embed = discord.Embed(
            title="🐾 Pet Unequipped",
            description=f"You unequipped your **{active_pet['rarity']} {active_pet['pet_type'].title()}**!",
            color=discord.Color.greyple()
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PetCommands(bot))

