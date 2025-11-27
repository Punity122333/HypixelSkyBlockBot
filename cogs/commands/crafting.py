import discord
from discord.ext import commands
from discord import app_commands

class CraftingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="craft", description="Craft an item")
    @app_commands.describe(item="Item ID to craft", quantity="Amount to craft")
    async def craft(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        await interaction.response.defer()
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        if quantity < 1:
            quantity = 1

        item_id = item.lower().replace(' ', '_')
        recipe_data = await self.bot.game_data.get_crafting_recipe(item_id)
        if not recipe_data:
            all_recipes = await self.bot.game_data.get_all_crafting_recipes()
            recipe = all_recipes.get(item_id)
        else:
            recipe = recipe_data.get('ingredients')

        if not recipe:
            await interaction.followup.send(f"❌ No recipe found for `{item}`!", ephemeral=True)
            return

        inventory = await self.bot.db.get_inventory(interaction.user.id)
        player_items = {}
        for inv_item in inventory:
            player_items[inv_item['item_id']] = player_items.get(inv_item['item_id'], 0) + 1

        missing = []
        for ing, amt in recipe.items():
            need = amt * quantity
            have = player_items.get(ing, 0)
            if have < need:
                missing.append(f"{need}x {ing.replace('_',' ').title()} (have {have})")

        if missing:
            embed = discord.Embed(title="❌ Missing Materials", description="You don't have enough materials.", color=discord.Color.red())
            embed.add_field(name="Missing", value="\n".join(missing), inline=False)
            await interaction.followup.send(embed=embed)
            return

        for ing, amt in recipe.items():
            await self.bot.db.remove_item_from_inventory(interaction.user.id, ing, amt * quantity)

        await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, quantity)

        obj = await self.bot.game_data.get_item(item_id)
        name = obj.name if obj else item.replace('_',' ').title()

        embed = discord.Embed(
            title="✅ Crafted!",
            description=f"You crafted **{quantity}x {name}**!",
            color=discord.Color.green()
        )

        s = "\n".join([f"• {amt * quantity}x {ing.replace('_',' ').title()}" for ing, amt in recipe.items()])
        embed.add_field(name="Materials Used", value=s, inline=False)
        embed.add_field(name="Result", value=f"{quantity}x {name}", inline=False)

        await interaction.followup.send(embed=embed)

    @craft.autocomplete('item')
    async def craft_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            all_recipes = await self.bot.game_data.get_all_crafting_recipes()
            
            choices = []
            for item_id in all_recipes.keys():
                item = await self.bot.game_data.get_item(item_id)
                if item:
                    item_name = item.name
                else:
                    item_name = item_id.replace('_', ' ').title()
                
                if current.lower() in item_name.lower() or current.lower() in item_id.lower():
                    choices.append(
                        app_commands.Choice(name=item_name, value=item_id)
                    )
            
            choices.sort(key=lambda x: x.name)
            return choices[:25]
        except Exception as e:
            print(f"Error in craft autocomplete: {e}")
            return []


    async def paginate(self, interaction, pages):
        for i, p in enumerate(pages):
            p.set_footer(text=f"Page {i+1}/{len(pages)}")
        await interaction.followup.send(embed=pages[0], view=self.PageView(self, pages, 0))

    class PageView(discord.ui.View):
        def __init__(self, cog, pages, current):
            super().__init__(timeout=120)
            self.cog = cog
            self.pages = pages
            self.current = current

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current = (self.current - 1) % len(self.pages)
            await interaction.response.edit_message(embed=self.pages[self.current], view=self)

        @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current = (self.current + 1) % len(self.pages)
            await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @app_commands.command(name="recipes", description="View available crafting recipes")
    async def view_recipes(self, interaction: discord.Interaction, filter_type: str = ""):
        await interaction.response.defer()
        all_recipes = await self.bot.game_data.get_all_crafting_recipes()
        pages = []
        batch = []
        for item_id, recipe in all_recipes.items():
            obj = await self.bot.game_data.get_item(item_id)
            if filter_type and obj and obj.type.lower() != filter_type.lower():
                continue
            name = obj.name if obj else item_id.replace('_',' ').title()
            line = ", ".join([f"{amt}x {ing.replace('_',' ').title()}" for ing, amt in recipe.items()])
            batch.append((name, line))
            if len(batch) == 10:
                embed = discord.Embed(title="📜 Crafting Recipes", color=discord.Color.blue())
                col1 = batch[:5]
                col2 = batch[5:]
                for n, r in col1:
                    embed.add_field(name=n, value=r, inline=True)
                for n, r in col2:
                    embed.add_field(name=n, value=r, inline=True)
                pages.append(embed)
                batch = []
        if batch:
            embed = discord.Embed(title="📜 Crafting Recipes", color=discord.Color.blue())
            col1 = batch[:5]
            col2 = batch[5:]
            for n, r in col1:
                embed.add_field(name=n, value=r, inline=True)
            for n, r in col2:
                embed.add_field(name=n, value=r, inline=True)
            pages.append(embed)
        if not pages:
            await interaction.followup.send("No recipes found.")
            return
        await self.paginate(interaction, pages)

    @app_commands.command(name="reforge", description="Reforge items")
    async def reforge(self, interaction: discord.Interaction, reforge: str):
        await interaction.response.defer()
        p = await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        rname = reforge.lower()
        rdata = await self.bot.game_data.get_reforge(rname)
        if not rdata:
            await interaction.followup.send("Unknown reforge.", ephemeral=True)
            return
        if p["coins"] < 5000:
            await interaction.followup.send("Not enough coins.", ephemeral=True)
            return
        await self.bot.player_manager.add_coins(interaction.user.id, -5000)
        embed = discord.Embed(title=f"{rname.title()} Applied", color=discord.Color.purple())
        s = "\n".join([f"+{v} {k.replace('_',' ').title()}" for k, v in rdata["stat_bonuses"].items()])
        embed.add_field(name="Bonuses", value=s, inline=False)
        embed.add_field(name="Cost", value="5000", inline=True)
        embed.add_field(name="Applies To", value=", ".join(rdata["applies_to"]), inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="reforges", description="View reforges")
    async def reforges(self, interaction: discord.Interaction):
        await interaction.response.defer()
        allr = await self.bot.game_data.get_all_reforges()
        pages = []
        batch = []
        for r in allr.values():
            stats = ", ".join([f"+{v} {k.replace('_',' ').title()}" for k, v in r["stat_bonuses"].items()])
            applies = ", ".join(r["applies_to"])
            batch.append((r["name"], stats, applies))
            if len(batch) == 10:
                embed = discord.Embed(title="⚡ Reforges", color=discord.Color.purple())
                col1 = batch[:5]
                col2 = batch[5:]
                for n, s, a in col1:
                    embed.add_field(name=f"{n} (5000)", value=f"{s}\nApplies: {a}", inline=True)
                for n, s, a in col2:
                    embed.add_field(name=f"{n} (5000)", value=f"{s}\nApplies: {a}", inline=True)
                pages.append(embed)
                batch = []
        if batch:
            embed = discord.Embed(title="⚡ Reforges", color=discord.Color.purple())
            col1 = batch[:5]
            col2 = batch[5:]
            for n, s, a in col1:
                embed.add_field(name=f"{n} (5000)", value=f"{s}\nApplies: {a}", inline=True)
            for n, s, a in col2:
                embed.add_field(name=f"{n} (5000)", value=f"{s}\nApplies: {a}", inline=True)
            pages.append(embed)
        await self.paginate(interaction, pages)

async def setup(bot):
    await bot.add_cog(CraftingCommands(bot))
