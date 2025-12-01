import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from typing import TYPE_CHECKING
from utils.systems.party_system import PartySystem

if TYPE_CHECKING:
    from main import SkyblockBot


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


class PartyCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot
    
    @app_commands.command(name="party_create", description="Create a new party for dungeons")
    async def party_create(self, interaction: discord.Interaction):
        result = PartySystem.create_party(interaction.user.id, interaction.user.name)
        
        if result['success']:
            party = result['party']
            embed = discord.Embed(
                title="🎉 Party Created!",
                description=f"**Party Leader:** {party['leader_name']}\n**Party ID:** {party['party_id']}\n\nUse `/party_invite` to invite members!",
                color=discord.Color.blue()
            )
            embed.add_field(name="Members", value=f"1/{party['max_members']}", inline=True)
            embed.set_footer(text="Party members can join you in dungeon runs!")
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @app_commands.command(name="party_invite", description="Invite a player to your party")
    @app_commands.describe(user="The user to invite to your party")
    async def party_invite(self, interaction: discord.Interaction, user: discord.User):
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot invite yourself!", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ You cannot invite bots!", ephemeral=True)
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
            
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @app_commands.command(name="party_list", description="View your current party")
    async def party_list(self, interaction: discord.Interaction):
        party = PartySystem.get_party(interaction.user.id)
        
        if not party:
            await interaction.response.send_message("❌ You are not in a party! Use `/party_create` to create one.", ephemeral=True)
            return
        
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
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="party_leave", description="Leave your current party")
    async def party_leave(self, interaction: discord.Interaction):
        result = PartySystem.leave_party(interaction.user.id)
        
        if result['success']:
            if result.get('disbanded'):
                embed = discord.Embed(
                    title="👋 Party Disbanded",
                    description="You left the party and it has been disbanded.",
                    color=discord.Color.greyple()
                )
            elif 'new_leader' in result:
                new_leader = result['new_leader']
                embed = discord.Embed(
                    title="👋 Left Party",
                    description=f"You left the party. **{new_leader['username']}** is the new leader!",
                    color=discord.Color.greyple()
                )
            else:
                embed = discord.Embed(
                    title="👋 Left Party",
                    description="You left the party successfully.",
                    color=discord.Color.greyple()
                )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @app_commands.command(name="party_kick", description="Kick a member from your party (leader only)")
    @app_commands.describe(user="The user to kick from the party")
    async def party_kick(self, interaction: discord.Interaction, user: discord.User):
        result = PartySystem.kick_member(interaction.user.id, user.id)
        
        if result['success']:
            embed = discord.Embed(
                title="🚫 Member Kicked",
                description=f"**{user.name}** has been removed from the party.",
                color=discord.Color.orange()
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @app_commands.command(name="party_disband", description="Disband your party (leader only)")
    async def party_disband(self, interaction: discord.Interaction):
        result = PartySystem.disband_party(interaction.user.id)
        
        if result['success']:
            embed = discord.Embed(
                title="💥 Party Disbanded",
                description="Your party has been disbanded.",
                color=discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
    
    @app_commands.command(name="party_invites", description="View your pending party invites")
    async def party_invites(self, interaction: discord.Interaction):
        invites = PartySystem.get_pending_invites(interaction.user.id)
        
        if not invites:
            await interaction.response.send_message("📭 You have no pending party invites.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📬 Your Party Invites",
            description=f"You have {len(invites)} pending invite(s):",
            color=discord.Color.blue()
        )
        
        for invite in invites:
            expires_in = int(invite['expires_at'] - invite['created_at'])
            embed.add_field(
                name=f"From: {invite['inviter_name']}",
                value=f"Party ID: {invite['party_id']}\nExpires: <t:{int(invite['expires_at'])}:R>",
                inline=False
            )
        
        embed.set_footer(text="Use the buttons on the invite message to accept or decline")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PartyCommands(bot))
