import aiosqlite
import asyncio
import time

FAIRY_SOUL_LOCATIONS = [
    "village_well",
    "forest_tree",
    "mountain_peak",
    "lake_shore",
    "farm_field",
    "desert_cactus",
    "cave_entrance",
    "castle_tower",
    "beach_rock",
    "swamp_hut",
    # Add more locations as needed up to 242
]

TEST_USER_ID = 123456789  # Replace with actual user_id if needed

async def get_all_user_ids(db_path="skyblock.db"):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT user_id FROM players")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def populate_fairy_soul_locations(db_path="skyblock.db"):
    async with aiosqlite.connect(db_path) as db:
        for location in FAIRY_SOUL_LOCATIONS:
            await db.execute(
                "INSERT OR IGNORE INTO fairy_soul_locations (location) VALUES (?)",
                (location,)
            )
        await db.commit()
    print("✅ Populated fairy_soul_locations table.")

async def populate_player_fairy_souls(db_path="skyblock.db", user_id=TEST_USER_ID):
    async with aiosqlite.connect(db_path) as db:
        now = int(time.time())
        for location in FAIRY_SOUL_LOCATIONS[:5]:  # Simulate collecting 5 souls
            await db.execute(
                "INSERT OR IGNORE INTO fairy_souls (user_id, location, collected_at, souls_collected) VALUES (?, ?, ?, ?)",
                (user_id, location, now, 1)
            )
        await db.commit()
    print(f"✅ Populated fairy_souls table for user {user_id}.")

async def populate_all_player_fairy_souls(db_path="skyblock.db"):
    user_ids = await get_all_user_ids(db_path)
    async with aiosqlite.connect(db_path) as db:
        now = int(time.time())
        for user_id in user_ids:
            for location in FAIRY_SOUL_LOCATIONS:
                await db.execute(
                    "INSERT OR IGNORE INTO fairy_souls (user_id, location, collected_at, souls_collected) VALUES (?, ?, ?, ?)",
                    (user_id, location, now, 1)
                )
        await db.commit()
    print("✅ Populated all fairy souls for all users.")

async def main():
    await populate_fairy_soul_locations()
    await populate_all_player_fairy_souls()

if __name__ == "__main__":
    asyncio.run(main())
