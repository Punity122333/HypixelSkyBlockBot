import discord
import random

class IslandSearchButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Search Fairy Soul", style=discord.ButtonStyle.blurple, custom_id="island_search", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        collected_locations_data = await self.parent_view.bot.db.get_fairy_soul_locations(self.parent_view.user_id)
        
        collected_locations = []
        if collected_locations_data:
            if isinstance(collected_locations_data, list):
                collected_locations = [loc if isinstance(loc, str) else loc.get('location', '') for loc in collected_locations_data if loc]
        
        all_locations_data = await self.parent_view.bot.game_data.get_all_fairy_soul_locations()
        all_locations = []
        if all_locations_data:
            if isinstance(all_locations_data, list):
                all_locations = [loc if isinstance(loc, str) else loc.get('location', '') for loc in all_locations_data if loc]
        
        uncollected = [loc for loc in all_locations if loc and loc not in collected_locations]
        
        if not uncollected:
            await interaction.followup.send("✨ You've collected all available fairy souls!", ephemeral=True)
            return
        
        found_chance = random.random()
        
        if found_chance < 0.3:
            location = random.choice(uncollected)
            success = await self.parent_view.bot.db.collect_fairy_soul(self.parent_view.user_id, location)
            
            if success:
                total_souls = await self.parent_view.bot.db.get_fairy_souls(self.parent_view.user_id)
                
                health_bonus = total_souls * 3
                mana_bonus = total_souls * 2
                
                player = await self.parent_view.bot.db.get_player(self.parent_view.user_id)
                base_health = 100
                base_mana = 20
                
                await self.parent_view.bot.db.update_player(
                    self.parent_view.user_id,
                    max_health=base_health + health_bonus,
                    max_mana=base_mana + mana_bonus
                )
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_fairy_soul_achievements(self.parent_view.bot.db, interaction, self.parent_view.user_id, total_souls)
                
                await interaction.followup.send(f"✨ **Fairy Soul Found!**\nYou found a fairy soul at **{location.replace('_', ' ')}**!\nTotal Souls: {total_souls}/{len(all_locations)}", ephemeral=True)
            else:
                await interaction.followup.send("✨ You've already collected this fairy soul!", ephemeral=True)
        else:
            await interaction.followup.send("🔍 You searched but didn't find a fairy soul this time. Keep searching!", ephemeral=True)

class IslandProgressButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Fairy Soul Progress", style=discord.ButtonStyle.green, custom_id="island_progress", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        souls = await self.parent_view.bot.db.get_fairy_souls(self.parent_view.user_id)
        
        health_bonus = souls * 3
        mana_bonus = souls * 2
        
        progress_pct = (souls / 242) * 100
        
        embed = discord.Embed(
            title="✨ Fairy Souls",
            description="Collect fairy souls for permanent stat bonuses!",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Collected", value=f"{souls} / 242", inline=True)
        embed.add_field(name="Progress", value=f"{progress_pct:.1f}%", inline=True)
        embed.add_field(name="Remaining", value=f"{242 - souls}", inline=True)
        
        embed.add_field(
            name="Current Bonuses",
            value=f"+{health_bonus} ❤️ Health\n+{mana_bonus} ✨ Mana",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class IslandRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.gray, custom_id="island_refresh", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
