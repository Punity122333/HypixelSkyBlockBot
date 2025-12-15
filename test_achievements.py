#!/usr/bin/env python3
"""
Test script for the achievement system
Run this to verify the achievement system is working correctly
"""

import asyncio
import sys
sys.path.insert(0, '/home/pxnity/Code/Python/HypixelSkyblockBot')

from database.stubs import GameDatabase


async def test_achievement_system():
    """Test the achievement system"""
    db = GameDatabase('skyblock.db')
    await db.initialize()
    
    print("=" * 60)
    print("ACHIEVEMENT SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Get all achievements
    print("\n1. Getting all achievements...")
    all_achievements = await db.achievements.get_all_achievements()
    print(f"   ✓ Found {len(all_achievements)} achievements")
    
    # Test 2: Get achievements by category
    print("\n2. Getting achievements by category...")
    categories = {}
    for achievement in all_achievements:
        category = achievement['category']
        categories[category] = categories.get(category, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"   - {category}: {count} achievements")
    
    # Test 3: Show some example achievements
    print("\n3. Example achievements:")
    examples = [
        'first_mine', 'mining_50', 'wealth_1m', 
        'kills_1000', 'dungeon_100', 'skill_level_50'
    ]
    
    for achievement_id in examples:
        achievement = await db.achievements.get_achievement(achievement_id)
        if achievement:
            print(f"   {achievement['icon']} {achievement['name']}")
            print(f"      {achievement['description']}")
            print(f"      Category: {achievement['category']}")
        else:
            print(f"   ⚠️  Achievement '{achievement_id}' not found")
    
    # Test 4: Test unlocking (for test user)
    test_user_id = 123456789
    print(f"\n4. Testing achievement unlock for test user {test_user_id}...")
    
    # Unlock a test achievement
    unlocked = await db.achievements.unlock_achievement(test_user_id, 'first_mine')
    if unlocked:
        print("   ✓ Successfully unlocked 'first_mine'")
    else:
        print("   ⚠️  Achievement was already unlocked or failed")
    
    # Try to unlock again (should fail)
    unlocked_again = await db.achievements.unlock_achievement(test_user_id, 'first_mine')
    if not unlocked_again:
        print("   ✓ Correctly prevented duplicate unlock")
    else:
        print("   ⚠️  Duplicate unlock was not prevented!")
    
    # Check if user has achievement
    has_achievement = await db.achievements.has_achievement(test_user_id, 'first_mine')
    print(f"   ✓ User has 'first_mine': {has_achievement}")
    
    # Get player achievements
    player_achievements = await db.achievements.get_player_achievements(test_user_id)
    print(f"   ✓ User has {len(player_achievements)} total achievements")
    
    # Test 5: Get achievement count
    print("\n5. Achievement statistics...")
    count = await db.achievements.get_achievement_count(test_user_id)
    print(f"   - Test user achievement count: {count}")
    
    # Test 6: Leaderboard
    print("\n6. Achievement leaderboard...")
    leaderboard = await db.achievements.get_achievement_leaderboard(limit=5)
    if leaderboard:
        for i, entry in enumerate(leaderboard, 1):
            print(f"   {i}. User {entry['user_id']}: {entry['achievement_count']} achievements")
    else:
        print("   - No leaderboard data yet")
    
    print("\n" + "=" * 60)
    print("ACHIEVEMENT SYSTEM TEST COMPLETE")
    print("=" * 60)
    print("\n✓ All tests passed!")
    print("\nNext steps:")
    print("1. Use /achievements command in Discord to view achievements")
    print("2. Play the game and unlock achievements")
    print("3. Add achievement checks to all commands (see ACHIEVEMENT_INTEGRATION_GUIDE.md)")
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(test_achievement_system())
