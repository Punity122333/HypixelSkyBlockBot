import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import GameDatabase
from utils.game_data import GameData

async def fix_all_skill_levels():
    db = GameDatabase('skyblock.db')
    await db.initialize()
    
    game_data = GameData(db)
    
    print("Fetching all players with skills...")
    if not db.conn:
        print("Database not connected!")
        return
    
    cursor = await db.conn.execute('SELECT DISTINCT user_id FROM skills')
    user_rows = await cursor.fetchall()
    user_rows = list(user_rows)
    count = len(user_rows)

    total_users = len(user_rows)
    print(f"Found {total_users} users with skills")
    
    for idx, user_row in enumerate(user_rows, 1):
        user_id = user_row['user_id']
        print(f"Processing user {idx}/{total_users} (ID: {user_id})...")
        
        skills = await db.get_skills(user_id)
        
        for skill in skills:
            skill_name = skill['skill_name']
            current_xp = skill['xp']
            current_level = skill['level']
            
            correct_level = await game_data.calculate_level_from_xp(skill_name, current_xp)
            
            if correct_level != current_level:
                print(f"  Fixing {skill_name}: Level {current_level} -> {correct_level} (XP: {current_xp})")
                await db.update_skill(user_id, skill_name, level=correct_level)
            else:
                print(f"  {skill_name}: Level {current_level} is correct (XP: {current_xp})")
    
    await db.close()
    print("\nDone! All skill levels have been recalculated.")

if __name__ == "__main__":
    asyncio.run(fix_all_skill_levels())
