import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import math

COMMAND_CATEGORIES = {
    '👤 Profile & Stats': [
        ('profile', 'View your player profile'),
        ('stats', 'View your stats'),
        ('skills', 'View your skill levels'),
        ('progression', 'View your progression and milestones')
    ],
    '💰 Economy & Banking': [
        ('bank', 'View your bank account'),
        ('deposit', 'Deposit coins into bank'),
        ('withdraw', 'Withdraw coins from bank'),
        ('pay', 'Pay coins to another player')
    ],
    '🎒 Inventory & Items': [
        ('inventory', 'View your inventory'),
        ('enderchest', 'View your ender chest'),
        ('wardrobe', 'Manage armor sets'),
        ('accessories', 'View accessory bag')
    ],
    '⛏️ Gathering & Skills': [
        ('mine', 'Mine for resources'),
        ('farm', 'Farm crops'),
        ('fish', 'Go fishing'),
        ('forage', 'Chop trees'),
        ('combat_mobs', 'Fight mobs')
    ],
    '🔨 Crafting & Upgrading': [
        ('craft', 'Craft items'),
        ('recipes', 'View crafting recipes'),
        ('reforge', 'Reforge items for better stats'),
        ('reforges', 'View available reforges'),
        ('enchant', 'Enchant items')
    ],
    '🏪 Trading & Markets': [
        ('ah_create', 'Create an auction'),
        ('ah_browse', 'Browse auctions'),
        ('ah_bid', 'Bid on auction'),
        ('ah_bin', 'Buy BIN auction'),
        ('ah_my', 'View your auctions'),
        ('bz_prices', 'View bazaar prices'),
        ('bz_buy', 'Buy from bazaar'),
        ('bz_sell', 'Sell to bazaar'),
        ('bz_order_buy', 'Place buy order'),
        ('bz_order_sell', 'Place sell order')
    ],
    '� Economy & Analysis': [
        ('stocks', 'View stock market'),
        ('stock_buy', 'Buy stocks'),
        ('stock_sell', 'Sell stocks'),
        ('portfolio', 'View portfolio'),
        ('flip_stats', 'View flip statistics'),
        ('market_trends', 'View market trends'),
        ('economy_overview', 'Economy overview')
    ],
    '🐾 Pets & Minions': [
        ('pets', 'View your pets'),
        ('pet_equip', 'Equip a pet'),
        ('pet_info', 'View pet info'),
        ('minions', 'View your minions'),
        ('minion_place', 'Place a minion'),
        ('minion_collect', 'Collect from minion')
    ],
    '📜 Quests & Collections': [
        ('quests', 'View active quests'),
        ('claim_quest', 'Claim quest reward'),
        ('daily', 'Claim daily reward'),
        ('collections', 'View collections'),
        ('starter_pack', 'Get starter items')
    ],
    '🏰 Dungeons & Combat': [
        ('dungeons', 'Enter dungeons'),
        ('slayer', 'Start slayer quest'),
        ('combat_stats', 'View combat stats')
    ],
    '🎪 Events & Calendar': [
        ('events', 'View active events'),
        ('calendar', 'View SkyBlock calendar')
    ],
    '🏆 Other Commands': [
        ('leaderboard', 'View leaderboards'),
        ('guide', 'Progression guide'),
        ('tips', 'Get trading tips'),
        ('progression_path', 'View tool progression')
    ]
}

class HelpView(View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.page = 0
        self.categories = list(COMMAND_CATEGORIES.keys())
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        if self.page > 0:
            prev_button = Button(label="◀️ Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if self.page < len(self.categories) - 1:
            next_button = Button(label="Next ▶️", style=discord.ButtonStyle.gray)
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
            title="� SkyBlock Bot Commands",
            description="All available commands organized by category",
            color=discord.Color.blue()
        )
        
        items_per_page = 3
        start_idx = self.page * items_per_page
        end_idx = min(start_idx + items_per_page, len(self.categories))
        
        for category_name in self.categories[start_idx:end_idx]:
            commands_list = COMMAND_CATEGORIES[category_name]
            commands_text = "\n".join([f"`/{cmd}` - {desc}" for cmd, desc in commands_list])
            
            embed.add_field(
                name=category_name,
                value=commands_text,
                inline=False
            )
        
        total_pages = math.ceil(len(self.categories) / items_per_page)
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Start with /starter_pack to begin!")
        
        return embed

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="View all available commands")
    async def help(self, interaction: discord.Interaction):
        view = HelpView(interaction.user.id)
        embed = view.create_embed()
        
        await interaction.response.send_message(embed=embed, view=view)


    @app_commands.command(name="wiki", description="Search the SkyBlock wiki")
    @app_commands.describe(query="What to search for")
    async def wiki(self, interaction: discord.Interaction, query: str):
        embed = discord.Embed(
            title=f"📚 Wiki Search: {query}",
            description=f"Search results for '{query}'",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Top Results",
            value=f"• {query} Guide\n• {query} Recipes\n• {query} Statistics",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

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
