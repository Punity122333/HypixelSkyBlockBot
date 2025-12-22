import asyncio
import aiosqlite

async def run_migration():
    conn = await aiosqlite.connect('/home/pxnity/Code/Python/HypixelSkyblockBot/skyblock.db')
    conn.row_factory = aiosqlite.Row
    
    with open('/home/pxnity/Code/Python/HypixelSkyblockBot/migrations/scripts/072_add_intelligence_to_weapon_stats.sql', 'r') as f:
        sql = f.read()
    
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    for statement in statements:
        try:
            await conn.execute(statement)
            print(f"✓ Executed: {statement[:80]}...")
        except Exception as e:
            print(f"✗ Error executing statement: {statement[:80]}...")
            print(f"  Error: {e}")
    
    await conn.commit()
    await conn.close()
    print("\n✅ Migration 072 completed successfully!")

if __name__ == '__main__':
    asyncio.run(run_migration())
