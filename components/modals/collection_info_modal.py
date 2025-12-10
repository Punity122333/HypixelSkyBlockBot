import discord
from utils.normalize import normalize_item_id

class CollectionInfoModal(discord.ui.Modal, title="Collection Info"):
    item = discord.ui.TextInput(label="Item Name", placeholder="e.g., wheat", required=True)
    
    def __init__(self, bot, cog):
        super().__init__()
        self.bot = bot
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        item_id = normalize_item_id(self.item.value)
        
        tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
        
        if not tiers:
            await interaction.followup.send(f"❌ Collection not found for '{self.item.value}'!", ephemeral=True)
            return
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        amount = await self.bot.db.get_collection(interaction.user.id, item_id)
        tier = await self.cog.get_tier_for_amount(item_id, amount)
        category = await self.cog.get_category_for_item(item_id)
        
        embed = discord.Embed(
            title=f"📦 {self.item.value.title()} Collection",
            description=f"Category: {category.title() if category else 'Unknown'}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Current Tier", value=f"{tier}/10", inline=True)
        embed.add_field(name="Total Collected", value=f"{amount:,}", inline=True)
        
        tiers_info = ""
        tier_rewards = await self.bot.game_data.get_all_collection_tier_rewards()
        for i, req in enumerate(tiers):
            tier_num = i + 1
            status = "✅" if amount >= req else "🔒"
            reward = tier_rewards.get(tier_num, {})
            reward_text = f" → {reward.get('coins', 0):,} coins"
            if reward.get('recipes'):
                reward_text += f", {len(reward['recipes'])} recipe(s)"
            tiers_info += f"{status} Tier {tier_num}: {req:,}{reward_text}\n"
        
        embed.add_field(name="Tier Tree", value=tiers_info, inline=False)
        
        if tier < 10 and tier < len(tiers):
            next_tier = tier + 1
            next_req = tiers[tier]
            progress = (amount / next_req) * 100 if next_req > 0 else 100
            embed.add_field(
                name=f"Progress to Tier {next_tier}",
                value=f"{amount:,} / {next_req:,} ({progress:.1f}%)",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)