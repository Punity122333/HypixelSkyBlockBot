import discord
from utils.systems.party_system import PartySystem

class PartyFinderCreateModal(discord.ui.Modal, title="Create Dungeon Party"):
    floor_input = discord.ui.TextInput(
        label="Floor (1-7)",
        placeholder="Enter floor number (1-7)",
        required=True,
        max_length=1
    )
    min_level_input = discord.ui.TextInput(
        label="Minimum Catacombs Level",
        placeholder="Enter minimum catacombs level",
        required=False,
        default="0",
        max_length=3
    )
    description_input = discord.ui.TextInput(
        label="Description (optional)",
        placeholder="Party description",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=200
    )
    
    def __init__(self, view):
        super().__init__()
        self.parent_view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            floor = int(self.floor_input.value)
            min_level = int(self.min_level_input.value) if self.min_level_input.value else 0
            description = self.description_input.value or ''
            
            if floor < 1 or floor > 7:
                await interaction.response.send_message("❌ Floor must be between 1 and 7", ephemeral=True)
                return
            
            requirements = {'min_catacombs_level': min_level}
            result = PartySystem.create_party(
                interaction.user.id,
                interaction.user.name,
                floor,
                requirements,
                description
            )
            
            if not result['success']:
                await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
                return
            
            self.parent_view.current_party_id = result['party_id']
            self.parent_view.current_view = 'party'
            await self.parent_view.load_parties()
            self.parent_view._update_buttons()
            embed = await self.parent_view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            
            stats = await self.parent_view.bot.db.get_dungeon_stats(interaction.user.id)
            if stats:
                total_parties_hosted = stats.get('parties_hosted', 0) + 1
                await self.parent_view.bot.db.update_dungeon_stats(interaction.user.id, parties_hosted=total_parties_hosted)
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_parties_hosted_achievements(self.parent_view.bot.db, interaction, interaction.user.id, total_parties_hosted)
            
        except ValueError as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class PartyFinderJoinModal(discord.ui.Modal, title="Join Dungeon Party"):
    party_id_input = discord.ui.TextInput(
        label="Party ID",
        placeholder="Enter party ID",
        required=True,
        max_length=10
    )
    dungeon_class_input = discord.ui.TextInput(
        label="Class",
        placeholder="healer, mage, berserker, archer, tank",
        required=True,
        max_length=20
    )
    
    def __init__(self, view):
        super().__init__()
        self.parent_view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            party_id = int(self.party_id_input.value)
            dungeon_class = self.dungeon_class_input.value.lower().strip()
            
            valid_classes = ['healer', 'mage', 'berserker', 'archer', 'tank']
            if dungeon_class not in valid_classes:
                await interaction.response.send_message(
                    f"❌ Invalid class. Choose from: {', '.join(valid_classes)}",
                    ephemeral=True
                )
                return
            
            result = PartySystem.join_party(
                party_id,
                interaction.user.id,
                interaction.user.name,
                dungeon_class
            )
            
            if result['success']:
                stats = await self.parent_view.bot.db.get_dungeon_stats(interaction.user.id)
                if stats:
                    total_parties_joined = stats.get('parties_joined', 0) + 1
                    await self.parent_view.bot.db.update_dungeon_stats(interaction.user.id, parties_joined=total_parties_joined)
                    
                    from utils.systems.achievement_system import AchievementSystem
                    await AchievementSystem.check_parties_joined_achievements(self.parent_view.bot.db, interaction, interaction.user.id, total_parties_joined)
                
                self.parent_view.current_party_id = party_id
                self.parent_view.current_view = 'party'
                await self.parent_view.load_parties()
                self.parent_view._update_buttons()
                embed = await self.parent_view.get_embed()
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
            else:
                await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Invalid party ID", ephemeral=True)
            return 