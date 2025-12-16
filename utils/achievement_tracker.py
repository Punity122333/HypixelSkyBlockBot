from typing import Optional, Dict, Any, List

class AchievementTracker:
    """
    Dynamic achievement tracker that loads achievements from database
    instead of hardcoded constants. All achievement checks dynamically 
    query the database for achievement definitions.
    """
    
    @staticmethod
    async def unlock_achievement(db, user_id: int, achievement_id: str) -> Optional[Dict[str, Any]]:
        """
        Unlock an achievement for a user
        Returns the achievement data if newly unlocked, None otherwise
        """
        unlocked = await db.achievements.unlock_achievement(user_id, achievement_id)
        
        if unlocked:
            achievement = await db.achievements.get_achievement(achievement_id)
            return achievement
        
        return None
    
    @staticmethod
    async def check_value_based_achievements(db, user_id: int, requirement_type: str, current_value: int) -> List[Dict[str, Any]]:
        """
        Generic method to check achievements based on requirement_type and value
        Loads achievement definitions from database dynamically
        """
        achievements = []
        
        # Get all achievements of this requirement type from database
        all_achievements = await db.achievements.get_all_achievements()
        
        for achievement_data in all_achievements:
            if achievement_data.get('requirement_type') == requirement_type:
                requirement_value = achievement_data.get('requirement_value', 0)
                
                # Check if user meets requirement
                if current_value >= requirement_value:
                    result = await AchievementTracker.unlock_achievement(db, user_id, achievement_data['achievement_id'])
                    if result:
                        achievements.append(result)
        
        return achievements
    
    @staticmethod
    async def check_and_unlock_wealth(db, user_id: int, total_wealth: int) -> List[Dict[str, Any]]:
        """Check and unlock wealth-based achievements - loaded from database"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'coins', total_wealth)
    
    @staticmethod
    async def check_and_unlock_skill(db, user_id: int, skill_name: str, level: int) -> List[Dict[str, Any]]:
        """Check and unlock skill-based achievements - loaded from database"""
        achievements = []
        
        # Get all skill achievements from database
        all_achievements = await db.achievements.get_all_achievements()
        
        for achievement_data in all_achievements:
            achievement_id = achievement_data['achievement_id']
            
            # Check specific skill achievements (e.g., mining_5, farming_20)
            if achievement_id.startswith(f'{skill_name}_') and achievement_data.get('requirement_type') == 'skill_level':
                requirement_level = achievement_data.get('requirement_value', 0)
                if level >= requirement_level:
                    result = await AchievementTracker.unlock_achievement(db, user_id, achievement_id)
                    if result:
                        achievements.append(result)
            
            # Check general skill level achievements (skill_level_10, skill_level_25, skill_level_50)
            elif achievement_id.startswith('skill_level_') and achievement_data.get('requirement_type') == 'skill_level':
                requirement_level = achievement_data.get('requirement_value', 0)
                if level >= requirement_level:
                    result = await AchievementTracker.unlock_achievement(db, user_id, achievement_id)
                    if result:
                        achievements.append(result)
        
        return achievements
    
    @staticmethod
    async def check_and_unlock_combat(db, user_id: int, kills: int = 0, wins: int = 0) -> List[Dict[str, Any]]:
        """Check and unlock combat-based achievements - loaded from database"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'kills', kills)
    
    @staticmethod
    async def check_and_unlock_gathering(db, user_id: int, resource_type: str, amount: int) -> List[Dict[str, Any]]:
        """Check and unlock gathering-based achievements - dynamically from database"""
        achievements = []
        
        # The "action" type achievements like first_mine, first_farm are handled separately
        # This is primarily for "first time" achievements
        return achievements
    
    @staticmethod
    async def check_and_unlock_collection(db, user_id: int, collection_name: str, tier: int) -> List[Dict[str, Any]]:
        """Check and unlock collection-based achievements - loaded from database"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'collection_tier', tier)
    
    @staticmethod
    async def check_and_unlock_dungeons(db, user_id: int, dungeon_count: int) -> List[Dict[str, Any]]:
        """Check and unlock dungeon-based achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'dungeons', dungeon_count)
    
    @staticmethod
    async def check_and_unlock_slayers(db, user_id: int, slayer_count: int) -> List[Dict[str, Any]]:
        """Check and unlock slayer-based achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'slayers', slayer_count)
    
    @staticmethod
    async def check_and_unlock_minions(db, user_id: int, minion_count: int) -> List[Dict[str, Any]]:
        """Check and unlock minion-based achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'minions', minion_count)
    
    @staticmethod
    async def check_and_unlock_auctions(db, user_id: int, auction_count: int) -> List[Dict[str, Any]]:
        """Check and unlock auction-based achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'auctions', auction_count)
    
    @staticmethod
    async def check_and_unlock_deaths(db, user_id: int, death_count: int) -> List[Dict[str, Any]]:
        """Check and unlock death-based achievements (cursed)"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'deaths', death_count)
    
    @staticmethod
    async def check_and_unlock_bazaar_profit(db, user_id: int, total_profit: int) -> List[Dict[str, Any]]:
        """Check and unlock bazaar profit achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'profit', total_profit)
    
    @staticmethod
    async def check_and_unlock_fairy_souls(db, user_id: int, soul_count: int) -> List[Dict[str, Any]]:
        """Check and unlock fairy soul achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'fairy_souls', soul_count)
    
    @staticmethod
    async def check_and_unlock_pets(db, user_id: int, pet_rarity: int = 0, pet_level: int = 0) -> List[Dict[str, Any]]:
        """Check and unlock pet-based achievements"""
        achievements = []
        
        if pet_rarity > 0:
            rarity_achievements = await AchievementTracker.check_value_based_achievements(db, user_id, 'pet_rarity', pet_rarity)
            achievements.extend(rarity_achievements)
        
        if pet_level > 0:
            level_achievements = await AchievementTracker.check_value_based_achievements(db, user_id, 'pet_level', pet_level)
            achievements.extend(level_achievements)
        
        return achievements
    
    @staticmethod
    async def check_and_unlock_hotm(db, user_id: int, hotm_tier: int) -> List[Dict[str, Any]]:
        """Check and unlock HOTM tier achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'hotm_tier', hotm_tier)
    
    @staticmethod
    async def check_and_unlock_boss_kills(db, user_id: int, boss_kill_count: int) -> List[Dict[str, Any]]:
        """Check and unlock boss kill achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'boss_kills', boss_kill_count)
    
    @staticmethod
    async def check_and_unlock_skill_average(db, user_id: int, skill_average: float) -> List[Dict[str, Any]]:
        """Check and unlock skill average achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'skill_average', int(skill_average))
    
    @staticmethod
    async def check_and_unlock_minion_tier(db, user_id: int, minion_tier: int) -> List[Dict[str, Any]]:
        """Check and unlock minion tier achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'minion_tier', minion_tier)
    
    @staticmethod
    async def check_and_unlock_minion_slots(db, user_id: int, slot_count: int) -> List[Dict[str, Any]]:
        """Check and unlock minion slot achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'minion_slots', slot_count)
    
    @staticmethod
    async def check_and_unlock_auction_wins(db, user_id: int, auction_win_count: int) -> List[Dict[str, Any]]:
        """Check and unlock auction win achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'auction_wins', auction_win_count)
    
    @staticmethod
    async def check_and_unlock_bazaar_orders(db, user_id: int, order_count: int) -> List[Dict[str, Any]]:
        """Check and unlock bazaar order achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'bazaar_orders', order_count)
    
    @staticmethod
    async def check_and_unlock_collections_tier(db, user_id: int, collection_count: int) -> List[Dict[str, Any]]:
        """Check and unlock collection count achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'collections', collection_count)
    
    @staticmethod
    async def check_and_unlock_collections_maxed(db, user_id: int, maxed_count: int) -> List[Dict[str, Any]]:
        """Check and unlock maxed collection achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'collections_maxed', maxed_count)
    
    @staticmethod
    async def check_and_unlock_crafts(db, user_id: int, craft_count: int) -> List[Dict[str, Any]]:
        """Check and unlock crafting achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'crafts', craft_count)
    
    @staticmethod
    async def check_and_unlock_enchants(db, user_id: int, enchant_count: int) -> List[Dict[str, Any]]:
        """Check and unlock enchanting achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'enchants', enchant_count)
    
    @staticmethod
    async def check_and_unlock_reforges(db, user_id: int, reforge_count: int) -> List[Dict[str, Any]]:
        """Check and unlock reforging achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'reforges', reforge_count)
    
    @staticmethod
    async def check_and_unlock_mithril_powder(db, user_id: int, powder_amount: int) -> List[Dict[str, Any]]:
        """Check and unlock mithril powder achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'mithril_powder', powder_amount)
    
    @staticmethod
    async def check_and_unlock_pets_owned(db, user_id: int, pet_count: int) -> List[Dict[str, Any]]:
        """Check and unlock pet ownership achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'pets_owned', pet_count)
    
    @staticmethod
    async def check_and_unlock_islands_visited(db, user_id: int, island_count: int) -> List[Dict[str, Any]]:
        """Check and unlock island exploration achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'islands_visited', island_count)
    
    @staticmethod
    async def check_and_unlock_bank_balance(db, user_id: int, balance: int) -> List[Dict[str, Any]]:
        """Check and unlock bank balance achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'bank_balance', balance)
    
    @staticmethod
    async def check_and_unlock_parties_joined(db, user_id: int, party_join_count: int) -> List[Dict[str, Any]]:
        """Check and unlock party join achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'parties_joined', party_join_count)
    
    @staticmethod
    async def check_and_unlock_parties_hosted(db, user_id: int, party_host_count: int) -> List[Dict[str, Any]]:
        """Check and unlock party hosting achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'parties', party_host_count)
    
    @staticmethod
    async def check_and_unlock_museum_donations(db, user_id: int, donation_count: int) -> List[Dict[str, Any]]:
        """Check and unlock museum donation achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'museum_donations', donation_count)
    
    @staticmethod
    async def check_and_unlock_quests(db, user_id: int, quest_count: int) -> List[Dict[str, Any]]:
        """Check and unlock quest completion achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'quests_completed', quest_count)
    
    @staticmethod
    async def check_and_unlock_login_streak(db, user_id: int, streak_days: int) -> List[Dict[str, Any]]:
        """Check and unlock login streak achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'login_streak', streak_days)
    
    @staticmethod
    async def check_and_unlock_slayer_tier(db, user_id: int, slayer_tier: int) -> List[Dict[str, Any]]:
        """Check and unlock slayer tier achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'slayer_tier', slayer_tier)
    
    @staticmethod
    async def check_and_unlock_prestige(db, user_id: int, prestige_level: int) -> List[Dict[str, Any]]:
        """Check and unlock prestige achievements"""
        return await AchievementTracker.check_value_based_achievements(db, user_id, 'prestige', prestige_level)
    
    @staticmethod
    async def check_and_unlock_action(db, user_id: int, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Check and unlock action-based achievements"""
        return await AchievementTracker.unlock_achievement(db, user_id, achievement_id)
    
    @staticmethod
    async def format_achievement_notification(achievement: Dict[str, Any]) -> str:
        """Format an achievement unlock notification"""
        icon = achievement.get('icon', '🏆')
        name = achievement.get('name', 'Achievement')
        description = achievement.get('description', '')
        
        return f"{icon} **Achievement Unlocked!** {icon}\n**{name}**\n*{description}*"

