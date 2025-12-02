import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import math
from typing import Dict, List, Tuple

COG_CATEGORY_MAP = {
    'ProfileCommands': '👤 Profile & Stats',
    'BeginCommands': '👤 Profile & Stats',
    'IslandCommands': '👤 Profile & Stats',
    'ProgressionCommands': '👤 Profile & Stats',
    'LeaderboardCommands': '👤 Profile & Stats',
    
    'BankCommands': '💰 Economy & Banking',
    'EconomyStatsCommands': '💰 Economy & Banking',
    
    'InventoryCommands': '🎒 Inventory & Items',
    'CollectionCommands': '🎒 Inventory & Items',
    
    'SkillCommands': '⛏️ Gathering & Skills',
    'GatheringCommands': '⛏️ Gathering & Skills',
    
    'CraftingCommands': '🔨 Crafting & Upgrading',
    'EnchantingCommands': '🔨 Crafting & Upgrading',
    
    'AuctionCommands': '🏪 Trading & Markets',
    'BazaarCommands': '🏪 Trading & Markets',
    'MarketplaceCommands': '🏪 Trading & Markets',
    'MerchantCommands': '🏪 Trading & Markets',
    
    'StockCommands': '📈 Stocks & Economy',
    
    'PetCommands': '🐾 Pets & Minions',
    'MinionCommands': '🐾 Pets & Minions',
    
    'QuestCommands': '📜 Quests & Collections',
    
    'CombatCommands': '🏰 Dungeons & Combat',
    'DungeonCommands': '🏰 Dungeons & Combat',
    'SlayerCommands': '🏰 Dungeons & Combat',
    
    'EventCommands': '🎪 Events & Calendar',
    
    'MiscCommands': '⚙️ Bot & Admin',
    'AdminCommands': '⚙️ Bot & Admin',
}

CATEGORY_ORDER = [
    '👤 Profile & Stats',
    '💰 Economy & Banking',
    '🎒 Inventory & Items',
    '⛏️ Gathering & Skills',
    '🔨 Crafting & Upgrading',
    '🏪 Trading & Markets',
    '📈 Stocks & Economy',
    '🐾 Pets & Minions',
    '📜 Quests & Collections',
    '🏰 Dungeons & Combat',
    '🎪 Events & Calendar',
    '⚙️ Bot & Admin',
]

def get_command_categories(bot: commands.Bot) -> Dict[str, List[Tuple[str, str]]]:
    categories: Dict[str, List[Tuple[str, str]]] = {category: [] for category in CATEGORY_ORDER}
    categories['📋 Other Commands'] = []
    
    for cmd in bot.tree.get_commands():
        if isinstance(cmd, (app_commands.Command, app_commands.Group)):
            cmd_name = cmd.name
            cmd_description = cmd.description or 'No description available'
            
            category = '📋 Other Commands'
            
            binding = getattr(cmd, 'binding', None)
            if binding is not None:
                cog_name = binding.__class__.__name__
                category = COG_CATEGORY_MAP.get(cog_name, '📋 Other Commands')
            
            categories[category].append((cmd_name, cmd_description))
    
    categories = {cat: cmds for cat, cmds in categories.items() if cmds}

    for category in categories:
        categories[category].sort(key=lambda x: x[0])
    
    return categories

