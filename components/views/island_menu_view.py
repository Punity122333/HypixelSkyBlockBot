import discord
import random
from components.buttons.island_buttons import (
    IslandSearchButton,
    IslandProgressButton,
    IslandRefreshButton
)
from components.modals.island_modals import IslandNameModal, PlaceDecorationModal


class IslandMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        
        self.add_item(IslandSearchButton(self))
        self.add_item(IslandProgressButton(self))
        self.add_item(IslandRefreshButton(self))
    
    async def get_embed(self):
        souls = await self.bot.db.get_fairy_souls(self.user_id)
        
        island_stats = await self.bot.db.island.get_island_stats(self.user_id)
        
        minion_count = island_stats['minion_count']
        max_minions = 25
        
        minion_display = f"{minion_count}/{max_minions} 🤖"
        if minion_count == 0:
            minion_status = "No minions placed yet!"
        elif minion_count < 5:
            minion_status = "Place more minions to boost production!"
        elif minion_count < 15:
            minion_status = "Good progress! Keep expanding."
        elif minion_count < max_minions:
            minion_status = "Impressive minion setup!"
        else:
            minion_status = "Maximum minions reached!"
        
        embed = discord.Embed(
            title=f"🏝️ {island_stats['island_name']}",
            description=f"**{self.username}'s** personal island in SkyBlock!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📊 Island Level", value=str(island_stats['island_level']), inline=True)
        embed.add_field(name="🎨 Theme", value=island_stats['theme'].replace('_', ' ').title(), inline=True)
        embed.add_field(name="✨ Fairy Souls", value=f"{souls}/242", inline=True)
        
        embed.add_field(
            name="🤖 Active Minions", 
            value=f"{minion_display}\n*{minion_status}*", 
            inline=False
        )
        
        embed.add_field(name="🎭 Decorations", value=f"{island_stats['decoration_count']}", inline=True)
        embed.add_field(name="🧱 Custom Blocks", value=f"{island_stats['block_count']}", inline=True)
        
        visitors_status = "✅ Enabled" if island_stats['visitors_enabled'] else "❌ Disabled"
        embed.add_field(name="👥 Visitors", value=visitors_status, inline=True)
        embed.add_field(name="⭐ Upgrade Points", value=str(island_stats['upgrade_points']), inline=True)
        
        embed.set_footer(text="Use buttons below to interact with your island | Place minions with /minions")
        return embed
    
    @discord.ui.button(label="Rename Island", style=discord.ButtonStyle.primary, emoji="✏️", row=1)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        modal = IslandNameModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Place Decoration", style=discord.ButtonStyle.primary, emoji="🎨", row=1)
    async def place_decoration_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        modal = PlaceDecorationModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="View Decorations", style=discord.ButtonStyle.secondary, emoji="📋", row=1)
    async def view_decorations_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        decorations = await self.bot.db.island.get_decorations(self.user_id)
        
        embed = discord.Embed(
            title="🎨 Island Decorations & Layout",
            description=f"Your island customization overview",
            color=discord.Color.purple()
        )
        
        if decorations:
            decoration_count = len(decorations)
            
            rarity_counts = {}
            type_counts = {}
            for deco in decorations:
                rarity = deco.get('rarity', 'COMMON')
                deco_type = deco.get('decoration_type', 'other')
                rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
                type_counts[deco_type] = type_counts.get(deco_type, 0) + 1
            
            embed.add_field(
                name="📊 Summary",
                value=f"Total: **{decoration_count}** decorations\nValue: Priceless! 💎",
                inline=False
            )
            
            rarity_text = []
            rarity_order = ['LEGENDARY', 'EPIC', 'RARE', 'UNCOMMON', 'COMMON']
            rarity_emoji = {
                'COMMON': '⚪',
                'UNCOMMON': '🟢',
                'RARE': '🔵',
                'EPIC': '🟣',
                'LEGENDARY': '🟠'
            }
            for rarity in rarity_order:
                if rarity in rarity_counts:
                    rarity_text.append(f"{rarity_emoji[rarity]} {rarity.title()}: {rarity_counts[rarity]}")
            
            if rarity_text:
                embed.add_field(
                    name="🏆 By Rarity",
                    value="\n".join(rarity_text),
                    inline=True
                )
            
            type_emoji = {
                'nature': '🌳',
                'structure': '🏛️',
                'lighting': '💡',
                'water': '💧',
                'furniture': '🪑',
                'path': '🛤️'
            }
            type_text = []
            for deco_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                emoji = type_emoji.get(deco_type, '🎨')
                type_text.append(f"{emoji} {deco_type.title()}: {count}")
            
            if type_text:
                embed.add_field(
                    name="🗂️ By Type",
                    value="\n".join(type_text[:5]),
                    inline=True
                )
            
            deco_list = []
            for i, deco in enumerate(decorations[:10], 1):
                rarity_emoji_single = rarity_emoji.get(deco['rarity'], '⚪')
                deco_list.append(
                    f"`{i}.` {rarity_emoji_single} **{deco['decoration_name']}** at ({deco['position_x']}, {deco['position_y']})"
                )
            
            if len(decorations) > 10:
                deco_list.append(f"*...and {len(decorations) - 10} more*")
            
            embed.add_field(
                name="📍 Placed Decorations",
                value="\n".join(deco_list),
                inline=False
            )
        else:
            embed.description = "No decorations placed yet! Start customizing your island."
            embed.add_field(
                name="💡 Getting Started",
                value="1. Browse 'Decoration Shop' button\n2. Click 'Place Decoration'\n3. Enter decoration details\n4. Watch your island come to life!",
                inline=False
            )
        
        embed.set_footer(text="Use 'Decoration Shop' button to buy more decorations | Place with 'Place Decoration' button")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Decoration Shop", style=discord.ButtonStyle.secondary, emoji="🏪", row=1)
    async def decoration_shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        decorations = await self.bot.db.island.get_available_decorations(self.user_id)
        
        embed = discord.Embed(
            title="🏪 Island Decoration Shop",
            description="Purchase decorations to customize your island!",
            color=discord.Color.gold()
        )
        
        rarity_colors = {
            'COMMON': '⚪',
            'UNCOMMON': '🟢',
            'RARE': '🔵',
            'EPIC': '🟣',
            'LEGENDARY': '🟠'
        }
        
        for deco in decorations[:15]:
            emoji = rarity_colors.get(deco['rarity'], '⚪')
            embed.add_field(
                name=f"{emoji} {deco['decoration_name']} ({deco['decoration_id']})",
                value=f"{deco['description']}\n💰 Cost: {deco['cost']:,} coins\n📊 Required Level: {deco['required_level']}\nSize: {deco['size_x']}x{deco['size_y']}",
                inline=True
            )
        
        embed.set_footer(text="Use the Place Decoration button to place items")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Change Theme", style=discord.ButtonStyle.secondary, emoji="🎭", row=2)
    async def change_theme_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        themes = await self.bot.db.island.get_available_themes(self.user_id)
        
        embed = discord.Embed(
            title="🎭 Available Island Themes",
            description="Purchase and apply themes to your island",
            color=discord.Color.blue()
        )
        
        for theme in themes[:10]:
            cost_text = f"{theme['cost']:,} coins" if theme['cost'] > 0 else "Free"
            requirement = f"\nRequirement: {theme['unlock_requirement']}" if theme['unlock_requirement'] else ""
            theme_id_display = f" (`{theme['theme_id']}`)"
            
            embed.add_field(
                name=f"{theme['theme_name']}{theme_id_display}",
                value=f"{theme['description']}\nCost: {cost_text}{requirement}",
                inline=False
            )
        
        embed.set_footer(text="To apply a theme, use Apply Theme button and enter theme ID")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Apply Theme", style=discord.ButtonStyle.secondary, emoji="✨", row=2)
    async def apply_theme_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        from components.modals.island_modals import ApplyThemeModal
        modal = ApplyThemeModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Toggle Visitors", style=discord.ButtonStyle.secondary, emoji="👥", row=2)
    async def toggle_visitors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your island!", ephemeral=True)
            return
        
        island = await self.bot.db.island.get_or_create_island(self.user_id)
        new_status = 0 if island.get('visitors_enabled', 1) else 1
        
        await self.bot.db.island.update_island(self.user_id, visitors_enabled=new_status)
        
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)