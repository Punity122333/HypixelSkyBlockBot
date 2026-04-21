import discord
from discord.ext import commands
from discord import app_commands
from components.views.achievements_view import AchievementsMenuView


class AchievementsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @app_commands.command(name="achievements", description="View your achievements")
    @app_commands.describe(
        user="The user whose achievements you want to view (defaults to yourself)"
    )
    async def achievements(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        _ = await interaction.response.defer()

        target_user: discord.User | discord.Member = user or interaction.user

        view: AchievementsMenuView = AchievementsMenuView(
            self.bot, interaction.user.id, target_user
        )
        await view.load_data()
        embed: discord.Embed = await view.get_embed()

        _ = await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AchievementsCommands(bot))