class HelpView(View):
    def __init__(self, user_id, command_categories: Dict[str, List[Tuple[str, str]]]):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.page = 0
        self.command_categories = command_categories
        self.categories = list(command_categories.keys())
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        if self.page > 0:
            prev_button = Button(label="Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if self.page < len(self.categories) - 1:
            next_button = Button(label="Next", style=discord.ButtonStyle.gray)
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page -= 1
        self.add_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page += 1
        self.add_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_embed(self):
        embed = discord.Embed(
            title="SkyBlock Bot Commands",
            description="All available commands organized by category",
            color=discord.Color.blue()
        )
        
        total_commands = sum(len(cmds) for cmds in self.command_categories.values())
        
        for category_name, commands_list in self.command_categories.items():
            if not commands_list:
                continue
            commands_text = "\n".join([f"`/{cmd}` - {desc}" for cmd, desc in commands_list])
            embed.add_field(
                name=category_name,
                value=commands_text,
                inline=False
            )
        
        embed.set_footer(text=f"Total: {total_commands} commands | Use /claim_starter_pack to begin!")
        return embed

class WikiPaginationView(View):
    def __init__(self, pages: list, title: str):
        super().__init__(timeout=180)
        self.pages = pages
        self.title = title
        self.current_page = 0
        self.update_buttons()
    
    def update_buttons(self):
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page >= len(self.pages) - 1
        self.last_page.disabled = self.current_page >= len(self.pages) - 1
    
    def get_embed(self):
        embed = discord.Embed(
            title=f"📚 {self.title} Wiki" if self.current_page == 0 else None,
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)}")
        return embed
    
    @discord.ui.button(label="First Page", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Last Page", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = len(self.pages) - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="View all available commands")
    async def help(self, interaction: discord.Interaction):
        command_categories = get_command_categories(self.bot)
        
        view = HelpView(interaction.user.id, command_categories)
        embed = view.create_embed()
        
        await interaction.response.send_message(embed=embed, view=view)


    @app_commands.command(name="wiki", description="Search the SkyBlock wiki")
    @app_commands.describe(query="What to search for")
    async def wiki(self, interaction: discord.Interaction, query: str):
        import os
        
        query_normalized = query.lower().strip().replace(' ', '_')
        
        wiki_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'wiki')
        wiki_file = os.path.join(wiki_path, f'{query_normalized}.txt')
        
        if os.path.exists(wiki_file):
            with open(wiki_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 4000:
                lines = content.split('\n')
                chunks = []
                current_chunk = ""
                
                for line in lines:
                    if len(current_chunk) + len(line) + 1 < 4000:
                        current_chunk += line + '\n'
                    else:
                        chunks.append(current_chunk)
                        current_chunk = line + '\n'
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                view = WikiPaginationView(chunks, query.title())
                embed = discord.Embed(
                    title=f"📚 {query.title()} Wiki",
                    description=chunks[0],
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Page 1/{len(chunks)}")
                
                await interaction.response.send_message(embed=embed, view=view)
            else:
                embed = discord.Embed(
                    title=f"📚 {query.title()} Wiki",
                    description=content,
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
        else:
            index_file = os.path.join(wiki_path, 'wiki_index.txt')
            suggestions = []
            
            if os.path.exists(index_file):
                with open(index_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 2:
                                keyword = parts[0].strip()
                                if query_normalized in keyword or keyword in query_normalized:
                                    suggestions.append(keyword.replace('_', ' '))
            
            if suggestions:
                suggestion_text = "\n".join([f"• {s}" for s in suggestions[:10]])
                embed = discord.Embed(
                    title=f"📚 No exact match for '{query}'",
                    description=f"Did you mean one of these?\n\n{suggestion_text}\n\nTry: `/wiki <topic>`",
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title=f"📚 Wiki topic not found: {query}",
                    description="Available topics:\n• getting_started\n• fairy_souls\n• dungeons\n• bazaar\n• coins\n• mining\n• farming\n• combat\n\nMore topics coming soon!",
                    color=discord.Color.red()
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="settings", description="Configure bot settings")
    async def settings(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚙️ Bot Settings",
            description="Configure your bot preferences",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Notifications",
            value="✅ Enabled",
            inline=True
        )
        embed.add_field(
            name="DM Alerts",
            value="❌ Disabled",
            inline=True
        )
        embed.add_field(
            name="Public Profile",
            value="✅ Enabled",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="claim_starter_pack", description="Claim your starter pack (one time only)")
    async def claim_starter_pack(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        
        if progression and progression.get('tutorial_completed'):
            await interaction.followup.send("❌ You've already claimed your starter pack!", ephemeral=True)
            return
        
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wooden_sword', 1)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wheat', 10)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'cobblestone', 20)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'oak_wood', 15)
        
        await self.bot.db.update_player(interaction.user.id, coins=player['coins'] + 500, total_earned=player.get('total_earned', 0) + 500)
        
        import time
        await self.bot.db.update_progression(
            interaction.user.id,
            tutorial_completed=1,
            first_mine_date=int(time.time())
        )
        
        embed = discord.Embed(
            title="🎁 Welcome to SkyBlock!",
            description="Your starter pack has been delivered!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Items Received",
            value="• Wooden Sword x1\n• Wheat x10\n• Cobblestone x20\n• Oak Wood x15\n• 500 coins",
            inline=False
        )
        
        embed.add_field(
            name="Getting Started",
            value="1. Use `/mine` to gather resources\n2. Use `/farm` to grow crops\n3. Sell items on `/bz_sell` for coins\n4. Buy better gear from `/ah_browse`\n5. Trade stocks with `/stocks`",
            inline=False
        )
        
        embed.set_footer(text="Your journey begins now! Work hard and build your fortune.")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MiscCommands(bot))