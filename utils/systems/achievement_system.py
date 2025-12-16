from typing import List, Dict, Any
import discord
from utils.achievement_tracker import AchievementTracker


class AchievementSystem:
    
    @staticmethod
    async def check_and_notify(
        db,
        interaction: discord.Interaction,
        user_id: int,
        achievements: List[Dict[str, Any]]
    ):
        if not achievements:
            return
        
        title = "🏆 Achievement Unlocked!" if len(achievements) == 1 else "🏆 Achievements Unlocked!"
        description = "" if len(achievements) == 1 else f"You've unlocked {len(achievements)} achievements!"
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.gold()
        )
        
        for achievement in achievements:
            if achievement and 'name' in achievement and 'description' in achievement:
                icon = achievement.get('icon', '🏆')
                name = achievement.get('name', 'Unknown')
                description = achievement.get('description', '')
                embed.add_field(
                    name=f"{icon} {name}",
                    value=description,
                    inline=False
                )
        
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            try:
                from discord.abc import Messageable
                if interaction.channel and isinstance(interaction.channel, Messageable):
                    await interaction.channel.send(f"{interaction.user.mention}", embed=embed)
            except:
                pass
    
    @staticmethod
    async def check_skill_achievements(db, interaction: discord.Interaction, user_id: int, skill_name: str, level: int):
        """Check and unlock skill-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_skill(db, user_id, skill_name, level)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_wealth_achievements(db, interaction: discord.Interaction, user_id: int, wealth: int):
        """Check and unlock wealth-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_wealth(db, user_id, wealth)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_combat_achievements(db, interaction: discord.Interaction, user_id: int, kills: int = 0, wins: int = 0):
        """Check and unlock combat-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_combat(db, user_id, kills, wins)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_gathering_achievements(db, interaction: discord.Interaction, user_id: int, resource_type: str, amount: int):
        """Check and unlock gathering-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_gathering(db, user_id, resource_type, amount)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_collection_achievements(db, interaction: discord.Interaction, user_id: int, collection_name: str, tier: int):
        """Check and unlock collection-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_collection(db, user_id, collection_name, tier)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_dungeon_achievements(db, interaction: discord.Interaction, user_id: int, dungeon_count: int):
        """Check and unlock dungeon-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_dungeons(db, user_id, dungeon_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_slayer_achievements(db, interaction: discord.Interaction, user_id: int, slayer_count: int):
        """Check and unlock slayer-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_slayers(db, user_id, slayer_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_minion_achievements(db, interaction: discord.Interaction, user_id: int, minion_count: int):
        """Check and unlock minion-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_minions(db, user_id, minion_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_auction_achievements(db, interaction: discord.Interaction, user_id: int, auction_count: int):
        """Check and unlock auction-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_auctions(db, user_id, auction_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_bazaar_profit_achievements(db, interaction: discord.Interaction, user_id: int, profit: int):
        """Check and unlock bazaar profit achievements"""
        achievements = await AchievementTracker.check_and_unlock_bazaar_profit(db, user_id, profit)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_pet_achievements(db, interaction: discord.Interaction, user_id: int, pet_rarity: int = 0, pet_level: int = 0):
        """Check and unlock pet-related achievements"""
        achievements = await AchievementTracker.check_and_unlock_pets(db, user_id, pet_rarity, pet_level)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_fairy_soul_achievements(db, interaction: discord.Interaction, user_id: int, soul_count: int):
        """Check and unlock fairy soul achievements"""
        achievements = await AchievementTracker.check_and_unlock_fairy_souls(db, user_id, soul_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_hotm_achievements(db, interaction: discord.Interaction, user_id: int, hotm_tier: int):
        """Check and unlock HOTM tier achievements"""
        achievements = await AchievementTracker.check_and_unlock_hotm(db, user_id, hotm_tier)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_death_achievements(db, interaction: discord.Interaction, user_id: int, death_count: int):
        """Check and unlock death-related achievements (cursed)"""
        achievements = await AchievementTracker.check_and_unlock_deaths(db, user_id, death_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_boss_kill_achievements(db, interaction: discord.Interaction, user_id: int, boss_kill_count: int):
        """Check and unlock boss kill achievements"""
        achievements = await AchievementTracker.check_and_unlock_boss_kills(db, user_id, boss_kill_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_skill_average_achievements(db, interaction: discord.Interaction, user_id: int, skill_average: float):
        """Check and unlock skill average achievements"""
        achievements = await AchievementTracker.check_and_unlock_skill_average(db, user_id, skill_average)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_minion_tier_achievements(db, interaction: discord.Interaction, user_id: int, minion_tier: int):
        """Check and unlock minion tier achievements"""
        achievements = await AchievementTracker.check_and_unlock_minion_tier(db, user_id, minion_tier)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_minion_slots_achievements(db, interaction: discord.Interaction, user_id: int, slot_count: int):
        """Check and unlock minion slot achievements"""
        achievements = await AchievementTracker.check_and_unlock_minion_slots(db, user_id, slot_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_auction_win_achievements(db, interaction: discord.Interaction, user_id: int, auction_win_count: int):
        """Check and unlock auction win achievements"""
        achievements = await AchievementTracker.check_and_unlock_auction_wins(db, user_id, auction_win_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_bazaar_order_achievements(db, interaction: discord.Interaction, user_id: int, order_count: int):
        """Check and unlock bazaar order achievements"""
        achievements = await AchievementTracker.check_and_unlock_bazaar_orders(db, user_id, order_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_collections_tier_achievements(db, interaction: discord.Interaction, user_id: int, collection_count: int):
        """Check and unlock collection count achievements"""
        achievements = await AchievementTracker.check_and_unlock_collections_tier(db, user_id, collection_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_collections_maxed_achievements(db, interaction: discord.Interaction, user_id: int, maxed_count: int):
        """Check and unlock maxed collection achievements"""
        achievements = await AchievementTracker.check_and_unlock_collections_maxed(db, user_id, maxed_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_craft_achievements(db, interaction: discord.Interaction, user_id: int, craft_count: int):
        """Check and unlock crafting achievements"""
        achievements = await AchievementTracker.check_and_unlock_crafts(db, user_id, craft_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_enchant_achievements(db, interaction: discord.Interaction, user_id: int, enchant_count: int):
        """Check and unlock enchanting achievements"""
        achievements = await AchievementTracker.check_and_unlock_enchants(db, user_id, enchant_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_reforge_achievements(db, interaction: discord.Interaction, user_id: int, reforge_count: int):
        """Check and unlock reforging achievements"""
        achievements = await AchievementTracker.check_and_unlock_reforges(db, user_id, reforge_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_mithril_powder_achievements(db, interaction: discord.Interaction, user_id: int, powder_amount: int):
        """Check and unlock mithril powder achievements"""
        achievements = await AchievementTracker.check_and_unlock_mithril_powder(db, user_id, powder_amount)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_pets_owned_achievements(db, interaction: discord.Interaction, user_id: int, pet_count: int):
        """Check and unlock pet ownership achievements"""
        achievements = await AchievementTracker.check_and_unlock_pets_owned(db, user_id, pet_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_islands_visited_achievements(db, interaction: discord.Interaction, user_id: int, island_count: int):
        """Check and unlock island exploration achievements"""
        achievements = await AchievementTracker.check_and_unlock_islands_visited(db, user_id, island_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_bank_balance_achievements(db, interaction: discord.Interaction, user_id: int, balance: int):
        """Check and unlock bank balance achievements"""
        achievements = await AchievementTracker.check_and_unlock_bank_balance(db, user_id, balance)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_parties_joined_achievements(db, interaction: discord.Interaction, user_id: int, party_join_count: int):
        """Check and unlock party join achievements"""
        achievements = await AchievementTracker.check_and_unlock_parties_joined(db, user_id, party_join_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_parties_hosted_achievements(db, interaction: discord.Interaction, user_id: int, party_host_count: int):
        """Check and unlock party hosting achievements"""
        achievements = await AchievementTracker.check_and_unlock_parties_hosted(db, user_id, party_host_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_museum_donation_achievements(db, interaction: discord.Interaction, user_id: int, donation_count: int):
        """Check and unlock museum donation achievements"""
        achievements = await AchievementTracker.check_and_unlock_museum_donations(db, user_id, donation_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_quest_achievements(db, interaction: discord.Interaction, user_id: int, quest_count: int):
        """Check and unlock quest completion achievements"""
        achievements = await AchievementTracker.check_and_unlock_quests(db, user_id, quest_count)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_login_streak_achievements(db, interaction: discord.Interaction, user_id: int, streak_days: int):
        """Check and unlock login streak achievements"""
        achievements = await AchievementTracker.check_and_unlock_login_streak(db, user_id, streak_days)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_slayer_tier_achievements(db, interaction: discord.Interaction, user_id: int, slayer_tier: int):
        """Check and unlock slayer tier achievements"""
        achievements = await AchievementTracker.check_and_unlock_slayer_tier(db, user_id, slayer_tier)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def check_prestige_achievements(db, interaction: discord.Interaction, user_id: int, prestige_level: int):
        """Check and unlock prestige achievements"""
        achievements = await AchievementTracker.check_and_unlock_prestige(db, user_id, prestige_level)
        await AchievementSystem.check_and_notify(db, interaction, user_id, achievements)
    
    @staticmethod
    async def unlock_action_achievement(db, interaction: discord.Interaction, user_id: int, achievement_id: str):
        """Unlock an action-based achievement"""
        achievement = await AchievementTracker.check_and_unlock_action(db, user_id, achievement_id)
        if achievement:
            await AchievementSystem.check_and_notify(db, interaction, user_id, [achievement])
    
    @staticmethod
    async def unlock_single_achievement(db, interaction: discord.Interaction, user_id: int, achievement_id: str):
        """Unlock a specific achievement and notify"""
        achievement = await AchievementTracker.unlock_achievement(db, user_id, achievement_id)
        if achievement:
            await AchievementSystem.check_and_notify(db, interaction, user_id, [achievement])

