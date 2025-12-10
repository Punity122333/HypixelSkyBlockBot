import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
from typing import Dict, List
from utils.autocomplete import recipe_autocomplete
from utils.normalize import normalize_item_id
from components.views.recipe_select_view import RecipeSelectView, _Trie

class CraftingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._recipes_cache = None
        self._recipes_cache_ts = 0
        self._cache_ttl = 5

    async def _load_all_recipes(self) -> Dict:
        now = time.time()
        if self._recipes_cache and now - self._recipes_cache_ts < self._cache_ttl:
            return self._recipes_cache
        all_recipes = await self.bot.game_data.get_all_crafting_recipes()
        if not isinstance(all_recipes, dict):
            all_recipes = {}
        self._recipes_cache = all_recipes
        self._recipes_cache_ts = now
        return all_recipes

    def _unwrap_recipe(self, entry):
        if entry is None:
            return None
        if isinstance(entry, dict):
            if "ingredients" in entry and isinstance(entry["ingredients"], dict):
                return entry["ingredients"]
            if all(isinstance(k, str) and isinstance(v, int) for k, v in entry.items()):
                return entry
        return None

    async def _resolve_item_name(self, item_id: str) -> str:
        try:
            obj = await self.bot.game_data.get_item(item_id)
            if obj and getattr(obj, "name", None):
                return obj.name
        except Exception:
            pass
        return item_id.replace("_", " ").title()

    @app_commands.command(name="craft", description="Craft an item")
    @app_commands.describe(item="Item ID to craft", quantity="Amount to craft")
    async def craft(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        try:
            await interaction.response.defer()
            await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
            if quantity < 1:
                quantity = 1
            item_id = normalize_item_id(item)
            
            recipes = await self.bot.db.get_crafting_recipes_by_output(item_id)
            if not recipes:
                all_recipes = await self._load_all_recipes()
                recipe_entry = all_recipes.get(item_id)
                recipe = self._unwrap_recipe(recipe_entry)
                output_amount = 1
                if recipe_entry and isinstance(recipe_entry, dict):
                    output_amount = recipe_entry.get('output_amount', 1)
                if not recipe:
                    await interaction.followup.send(f"❌ No recipe found for `{item}`!", ephemeral=True)
                    return
                recipes = [{'recipe_id': item_id, 'output_item': item_id, 'ingredients': recipe, 'output_amount': output_amount}]
            
            if len(recipes) > 1:
                view = RecipeSelectView(self.bot, interaction.user.id, item_id, recipes, quantity)
                embed = discord.Embed(
                    title=f"🔨 Select Recipe for {await self._resolve_item_name(item_id)}",
                    description=f"Multiple recipes found. Select which one to craft:",
                    color=discord.Color.blue()
                )
                for idx, rec in enumerate(recipes):
                    ing_list = "\n".join([f"• {amt}x {ing.replace('_', ' ').title()}" for ing, amt in rec['ingredients'].items()])
                    embed.add_field(
                        name=f"Recipe {idx + 1} (Output: {rec.get('output_amount', 1)}x)",
                        value=ing_list,
                        inline=False
                    )
                await interaction.followup.send(embed=embed, view=view)
                return
            
            recipe_data = recipes[0]
            recipe = recipe_data['ingredients']
            output_amount = recipe_data.get('output_amount', 1)
            if not recipe:
                await interaction.followup.send(f"❌ No recipe found for `{item}`!", ephemeral=True)
                return
            if output_amount < 1:
                output_amount = 1
            inventory = await self.bot.db.get_inventory(interaction.user.id)
            player_items = {}
            for inv_item in inventory:
                iid = inv_item.get("item_id") or inv_item.get("id")
                qty = inv_item.get("quantity") or inv_item.get("qty") or inv_item.get("count") or 1
                try:
                    qty = int(qty)
                except Exception:
                    qty = 1
                player_items[iid] = player_items.get(iid, 0) + qty
            missing = []
            for ing, amt in recipe.items():
                need = amt * quantity
                have = player_items.get(ing, 0)
                if have < need:
                    missing.append(f"{need}x {ing.replace('_', ' ').title()} (have {have})")
            if missing:
                embed = discord.Embed(title="❌ Missing Materials", description="You don't have enough materials.", color=discord.Color.red())
                embed.add_field(name="Missing", value="\n".join(missing), inline=False)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            tasks = []
            for ing, amt in recipe.items():
                tasks.append(self.bot.db.remove_item_from_inventory(interaction.user.id, ing, amt * quantity))
            await asyncio.gather(*tasks)
            
            item_obj = await self.bot.game_data.get_item(item_id)
            is_pet = False
            if item_obj and hasattr(item_obj, 'type') and item_obj.type == 'PET':
                is_pet = True
            elif item_obj and isinstance(item_obj, dict) and item_obj.get('type') == 'PET':
                is_pet = True
            
            if is_pet:
                pet_type = item_id
                if '_' in item_id:
                    parts = item_id.rsplit('_', 1)
                    if len(parts) == 2 and parts[1].upper() in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC']:
                        pet_type = parts[0]
                        rarity = parts[1].upper()
                    else:
                        pet_type = item_id
                        rarity = 'COMMON'
                else:
                    rarity = 'COMMON'
                
                total_pets = quantity * output_amount
                for _ in range(total_pets):
                    await self.bot.db.add_player_pet(interaction.user.id, pet_type, rarity)
            else:
                total_output = quantity * output_amount
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, total_output)
            
            name = await self._resolve_item_name(item_id)
            name = f"**{name}**"
            total_crafted = quantity * output_amount
            
            if output_amount > 1:
                craft_desc = f"You crafted **{quantity}x** recipes, producing **{total_crafted}x** {name}!"
            else:
                craft_desc = f"You crafted **{total_crafted}x** {name}!"
            
            embed = discord.Embed(title="✅ Crafted!", description=craft_desc, color=discord.Color.green())
            s = "\n".join([f"• **{amt * quantity}x** {ing.replace('_',' ').title()}" for ing, amt in recipe.items()])
            embed.add_field(name="Materials Used", value=s, inline=False)
            if is_pet:
                embed.add_field(name="Result", value=f"🐾 **{total_crafted}x** {name} added to your pet collection!", inline=False)
            else:
                embed.add_field(name="Result", value=f"**{total_crafted}x** {name}", inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"An error occurred while crafting. {e}", ephemeral=True)


    @craft.autocomplete("item")
    async def craft_autocomplete(self, interaction: discord.Interaction, current: str):
        return await recipe_autocomplete(interaction, current)

    async def paginate(self, interaction, pages: List[discord.Embed]):
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
        try:
            await interaction.response.defer()
            all_recipes = await self._load_all_recipes()
            pages = []
            batch = []
            for item_id, entry in all_recipes.items():
                recipe = self._unwrap_recipe(entry)
                if not recipe:
                    continue
                obj = None
                try:
                    obj = await self.bot.game_data.get_item(item_id)
                except Exception:
                    obj = None
                if filter_type and obj and getattr(obj, "type", None) and obj.type.lower() != filter_type.lower():
                    continue
                name = obj.name if obj and getattr(obj, "name", None) else item_id.replace("_", " ").title()
                name = f"{name}" if isinstance(entry, dict) and entry.get('output_amount', 1) > 1 else name
                line = ", ".join([f"{amt}x {ing.replace('_', ' ').title()}" for ing, amt in recipe.items()])
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
        except Exception as e:
            await interaction.followup.send(f"Failed to load recipes.\n {e}", ephemeral=True)

    @app_commands.command(name="reforge", description="Reforge items")
    async def reforge(self, interaction: discord.Interaction, reforge: str):
        try:
            await interaction.response.defer()
            p = await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
            rname = reforge.lower()
            rdata = await self.bot.game_data.get_reforge(rname)
            if not rdata:
                await interaction.followup.send("Unknown reforge.", ephemeral=True)
                return
            if p.get("coins", 0) < 5000:
                await interaction.followup.send("Not enough coins.", ephemeral=True)
                return
            await self.bot.player_manager.add_coins(interaction.user.id, -5000)
            embed = discord.Embed(title=f"{rname.title()} Applied", color=discord.Color.purple())
            s = "\n".join([f"+{v} {k.replace('_',' ').title()}" for k, v in rdata.get("stat_bonuses", {}).items()])
            embed.add_field(name="Bonuses", value=s or "None", inline=False)
            embed.add_field(name="Cost", value="5000", inline=True)
            embed.add_field(name="Applies To", value=", ".join(rdata.get("applies_to", [])), inline=True)
            await interaction.followup.send(embed=embed)
        except Exception:
            await interaction.followup.send("Failed to apply reforge.", ephemeral=True)

    @app_commands.command(name="reforges", description="View reforges")
    async def reforges(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            allr = await self.bot.game_data.get_all_reforges()
            pages = []
            batch = []
            for r in (allr or {}).values():
                stats = ", ".join([f"+{v} {k.replace('_',' ').title()}" for k, v in r.get("stat_bonuses", {}).items()])
                applies = ", ".join(r.get("applies_to", []))
                batch.append((r.get("name", "Unnamed"), stats, applies))
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
            if not pages:
                await interaction.followup.send("No reforges found.")
                return
            await self.paginate(interaction, pages)
        except Exception:
            await interaction.followup.send("Failed to load reforges.", ephemeral=True)

    @view_recipes.autocomplete("filter_type")
    async def view_recipes_autocomplete(self, interaction: discord.Interaction, current: str):
        q = (current or "").strip().lower()
        recipes = await self._load_all_recipes()
        if not recipes:
            return []

        if not hasattr(self, "_type_trie_ready"):
            type_names = {}
            for item_id in recipes:
                try:
                    obj = await self.bot.game_data.get_item(item_id)
                    t = obj.type if obj and getattr(obj, "type", None) else None
                    if t:
                        disp = t.replace("_", " ").title()
                        type_names[t.lower()] = t.title()
                except Exception:
                    continue
            self._type_names = type_names
            self._type_trie = _Trie()
            for t, disp in type_names.items():
                self._type_trie.insert(disp.lower(), t)
                self._type_trie.insert(t.lower(), t)
            self._type_trie_ready = True

        if not q:
            out = list(self._type_names.keys())[:25]
            out = sorted(out, key=lambda t: self._type_names[t].lower())
            return [app_commands.Choice(name=self._type_names[t], value=t) for t in out]

        from_prefix = self._type_trie.search_prefix(q)
        seen = set(from_prefix)
        partial = [t for t in self._type_names if q in t or q in self._type_names[t].lower()]
        for t in partial:
            if t not in seen:
                from_prefix.append(t)
        from_prefix.sort(key=lambda t: self._type_names[t].lower())
        from_prefix = from_prefix[:25]
        return [app_commands.Choice(name=self._type_names[t], value=t) for t in from_prefix]

async def setup(bot):
    await bot.add_cog(CraftingCommands(bot))
