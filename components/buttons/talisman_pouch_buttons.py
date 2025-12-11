import discord

class TalismanPouchButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📿 Talisman Pouch", style=discord.ButtonStyle.blurple, custom_id="talisman_pouch", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'talisman_pouch'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class AddTalismanButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="➕ Add Talisman", style=discord.ButtonStyle.green, custom_id="add_talisman", row=3)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        talismans = []
        inventory = await self.parent_view.bot.db.get_inventory(self.parent_view.user_id)
        
        for item_row in inventory:
            item_id = item_row['item_id']
            item = await self.parent_view.bot.game_data.get_item(item_id)
            if item and item.type == 'TALISMAN':
                talismans.append((item_id, item.name))
        
        if not talismans:
            await interaction.response.send_message("You don't have any talismans!", ephemeral=True)
            return
        
        class TalismanSelect(discord.ui.Select):
            def __init__(self, talismans_list, parent_button):
                self.parent_button = parent_button
                options = [
                    discord.SelectOption(label=name, value=talisman_id)
                    for talisman_id, name in talismans_list[:25]
                ]
                super().__init__(placeholder="Choose a talisman to add...", options=options)
            
            async def callback(self, interaction: discord.Interaction):
                from utils.systems.talisman_pouch_system import TalismanPouchSystem
                talisman_id = self.values[0]
                result = await TalismanPouchSystem.add_talisman_to_pouch(
                    self.parent_button.parent_view.bot.db,
                    self.parent_button.parent_view.user_id,
                    talisman_id
                )
                
                if result['success']:
                    await interaction.response.send_message(
                        f"✅ {result['message']}",
                        ephemeral=True
                    )
                    self.parent_button.parent_view.current_view = 'talisman_pouch'
                    await self.parent_button.parent_view.message.edit(
                        embed=await self.parent_button.parent_view.get_embed(),
                        view=self.parent_button.parent_view
                    )
                else:
                    await interaction.response.send_message(
                        f"❌ {result['message']}",
                        ephemeral=True
                    )
        
        view = discord.ui.View()
        view.add_item(TalismanSelect(talismans, self))
        await interaction.response.send_message("Select a talisman to add:", view=view, ephemeral=True)

class RemoveTalismanButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="➖ Remove Talisman", style=discord.ButtonStyle.red, custom_id="remove_talisman", row=3)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        from utils.systems.talisman_pouch_system import TalismanPouchSystem
        talismans = await TalismanPouchSystem.get_talisman_pouch(
            self.parent_view.bot.db,
            self.parent_view.user_id
        )
        
        if not talismans:
            await interaction.response.send_message("Your talisman pouch is empty!", ephemeral=True)
            return
        
        class TalismanRemoveSelect(discord.ui.Select):
            def __init__(self, talismans_list, parent_button):
                self.parent_button = parent_button
                options = []
                for talisman_data in talismans_list[:25]:
                    item = None
                    import asyncio
                    loop = asyncio.get_event_loop()
                    item = loop.run_until_complete(
                        parent_button.parent_view.bot.game_data.get_item(talisman_data['talisman_id'])
                    )
                    if item:
                        options.append(
                            discord.SelectOption(
                                label=item.name,
                                value=str(talisman_data['slot'])
                            )
                        )
                super().__init__(placeholder="Choose a talisman to remove...", options=options)
            
            async def callback(self, interaction: discord.Interaction):
                from utils.systems.talisman_pouch_system import TalismanPouchSystem
                slot = int(self.values[0])
                result = await TalismanPouchSystem.remove_talisman_from_pouch(
                    self.parent_button.parent_view.bot.db,
                    self.parent_button.parent_view.user_id,
                    slot
                )
                
                if result['success']:
                    await interaction.response.send_message(
                        "✅ Talisman removed from pouch!",
                        ephemeral=True
                    )
                    self.parent_button.parent_view.current_view = 'talisman_pouch'
                    await self.parent_button.parent_view.message.edit(
                        embed=await self.parent_button.parent_view.get_embed(),
                        view=self.parent_button.parent_view
                    )
                else:
                    await interaction.response.send_message(
                        f"❌ {result['message']}",
                        ephemeral=True
                    )
        
        view = discord.ui.View()
        view.add_item(TalismanRemoveSelect(talismans, self))
        await interaction.response.send_message("Select a talisman to remove:", view=view, ephemeral=True)
