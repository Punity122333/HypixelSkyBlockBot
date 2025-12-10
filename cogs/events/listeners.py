import discord
from discord.ext import commands

class EventListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided")
        else:
            print(f"Error: {error}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            embed = discord.Embed(
                title="👋 Welcome to SkyBlock!",
                description=f"Welcome {member.mention}! Use `/profile` to get started!",
                color=discord.Color.green()
            )
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EventListeners(bot))
