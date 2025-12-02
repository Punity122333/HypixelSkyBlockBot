import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from typing import TYPE_CHECKING
from utils.systems.party_system import PartySystem

if TYPE_CHECKING:
    from main import SkyblockBot

class PartyInviteModal(discord.ui.Modal, title="Invite to Party"):
    user_id = discord.ui.TextInput(label="User ID", placeholder="Enter user ID to invite", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            target_user_id = int(self.user_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid user ID!", ephemeral=True)
            return
        
        if target_user_id == interaction.user.id:
            await interaction.followup.send("❌ You cannot invite yourself!", ephemeral=True)
            return
        
        try:
            user = await self.bot.fetch_user(target_user_id)
        except:
            await interaction.followup.send("❌ User not found!", ephemeral=True)
            return
        
        if user.bot:
            await interaction.followup.send("❌ You cannot invite bots!", ephemeral=True)
            return
        
        result = PartySystem.invite_to_party(interaction.user.id, user.id, user.name)
        
        if result['success']:
            invite = result['invite']
            embed = discord.Embed(
                title="🎊 Party Invite",
                description=f"{user.mention}, you've been invited to join **{invite['inviter_name']}'s** party!",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Invite expires in 5 minutes")
            
            view = PartyInviteView(user.id, invite['party_id'])
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)

class PartyKickModal(discord.ui.Modal, title="Kick Member"):
    user_id = discord.ui.TextInput(label="User ID", placeholder="Enter user ID to kick", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            target_user_id = int(self.user_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid user ID!", ephemeral=True)
            return
        
        result = PartySystem.kick_member(interaction.user.id, target_user_id)
        
        if result['success']:
            embed = discord.Embed(
                title="🚫 Member Kicked",
                description=f"Member has been removed from the party.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)

class PartyInviteView(View):
    def __init__(self, user_id: int, party_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.party_id = party_id
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This invite is not for you!", ephemeral=True)
            return
        
        result = PartySystem.accept_invite(interaction.user.id, self.party_id)
        
        if result['success']:
            party = result['party']
            embed = discord.Embed(
                title="✅ Joined Party!",
                description=f"You joined {party['leader_name']}'s party!",
                color=discord.Color.green()
            )
            embed.add_field(name="Party Members", value=f"{len(party['members'])}/{party['max_members']}", inline=True)
            
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This invite is not for you!", ephemeral=True)
            return
        
        result = PartySystem.decline_invite(interaction.user.id, self.party_id)
        
        embed = discord.Embed(
            title="❌ Invite Declined",
            description="You declined the party invite.",
            color=discord.Color.red()
        )
        
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)


class PartyMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
    
    async def get_embed(self):
        party = PartySystem.get_party(self.user_id)
        
        if not party:
            embed = discord.Embed(
                title="👥 Party System",
                description="You are not in a party. Create or join one!",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title=f"👥 {party['leader_name']}'s Party",
                description=f"**Party ID:** {party['party_id']}\n**Created:** <t:{int(party['created_at'])}:R>",
                color=discord.Color.blue()
            )
            
            members_text = ""
            for member in party['members']:
                leader_badge = "👑 " if member['user_id'] == party['leader_id'] else ""
                members_text += f"{leader_badge}**{member['username']}** (joined <t:{int(member['joined_at'])}:R>)\n"
            
            embed.add_field(name=f"Members ({len(party['members'])}/{party['max_members']})", value=members_text, inline=False)
            
            if party['in_dungeon']:
                embed.add_field(name="Status", value=f"🏰 In Dungeon: {party['dungeon_floor']}", inline=False)
            else:
                embed.add_field(name="Status", value="⏳ Waiting in lobby", inline=False)
        
        return embed
    
    @discord.ui.button(label="Create Party", style=discord.ButtonStyle.green, row=0)
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        result = PartySystem.create_party(self.user_id, self.username)
        
        if result['success']:
            await interaction.response.send_message("✅ Party created!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @discord.ui.button(label="Leave Party", style=discord.ButtonStyle.red, row=0)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        result = PartySystem.leave_party(self.user_id)
        
        if result['success']:
            if result.get('disbanded'):
                await interaction.response.send_message("👋 You left and the party was disbanded.", ephemeral=True)
            else:
                await interaction.response.send_message("👋 You left the party.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.gray, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="👥 Invite", style=discord.ButtonStyle.blurple, row=1)
    async def invite_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(PartyInviteModal(self.bot))
    
    @discord.ui.button(label="🚫 Kick", style=discord.ButtonStyle.red, row=1)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(PartyKickModal(self.bot))
    
    @discord.ui.button(label="💥 Disband", style=discord.ButtonStyle.red, row=1)
    async def disband_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        result = PartySystem.disband_party(interaction.user.id)
        
        if result['success']:
            embed = discord.Embed(
                title="💥 Party Disbanded",
                description="Your party has been disbanded.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot
    
    @app_commands.command(name="party", description="Manage your party")
    async def party(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        view = PartyMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PartyCommands(bot))
