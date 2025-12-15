import discord
import math
from components.views.minion_select_view import MinionSelectView
from components.views.minion_fuel_select_view import MinionFuelSelectView
from components.views.minion_skin_select_view import MinionSkinSelectView
from components.views.minion_upgrade_view import MinionUpgradeView
from components.views.minion_remove_view import MinionRemoveView

class MinionPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="minion_previous", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class MinionNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="minion_next", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = math.ceil(len(self.parent_view.minions) / self.parent_view.items_per_page)
        if self.parent_view.page < total_pages - 1:
            self.parent_view.page += 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class MinionRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.blurple, custom_id="minion_refresh", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.minions = await self.parent_view.bot.db.get_user_minions(self.parent_view.user_id)
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class MinionCollectButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💰 Collect All", style=discord.ButtonStyle.success, custom_id="minion_collect", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if not self.parent_view.minions:
            await interaction.response.send_message(
                "❌ You don't have any placed minions!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        total_collected = {}
        minions_collected = 0
        
        for minion in self.parent_view.minions:
            collected_items = await self.parent_view.bot.db.collect_minion(minion['id'])
            if collected_items:
                minions_collected += 1
                for item in collected_items:
                    item_name = item['item_id'].replace('_', ' ').title()
                    total_collected[item_name] = total_collected.get(item_name, 0) + item['amount']
        
        if not total_collected:
            await interaction.followup.send(
                "📦 No items to collect! Your minions are still working.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="💰 Minions Collected!",
            description=f"Collected from {minions_collected} minion(s):",
            color=discord.Color.green()
        )
        
        for item_name, amount in total_collected.items():
            embed.add_field(name=item_name, value=f"x{amount}", inline=True)
        
        self.parent_view.minions = await self.parent_view.bot.db.get_user_minions(self.parent_view.user_id)
        
        await interaction.followup.send(embed=embed)

class MinionRemoveButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🗑️ Remove", style=discord.ButtonStyle.danger, custom_id="minion_remove", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if not self.parent_view.minions:
            await interaction.response.send_message(
                "❌ You don't have any placed minions!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        options = []
        for i, minion in enumerate(self.parent_view.minions[:25]):
            options.append(
                discord.SelectOption(
                    label=f"{minion['minion_type'].title()} Minion (Tier {minion['tier']})",
                    description=f"Slot {minion.get('island_slot', i+1)}",
                    value=str(i)
                )
            )
        
        embed = discord.Embed(
            title="🗑️ Remove Minion",
            description="Select a minion to remove from your island. It will be returned to your inventory.",
            color=discord.Color.red()
        )
        
        for i, minion in enumerate(self.parent_view.minions[:25], start=1):
            embed.add_field(
                name=f"{i}. {minion['minion_type'].title()} Minion (Tier {minion['tier']})",
                value=f"Slot {minion.get('island_slot', i)}",
                inline=False
            )
        
        if len(self.parent_view.minions) > 25:
            embed.set_footer(text=f"Showing first 25 of {len(self.parent_view.minions)} minions")
        
        view = MinionRemoveView(self.parent_view.bot, self.parent_view.user_id, self.parent_view.minions[:25])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class MinionPlaceButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📦 Place Minion", style=discord.ButtonStyle.green, custom_id="minion_place", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        inventory = await self.parent_view.bot.db.get_inventory(self.parent_view.user_id)
        
        minion_items = []
        for item in inventory:
            item_data = await self.parent_view.bot.game_data.get_item(item['item_id'])
            if item_data:
                item_type = item_data.type if hasattr(item_data, 'type') else item_data.get('type') if isinstance(item_data, dict) else None
                if item_type == 'MINION':
                    if hasattr(item_data, 'name'):
                        item_name = item_data.name #type: ignore
                    elif isinstance(item_data, dict):
                        item_name = item_data.get('name', item['item_id'].replace('_', ' ').title())
                    else:
                        item_name = item['item_id'].replace('_', ' ').title()
                    minion_items.append({
                        'item_id': item['item_id'],
                        'name': item_name,
                        'amount': item['amount']
                    })
        
        if not minion_items:
            await interaction.followup.send(
                "❌ You don't have any minions in your inventory!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📦 Select Minion to Place",
            description="Choose which minion you want to place on your island:",
            color=discord.Color.green()
        )
        
        for i, minion in enumerate(minion_items[:25]):
            embed.add_field(
                name=f"{i+1}. {minion['name']}",
                value=f"Amount: {minion['amount']}",
                inline=True
            )
        
        if len(minion_items) > 25:
            embed.set_footer(text=f"Showing first 25 of {len(minion_items)} minions")
        
        view = MinionSelectView(self.parent_view.bot, self.parent_view.user_id, minion_items[:25])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class MinionUpgradeButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⬆️ Upgrade", style=discord.ButtonStyle.blurple, custom_id="minion_upgrade", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if not self.parent_view.minions:
            await interaction.response.send_message(
                "❌ You don't have any placed minions!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="⬆️ Upgrade Minion",
            description="Select a minion to upgrade to the next tier:",
            color=discord.Color.blue()
        )
        
        for i, minion in enumerate(self.parent_view.minions[:25], start=1):
            current_tier = minion['tier']
            upgrade_cost = 5000 * current_tier
            embed.add_field(
                name=f"{i}. {minion['minion_type'].title()} Minion (Tier {current_tier})",
                value=f"Upgrade to Tier {current_tier + 1} | Cost: {upgrade_cost:,} coins",
                inline=False
            )
        
        if len(self.parent_view.minions) > 25:
            embed.set_footer(text=f"Showing first 25 of {len(self.parent_view.minions)} minions")
        
        view = MinionUpgradeView(self.parent_view.bot, self.parent_view.user_id, self.parent_view.minions[:25])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class MinionFuelButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⛽ Add Fuel", style=discord.ButtonStyle.green, custom_id="minion_fuel", row=3)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if not self.parent_view.minions:
            await interaction.response.send_message(
                "❌ You don't have any placed minions!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        all_fuels = await self.parent_view.bot.db.game_data.fetchall(
            'SELECT * FROM game_minion_fuels',
            ()
        )
        
        inventory = await self.parent_view.bot.db.get_inventory(self.parent_view.user_id)
        
        fuel_items = []
        for fuel in all_fuels:
            for item in inventory:
                if item['item_id'] == fuel['fuel_id'] and item['amount'] > 0:
                    fuel_items.append({
                        'item_id': fuel['fuel_id'],
                        'name': fuel['name'],
                        'speed_boost': fuel['speed_boost'],
                        'duration': fuel['duration'],
                        'amount': item['amount']
                    })
                    break
        
        if not fuel_items:
            await interaction.followup.send(
                "❌ You don't have any minion fuels in your inventory!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="⛽ Select Fuel",
            description="Choose which fuel to apply to a minion:",
            color=discord.Color.green()
        )
        
        for i, fuel in enumerate(fuel_items[:25]):
            duration_hours = fuel['duration'] / 3600
            embed.add_field(
                name=f"{i+1}. {fuel['name']}",
                value=f"Speed: {fuel['speed_boost']}% | Duration: {duration_hours:.1f}h | Amount: {fuel['amount']}",
                inline=False
            )
        
        view = MinionFuelSelectView(self.parent_view.bot, self.parent_view.user_id, self.parent_view.minions, fuel_items[:25])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class MinionSkinButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🎨 Apply Skin", style=discord.ButtonStyle.blurple, custom_id="minion_skin", row=3)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if not self.parent_view.minions:
            await interaction.response.send_message(
                "❌ You don't have any placed minions!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        all_skins = await self.parent_view.bot.db.game_data.fetchall(
            'SELECT * FROM game_minion_skins',
            ()
        )
        
        inventory = await self.parent_view.bot.db.get_inventory(self.parent_view.user_id)
        
        skin_items = []
        for skin in all_skins:
            for item in inventory:
                if item['item_id'] == skin['skin_id'] and item['amount'] > 0:
                    skin_items.append({
                        'item_id': skin['skin_id'],
                        'name': skin['name'],
                        'minion_type': skin['minion_type'],
                        'rarity': skin['rarity'],
                        'amount': item['amount']
                    })
                    break
        
        if not skin_items:
            await interaction.followup.send(
                "❌ You don't have any minion skins in your inventory!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🎨 Select Skin",
            description="Choose which skin to apply to a minion:",
            color=discord.Color.blue()
        )
        
        for i, skin in enumerate(skin_items[:25]):
            embed.add_field(
                name=f"{i+1}. {skin['name']}",
                value=f"Type: {skin['minion_type'].title()} | Rarity: {skin['rarity']} | Amount: {skin['amount']}",
                inline=False
            )
        
        view = MinionSkinSelectView(self.parent_view.bot, self.parent_view.user_id, self.parent_view.minions, skin_items[:25])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)