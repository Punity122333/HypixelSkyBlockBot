import functools
from discord import Interaction

def auto_defer(func):
    @functools.wraps(func)
    async def wrapper(self, interaction: Interaction, *args, **kwargs):
        await interaction.response.defer()
        return await func(self, interaction, *args, **kwargs)
    return wrapper
