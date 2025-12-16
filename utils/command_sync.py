import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import hashlib
from typing import List, Dict, Optional, Union, Any
from pathlib import Path


class CommandSyncManager:
    def __init__(self, bot: commands.Bot, cache_file: str = ".command_cache.json"):
        self.bot = bot
        self.cache_file = Path(cache_file)
        self.command_hashes: Dict[str, Dict[str, str]] = {}
        self._load_cache()
    
    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.command_hashes = json.load(f)
            except Exception as e:
                print(f'⚠️  Failed to load command cache: {e}')
                self.command_hashes = {}
        else:
            self.command_hashes = {}
    
    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.command_hashes, f, indent=2)
        except Exception as e:
            print(f'⚠️  Failed to save command cache: {e}')
    
    def _hash_command(self, cmd: Union[app_commands.Command, app_commands.Group]) -> str:
        data: Dict[str, Any] = {
            'name': cmd.name,
            'description': cmd.description,
            'type': str(type(cmd).__name__),
        }
        
        if isinstance(cmd, app_commands.Command):
            if hasattr(cmd, 'callback') and hasattr(cmd.callback, '__code__'):
                data['callback'] = str(cmd.callback.__code__.co_code)
            
            if cmd.parameters:
                params = []
                for p in cmd.parameters:
                    param_data = {
                        'name': p.name,
                        'description': p.description,
                        'required': p.required,
                        'type': str(p.type) if hasattr(p, 'type') else None,
                        'default': str(p.default) if hasattr(p, 'default') else None,
                    }
                    if hasattr(p, 'choices') and p.choices:
                        param_data['choices'] = [{'name': c.name, 'value': str(c.value)} for c in p.choices]
                    params.append(param_data)
                data['parameters'] = params
        
        if isinstance(cmd, app_commands.Group):
            data['commands'] = [self._hash_command(c) for c in cmd.commands]
        
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _get_current_commands(self) -> Dict[str, str]:
        current = {}
        for cmd in self.bot.tree.get_commands():
            if isinstance(cmd, (app_commands.Command, app_commands.Group)):
                cmd_hash = self._hash_command(cmd)
                current[cmd.name] = cmd_hash
        return current
    
    def get_changed_commands(self, guild_id: Optional[str] = None) -> tuple[List[str], List[str], List[str]]:
        guild_key = guild_id if guild_id else "global"
        current = self._get_current_commands()
        cached = self.command_hashes.get(guild_key, {})
        
        current_names = set(current.keys())
        cached_names = set(cached.keys())
        
        new_commands = list(current_names - cached_names)
        removed_commands = list(cached_names - current_names)
        modified_commands = [
            name for name in (current_names & cached_names)
            if current[name] != cached[name]
        ]
        
        return new_commands, removed_commands, modified_commands
    
    async def safe_sync(
        self,
        guild: Optional[discord.Object] = None,
        force: bool = False
    ) -> int:
        guild_id = str(guild.id) if guild else None
        guild_key = guild_id if guild_id else "global"
        
        new, removed, modified = self.get_changed_commands(guild_id)
        
        if not force and not new and not removed and not modified:
            print(f'✨ No changes detected for {guild_key}, skipping sync')
            return 0
        
        if new or removed or modified:
            total_changes = len(new) + len(removed) + len(modified)
            print(f'📝 Changes detected for {guild_key}:')
            if new:
                print(f'   ✅ New: {", ".join(new)}')
            if removed:
                print(f'   ❌ Removed: {", ".join(removed)}')
            if modified:
                print(f'   🔄 Modified: {", ".join(modified)}')
            print(f'   Total: {total_changes} changes')
        
        try:
            if guild:
                synced = await self.bot.tree.sync(guild=guild)
            else:
                synced = await self.bot.tree.sync()
            
            current = self._get_current_commands()
            self.command_hashes[guild_key] = current
            self._save_cache()
            
            return len(synced)
        except discord.HTTPException as e:
            print(f'❌ Sync failed for {guild_key}: {e}')
            raise
    
    async def batch_sync_guilds(
        self,
        guild_ids: List[str],
        force: bool = False,
        delay_between: float = 2.0
    ) -> Dict[str, int]:
        results = {}
        
        for idx, guild_id in enumerate(guild_ids, 1):
            if not guild_id:
                continue
            
            guild = discord.Object(id=int(guild_id))
            print(f'\n🔄 [{idx}/{len(guild_ids)}] Processing guild {guild_id}...')
            
            try:
                self.bot.tree.copy_global_to(guild=guild)
                synced_count = await self.safe_sync(guild=guild, force=force)
                results[guild_id] = synced_count
                
                if synced_count > 0:
                    print(f'✅ Synced {synced_count} commands to guild {guild_id}')
                
                if idx < len(guild_ids):
                    await asyncio.sleep(delay_between)
                    
            except Exception as e:
                print(f'❌ Failed to sync guild {guild_id}: {e}')
                results[guild_id] = -1
                import traceback
                traceback.print_exc()
        
        return results
    
    def clear_cache(self, guild_id: Optional[str] = None):
        if guild_id:
            guild_key = guild_id
            if guild_key in self.command_hashes:
                del self.command_hashes[guild_key]
                print(f'🗑️  Cleared cache for guild {guild_id}')
        else:
            self.command_hashes = {}
            print('🗑️  Cleared all command cache')
        
        self._save_cache()
