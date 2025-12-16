import discord
from utils.systems.economy_system import EconomySystem
from utils.normalize import normalize_item_id

class AuctionCreateModal(discord.ui.Modal, title="Create Auction"):
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount (default: 1)", required=False, default="1")
    starting_bid = discord.ui.TextInput(label="Starting Bid", placeholder="Enter starting bid", required=True)
    duration_hours = discord.ui.TextInput(label="Duration (hours)", placeholder="1-48 hours", required=True)
    bin_price = discord.ui.TextInput(label="BIN Price (optional)", placeholder="Buy it now price", required=False)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value) if self.amount.value else 1
            starting_bid = int(self.starting_bid.value)
            duration_hours = int(self.duration_hours.value)
            bin_price = int(self.bin_price.value) if self.bin_price.value else 0
        except ValueError:
            await interaction.followup.send("❌ Invalid input values!", ephemeral=True)
            return
        item_id_normalized = normalize_item_id(self.item_id.value)
        item = await self.bot.game_data.get_item(item_id_normalized)
        if not item:
            await interaction.followup.send("❌ Invalid item!", ephemeral=True)
            return
        
        if duration_hours < 1 or duration_hours > 48:
            await interaction.followup.send("❌ Duration must be between 1 and 48 hours!", ephemeral=True)
            return
        
        item_count = await self.bot.db.get_item_count(interaction.user.id, item_id_normalized)
        if item_count < amount:
            await interaction.followup.send(f"❌ You don't have enough {item.name}!", ephemeral=True)
            return
        
        result = await EconomySystem.create_auction(self.bot.db, interaction.user.id, item_id_normalized, amount, starting_bid, duration_hours, bin_price if bin_price > 0 else None)
        
        if result['success']:
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'auction_created')
            auctions = await self.bot.db.get_user_auctions(interaction.user.id)
            if len(auctions) >= 1:
                await BadgeSystem.unlock_badge(self.bot.db, interaction.user.id, 'first_auction')
            if len(auctions) >= 100:
                await BadgeSystem.unlock_badge(self.bot.db, interaction.user.id, 'auction_100')
            
            player_economy = await self.bot.db.fetchone(
                'SELECT total_auctions FROM player_economy WHERE user_id = ?',
                (interaction.user.id,)
            )
            if player_economy:
                total_auctions = player_economy['total_auctions'] + 1
                await self.bot.db.execute(
                    'UPDATE player_economy SET total_auctions = ? WHERE user_id = ?',
                    (total_auctions, interaction.user.id)
                )
                await self.bot.db.commit()
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_auction_achievements(self.bot.db, interaction, interaction.user.id, total_auctions)
            
            await self.bot.db.remove_item_from_inventory(interaction.user.id, item_id_normalized, amount)
            embed = discord.Embed(title="✅ Auction Created!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{amount}x {item.name}", inline=True)
            embed.add_field(name="Starting Bid", value=f"{starting_bid:,} coins", inline=True)
            if bin_price > 0:
                embed.add_field(name="BIN Price", value=f"{bin_price:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Failed to create auction')}", ephemeral=True)
