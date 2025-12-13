import discord
import asyncio

class _TrieNode:
        __slots__ = ("children", "items")
        def __init__(self):
            self.children = {}
            self.items = []


class _Trie:
    def __init__(self):
        self.root = _TrieNode()

    def insert(self, key: str, item_id: str):
        node = self.root
        for ch in key:
            if ch not in node.children:
                node.children[ch] = _TrieNode()
            node = node.children[ch]
        node.items.append(item_id)

    def search_prefix(self, prefix: str):

        norm = lambda s: s.lower().replace(' ', '').replace('_', '')
        prefix = norm(prefix)
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        stack = [node]
        out = []
        while stack:
            n = stack.pop()
            out.extend(n.items)
            for child in n.children.values():
                stack.append(child)
        return out

class RecipeSelectView(discord.ui.View):
    def __init__(self, bot, user_id, item_id, recipes, quantity):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.item_id = item_id
        self.recipes = recipes
        self.quantity = quantity
        
        for idx, recipe in enumerate(recipes):
            button = discord.ui.Button(
                label=f"Recipe {idx + 1}",
                style=discord.ButtonStyle.primary,
                custom_id=f"recipe_{idx}"
            )
            button.callback = self.create_callback(idx)
            self.add_item(button)
    
    def create_callback(self, recipe_idx):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your menu!", ephemeral=True)
                return
            
            await interaction.response.defer()
            selected_recipe = self.recipes[recipe_idx]
            await self.craft_with_recipe(interaction, selected_recipe)
        
        return callback
    
    async def craft_with_recipe(self, interaction, recipe_data):
        recipe = recipe_data['ingredients']
        output_amount = recipe_data.get('output_amount', 1)
        
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
            need = amt * self.quantity
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
            tasks.append(self.bot.db.remove_item_from_inventory(interaction.user.id, ing, amt * self.quantity))
        await asyncio.gather(*tasks)
        
        item_obj = await self.bot.game_data.get_item(self.item_id)
        is_pet = False
        if item_obj and hasattr(item_obj, 'type') and item_obj.type == 'PET':
            is_pet = True
        elif item_obj and isinstance(item_obj, dict) and item_obj.get('type') == 'PET':
            is_pet = True
        
        if is_pet:
            pet_type = self.item_id
            if '_' in self.item_id:
                parts = self.item_id.rsplit('_', 1)
                if len(parts) == 2 and parts[1].upper() in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC']:
                    pet_type = parts[0]
                    rarity = parts[1].upper()
                else:
                    pet_type = self.item_id
                    rarity = 'COMMON'
            else:
                rarity = 'COMMON'
            
            total_pets = self.quantity * output_amount
            for _ in range(total_pets):
                await self.bot.db.add_player_pet(interaction.user.id, pet_type, rarity)
        else:
            total_output = self.quantity * output_amount
            await self.bot.db.add_item_to_inventory(interaction.user.id, self.item_id, total_output)
        
        cog = self.bot.get_cog('CraftingCommands')
        name = await cog._resolve_item_name(self.item_id) if cog else self.item_id.replace('_', ' ').title()
        name = f"**{name}**"
        total_crafted = self.quantity * output_amount
        
        if output_amount > 1:
            craft_desc = f"You crafted **{self.quantity}x** recipes, producing **{total_crafted}x** {name}!"
        else:
            craft_desc = f"You crafted **{total_crafted}x** {name}!"
        
        embed = discord.Embed(title="✅ Crafted!", description=craft_desc, color=discord.Color.green())
        s = "\n".join([f"• **{amt * self.quantity}x** {ing.replace('_',' ').title()}" for ing, amt in recipe.items()])
        embed.add_field(name="Materials Used", value=s, inline=False)
        if is_pet:
            embed.add_field(name="Result", value=f"🐾 **{total_crafted}x** {name} added to your pet collection!", inline=False)
        else:
            embed.add_field(name="Result", value=f"**{total_crafted}x** {name}", inline=False)
        await interaction.followup.send(embed=embed)