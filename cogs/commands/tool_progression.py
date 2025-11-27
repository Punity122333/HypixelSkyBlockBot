import discord
from discord.ext import commands
from discord import app_commands

class ToolProgressionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="progression_path", description="View your tool progression path")
    async def progression_path(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        inventory = await self.bot.db.get_inventory(interaction.user.id)
        player_items = [item['item_id'] for item in inventory]
        
        embed = discord.Embed(
            title="🛠️ Tool Progression Path",
            description="Upgrade your tools to gather resources faster!",
            color=discord.Color.blue()
        )
        
        tool_tiers_from_db = await self.bot.game_data.get_all_tool_tiers()
        
        if tool_tiers_from_db:
            for tool_type, tiers in tool_tiers_from_db.items():
                current_tier = -1
                for tier_info in tiers:
                    if tier_info['item_id'] in player_items:
                        current_tier = tier_info['tier']
                
                status = ""
                for tier_info in tiers:
                    if tier_info['tier'] <= current_tier:
                        status += f"✅ {tier_info['name']}\n"
                    elif tier_info['tier'] == current_tier + 1:
                        status += f"⏭️ {tier_info['name']} (Next Upgrade)\n"
                        if tier_info.get('recipe'):
                            recipe_str = ", ".join([f"{amt}x {item}" for item, amt in tier_info['recipe'].items()])
                            status += f"   Recipe: {recipe_str}\n"
                    else:
                        status += f"🔒 {tier_info['name']}\n"
                
                embed.add_field(name=f"{tool_type.title().replace("_", " ")}s", value=status or "None", inline=False)
        
        embed.set_footer(text="Use /craft <item_id> to craft upgrades!")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ToolProgressionCommands(bot))
