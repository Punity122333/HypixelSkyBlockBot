import discord
from discord.ext import commands
from discord import app_commands

class QuestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quests", description="View available quests")
    async def quests(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
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
        
        embed = discord.Embed(
            title="📜 Quest System",
            description="Complete quests to earn rewards!",
            color=discord.Color.gold()
        )
        
        active_quests = []
        completed_quests = []
        
        for quest in user_quests:
            quest_id = quest['quest_id']
            quest_info = await self.bot.game_data.get_game_quest(quest_id)
            if not quest_info:
                continue
            
            if quest_info['requirement_type'] == 'collection':
                current_amount = await self.bot.db.get_collection(interaction.user.id, quest_info['requirement_item'])
            else:
                current_amount = quest['progress']
            
            required_amount = quest_info['requirement_amount']
            
            if quest['completed'] and quest['claimed']:
                completed_quests.append(quest_info['name'])
            elif quest['completed'] and not quest['claimed']:
                active_quests.append(
                    f"{quest_info['name']}\n✅ COMPLETE - Use `/claim_quest {quest_id}` to claim!\nReward: {quest_info['reward_coins']:,} coins"
                )
            else:
                progress_bar = self.create_progress_bar(current_amount, required_amount)
                active_quests.append(
                    f"{quest_info['name']}\n{quest_info['description']}\nProgress: {current_amount}/{required_amount} {progress_bar}\nReward: {quest_info['reward_coins']:,} coins"
                )
                
                if current_amount >= required_amount and not quest['completed']:
                    await self.bot.db.complete_quest(interaction.user.id, quest_id)
        
        if active_quests:
            for i in range(0, len(active_quests), 3):
                batch = active_quests[i:i+3]
                for quest_str in batch:
                    embed.add_field(name="\u200b", value=quest_str, inline=False)
        
        if completed_quests:
            embed.add_field(
                name="✅ Completed Quests",
                value="\n".join(completed_quests[:10]) if len(completed_quests) <= 10 else f"{len(completed_quests)} quests completed!",
                inline=False
            )
        
        embed.set_footer(text="Use gathering commands to make progress!")
        
        await interaction.followup.send(embed=embed)
    
    def create_progress_bar(self, current: int, required: int, length: int = 10) -> str:
        filled = int((current / required) * length) if required > 0 else 0
        filled = min(filled, length)
        empty = length - filled
        return f"[{'█' * filled}{'░' * empty}]"

    @app_commands.command(name="claim_quest", description="Claim a completed quest reward")
    @app_commands.describe(quest_id="The ID of the quest to claim")
    async def claim_quest(self, interaction: discord.Interaction, quest_id: str):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
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

