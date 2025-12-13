from typing import Optional, TYPE_CHECKING
import discord
from discord.ui import View, Button
import random
from utils.stat_calculator import StatCalculator
from utils.systems.puzzle_system import PuzzleSystem, Puzzle
from utils.systems.combat_system import CombatSystem
from utils.normalize import normalize_item_id
from utils.systems.party_system import PartySystem
from components.views.puzzle_view import PuzzleView
from utils.compat import roll_loot as compat_roll_loot
from utils.data.loot_tables import default_loot
from components.buttons.dungeon_buttons import (
    DungeonOpenDoorButton,
    DungeonSearchSecretsButton,
    DungeonExitButton,
    DungeonGetHintButton
)
from components.buttons.use_potion_button import UsePotionButton

if TYPE_CHECKING:
    from main import SkyblockBot

class DungeonView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, floor_name: str, floor_data: dict, party_id: Optional[int] = None):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.floor_name = floor_name
        self.floor_data = floor_data
        self.party_id = party_id
        self.rooms_cleared = 0
        self.total_rooms = 7
        self.current_health: Optional[int] = None
        self.max_health: Optional[int] = None
        self.keys = 0
        self.wither_doors_unlocked = 0
        self.blood_doors_unlocked = 0
        self.total_damage = 0
        self.secrets_found = 0
        self.max_secrets = 25
        self.crypts_opened = 0
        self.puzzles_failed = 0
        self.death_count = 0
        self.room_history = []
        self.coins_gained_in_run = 0
        self.current_puzzle: Optional[Puzzle] = None
        self.party_size = 1
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                self.party_size = len(party['members'])
        
        self.player_stats: Optional[dict] = None
        
        self.add_item(DungeonOpenDoorButton(self))
        self.add_item(DungeonSearchSecretsButton(self))
        self.add_item(DungeonExitButton(self))
        self.add_item(DungeonGetHintButton(self))
        self.add_item(UsePotionButton(self))
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your dungeon run!", ephemeral=True)
            return False
        return True
    
    def _format_puzzle_display(self, puzzle: Puzzle) -> str:
        puzzle_type = puzzle.puzzle_type
        data = puzzle.data
        
        if puzzle_type == 'sequence':
            if data.get('type') == 'color_simon':
                sequence_str = ' → '.join(data['sequence'])
                return f"**Color Sequence:**\n{sequence_str}\n*Type the emojis in order separated by spaces*"
            elif data.get('type') == 'number_sequence':
                sequence_str = ' → '.join(str(n) for n in data['sequence'])
                return f"**Number Sequence:**\n{sequence_str}\n*Type the numbers separated by spaces (e.g., 1 2 3)*"
            elif data.get('type') == 'direction_sequence':
                sequence_str = ' → '.join(data['sequence'])
                return f"**Direction Sequence:**\n{sequence_str}\n*Type the arrow emojis in order separated by spaces*"
        
        elif puzzle_type == 'memory':
            grid_size = data.get('grid_size', 2)
            grid = data.get('grid', [])
            
            if grid:
                grid_display = ""
                for row in grid:
                    grid_display += ' '.join(row) + "\n"
                return f"**Memory Grid ({grid_size}x{grid_size}):**\n{grid_display}\n*Study this grid! Type 'match' when ready.*"
            else:
                items = data.get('items', [])
                grid_display = ""
                for i in range(0, len(items), grid_size):
                    row = items[i:i+grid_size]
                    grid_display += ' '.join(row) + "\n"
                return f"**Memory Grid ({grid_size}x{grid_size}):**\n{grid_display}\n*Type 'match' to solve*"
        
        elif puzzle_type == 'pattern':
            if 'sequence' in data:
                sequence_str = ' '.join(data['sequence'])
                return f"**Pattern:**\n{sequence_str}"
        
        return ""
    
    async def check_puzzle_answer(self, message_content: str) -> bool:
        if not self.current_puzzle:
            return False
        
        is_correct, message = self.current_puzzle.attempt_solve(message_content)
        
        if is_correct:
            floor_difficulty = min(10, max(1, (self.rooms_cleared // 2) + 1))
            
            rewards = PuzzleSystem.calculate_puzzle_rewards(
                self.current_puzzle,
                floor_difficulty
            )
            
            self.coins_gained_in_run += rewards['coins']
            
            self.current_puzzle = None
            return True
        else:
            attempts_remaining = self.current_puzzle.max_attempts - self.current_puzzle.attempts
            if attempts_remaining <= 0:
                self.puzzles_failed += 1
                
                player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
                
                damage = PuzzleSystem.calculate_damage_on_failure(
                    self.current_puzzle.difficulty,
                    player_stats
                )
                
                self.current_health = (self.current_health or 0) - damage
                self.total_damage += damage
                
                self.current_puzzle = None
                return False
            return False
    
    async def _roll_dungeon_loot(self, floor_id: str, score: int, magic_find: float):
        dungeon_loot = await self.bot.db.get_dungeon_loot(floor_id, score)
        items = []

        if not dungeon_loot:
            dungeon_loot = self._get_default_dungeon_loot(floor_id)

        valid_loot = []
        for loot in dungeon_loot:
            req = loot.get('score_requirement') if isinstance(loot, dict) else loot['score_requirement']
            if req is None or score >= req:
                valid_loot.append(loot)

        for loot in valid_loot:
            if isinstance(loot, dict):
                drop_chance = loot.get('drop_chance', 0.1)
                item_id = loot.get('item_id')
                min_amount = loot.get('min_amount', 1)
                max_amount = loot.get('max_amount', 1)
            else:
                drop_chance = loot['drop_chance']
                item_id = loot['item_id']
                min_amount = loot['min_amount']
                max_amount = loot['max_amount']

            adjusted_chance = drop_chance * (1 + magic_find / 100)
            if random.random() < adjusted_chance:
                amount = random.randint(min_amount, max_amount)
                items.append((item_id, amount))

        return items

    def _get_default_dungeon_loot(self, floor_id: str):
        
        return default_loot.get(floor_id, default_loot.get('entrance', []))
    
    def _calculate_score(self) -> int:
        base_score = (self.rooms_cleared * 20)
        secret_bonus = (self.secrets_found * 5)
        death_penalty = (self.death_count * 25)
        door_bonus = (self.wither_doors_unlocked * 3) + (self.blood_doors_unlocked * 2)
        crypt_bonus = (self.crypts_opened * 5)
        puzzle_penalty = (self.puzzles_failed * 10)
        
        score = base_score + secret_bonus + door_bonus + crypt_bonus - death_penalty - puzzle_penalty
        
        return max(0, score)