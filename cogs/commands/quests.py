import discord
from discord.ext import commands
from discord import app_commands
from components.views.quest_view import QuestMenuView

class QuestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quest", description="View and manage your quests")
    @app_commands.describe(claim="Quest ID, quest name, or serial number to claim (e.g., #1, #2)")
    async def quest(self, interaction: discord.Interaction, claim: str = ""):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if claim:
            quest_input = claim.strip()
            
            quests_from_db = await self.bot.game_data.get_all_game_quests()
            if quests_from_db:
                quest_data = {}
                for quest in quests_from_db:
                    quest_data[quest['quest_id']] = quest
            else:
                quest_data = {}
            
            for quest_id in quest_data.keys():
                existing_quest = await self.bot.db.get_quest(interaction.user.id, quest_id)
                if not existing_quest:
                    await self.bot.db.create_quest(interaction.user.id, quest_id, 0)
            
            user_quests = await self.bot.db.get_user_quests(interaction.user.id)
            
            quest_id = None
            if quest_input.startswith('#'):
                try:
                    serial = int(quest_input[1:])
                    if 1 <= serial <= len(user_quests):
                        quest_id = user_quests[serial - 1]['quest_id']
                    else:
                        await interaction.followup.send(f"❌ Quest #{serial} not found!", ephemeral=True)
                        return
                except ValueError:
                    await interaction.followup.send("❌ Invalid serial number format! Use #1, #2, etc.", ephemeral=True)
                    return
            else:
                for quest in user_quests:
                    qid = quest['quest_id']
                    qinfo = await self.bot.game_data.get_game_quest(qid)
                    if qinfo and (qid == quest_input or qinfo['name'].lower() == quest_input.lower()):
                        quest_id = qid
                        break
                if not quest_id:
                    await interaction.followup.send(f"❌ Quest '{quest_input}' not found!", ephemeral=True)
                    return
            
            quest = await self.bot.db.get_quest(interaction.user.id, quest_id)
            
            if not quest:
                await interaction.followup.send("❌ Quest not found!", ephemeral=True)
                return
            
            if not quest['completed']:
                await interaction.followup.send("❌ This quest is not completed yet!", ephemeral=True)
                return
            
            if quest['claimed']:
                await interaction.followup.send("❌ You already claimed this quest reward!", ephemeral=True)
                return
            
            quest_info = await self.bot.game_data.get_game_quest(quest_id)
            if not quest_info:
                await interaction.followup.send("❌ Invalid quest!", ephemeral=True)
                return
            
            await self.bot.player_manager.add_coins(interaction.user.id, quest_info['reward_coins'])
            
            for item_id, amount in quest_info['reward_items']:
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
            
            await self.bot.db.claim_quest_reward(interaction.user.id, quest_id)
            
            embed = discord.Embed(
                title="🎉 Quest Completed!",
                description=f"**{quest_info['name']}**\n{quest_info['description']}",
                color=discord.Color.green()
            )
            
            rewards_text = f"💰 {quest_info['reward_coins']:,} coins"
            if quest_info['reward_items']:
                items_text = ", ".join([f"{amount}x {item_id}" for item_id, amount in quest_info['reward_items']])
                rewards_text += f"\n🎁 {items_text}"
            
            embed.add_field(name="Rewards Claimed", value=rewards_text, inline=False)
            
            await interaction.followup.send(embed=embed)
        else:
            view = QuestMenuView(self.bot, interaction.user.id)
            await view.load_quests()
            embed = await view.get_embed()
            
            await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="daily_reward", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        reward, streak = await self.bot.db.claim_daily_reward(interaction.user.id)
        
        if reward == 0:
            embed = discord.Embed(
                title="❌ Already Claimed!",
                description="You've already claimed your daily reward today!",
                color=discord.Color.red()
            )
            embed.add_field(name="Current Streak", value=f"{streak} days", inline=True)
            embed.add_field(name="Next Reward", value="In 24 hours", inline=True)
        else:
            await self.bot.player_manager.add_coins(interaction.user.id, reward)
            
            embed = discord.Embed(
                title="🎁 Daily Reward Claimed!",
                description=f"You received {reward:,} coins!",
                color=discord.Color.green()
            )
            embed.add_field(name="Streak", value=f"{streak} days 🔥", inline=True)
            embed.add_field(name="Next Reward", value=f"{1000 + (streak + 1) * 500:,} coins", inline=True)
            
            if streak > 1:
                embed.add_field(name="Streak Bonus", value=f"+{500 * (streak - 1):,} coins", inline=True)
            
            if streak >= 7:
                embed.add_field(name="🔥 Weekly Streak!", value="You've maintained your streak for a week!", inline=False)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(QuestCommands(bot))

