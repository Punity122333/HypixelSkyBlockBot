import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from typing import Optional
from database import GameDatabase
from utils.player_manager import PlayerManager
from utils.systems.market_system import MarketSystem, run_market_simulation
from utils.systems.badge_system import BadgeSystem
from utils.data.game_data import GameDataManager
from utils.command_sync import CommandSyncManager
from utils.backup_manager import BackupManager
import pathlib
import asyncio
from discord.errors import PrivilegedIntentsRequired    

load_dotenv()
TOKEN = os.getenv('TOKEN')
APPLICATION_ID = os.getenv('APPID')
DEV_GUILD_ID = os.getenv('DEV_GUILD_ID')
DEV_GUILD_IDS = [gid.strip() for gid in DEV_GUILD_ID.split(',')] if DEV_GUILD_ID else []

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

class SkyblockBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db: GameDatabase
        self.player_manager: PlayerManager
        self.market_system: MarketSystem
        self.game_data: GameDataManager
        self.market_task: Optional[asyncio.Task] = None
        self.sync_manager: CommandSyncManager
        self.backup_manager: BackupManager

    async def setup_hook(self) -> None:
        print('🔄 Starting setup...')
        
        print('🗄️  Initializing database...')
        self.db = GameDatabase("skyblock.db")
        await self.db.initialize()
        
        print('📊 Loading game constants...')
        from utils.data.skills import _load_xp_requirements, _load_skill_bonuses, _load_collection_tiers
        from utils.systems.progression_system import ProgressionSystem
        from utils.systems.party_system import PartySystem
        from utils.systems.potion_system import PotionSystem
        from utils.systems.gathering_system import GatheringSystem
        
        await _load_xp_requirements(self.db)
        await _load_skill_bonuses(self.db)
        await _load_collection_tiers(self.db)
        await ProgressionSystem._load_constants(self.db)
        await PartySystem._load_constants(self.db)
        await PotionSystem._load_constants(self.db)
        await GatheringSystem._load_constants(self.db)
        
        self.player_manager = PlayerManager(self.db)
        self.market_system = MarketSystem(self.db)
        self.game_data = GameDataManager(self.db)
        
        print('🏪 Initializing market system...')
        await self.market_system.initialize(self.game_data)
        await self.db.init_bot_traders()
        await self.db.init_auction_bots()
        await self.db.init_stock_market()
        await self.market_system.update_bazaar_prices()
        
        print('🏅 Initializing badge system...')
        await BadgeSystem.initialize_badges(self.db)
        
        print('✅ Database, player manager, game data, and market system ready!')
        
        print('🔧 Initializing command sync manager...')
        self.sync_manager = CommandSyncManager(self)
        
        print('\n📦 Loading cogs...')
        await self.load_cogs()

        print(f'\n📋 Commands in tree: {len(self.tree.get_commands())}')
        for cmd in self.tree.get_commands():
            print(f'  - {cmd.name}')

        if DEV_GUILD_IDS:
            print(f'\n🏢 DEV MODE: Syncing commands to {len(DEV_GUILD_IDS)} guild(s)...')
            results = await self.sync_manager.batch_sync_guilds(
                guild_ids=[gid for gid in DEV_GUILD_IDS if gid],
                force=False,
                delay_between=2.0
            )
            
            total_synced = sum(count for count in results.values() if count > 0)
            failed_count = sum(1 for count in results.values() if count < 0)
            unchanged_count = sum(1 for count in results.values() if count == 0)
            
            print(f'\n📊 Sync Summary:')
            print(f'   ✅ Synced: {total_synced} commands')
            print(f'   ⏭️  Unchanged: {unchanged_count} guilds')
            if failed_count > 0:
                print(f'   ❌ Failed: {failed_count} guilds')
        else:
            print('\n🌍 PRODUCTION MODE: Syncing commands globally...')
            try:
                synced_count = await self.sync_manager.safe_sync(guild=None, force=False)
                if synced_count > 0:
                    print(f'✅ Synced {synced_count} commands globally (may take up to 1 hour to appear)')
                else:
                    print('✨ No changes detected, commands already up to date')
            except Exception as e:
                print(f'❌ Failed to sync globally: {e}')
                import traceback
                traceback.print_exc()
        
        print('\n🎉 Setup complete!')
        if DEV_GUILD_IDS:
            print(f'📝 Note: Commands synced to {len(DEV_GUILD_IDS)} dev guild(s) ONLY (not global)')
        
        print('🤖 Starting market simulation...')
        self.market_task = self.loop.create_task(self.market_simulation_loop())
        
        print('💾 Starting backup manager...')
        self.backup_manager = BackupManager("skyblock.db", backup_dir="backups", interval_hours=6, max_backups=10)
        self.backup_manager.start(self.loop)

    async def market_simulation_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                await run_market_simulation(self.db, self.market_system)
            except Exception as e:
                print(f'Market simulation error: {e}')
            await asyncio.sleep(300)

    async def load_cogs(self):
        cogs_dir = pathlib.Path("cogs")
        
        for category_dir in cogs_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('__'):
                continue
            
            for file_path in category_dir.rglob("*.py"):
                if file_path.name.startswith('__'):
                    continue
                
                relative_path = file_path.relative_to(pathlib.Path("."))
                cog_path = str(relative_path).replace(os.sep, '.')[:-3]
                
                try:
                    await self.load_extension(cog_path)
                    print(f'✅ Loaded {cog_path}')
                except Exception as e:
                    print(f'❌ Failed to load {cog_path}: {e}')

application_id = None
if APPLICATION_ID:
    try:
        application_id = int(APPLICATION_ID)
    except Exception:
        print('Invalid APPLICATION_ID in env; ignoring')

bot = SkyblockBot(command_prefix='/', intents=intents, application_id=application_id)

@bot.event
async def on_ready():
    if bot.user:
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    else:
        print('Logged in, but bot.user is None')
    print('------')

async def shutdown():
    print('\n🛑 Shutting down...')
    if bot.market_task:
        bot.market_task.cancel()
    if hasattr(bot, 'backup_manager'):
        bot.backup_manager.stop()
    if bot.db:
        await bot.db.close()
    print('✅ Cleanup complete')

if __name__ == '__main__':
    if TOKEN is None:
        raise ValueError('TOKEN environment variable not set')
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        import asyncio
        asyncio.run(shutdown())
    except PrivilegedIntentsRequired:
        print('\nPrivileged intents required but not enabled for this application.')
        print('Go to https://discord.com/developers/applications, open your application,')
        print('navigate to "Bot" and enable the "Server Members Intent" and/or "Presence Intent" as needed.')
        raise
