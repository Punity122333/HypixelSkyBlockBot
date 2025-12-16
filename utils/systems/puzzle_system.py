from typing import Dict, Optional, Any, Tuple
import random


class PuzzleType:
    LOGIC = "logic"
    PATTERN = "pattern"
    SEQUENCE = "sequence"
    MEMORY = "memory"
    RIDDLE = "riddle"
    MATH = "math"


class Puzzle:
    def __init__(self, puzzle_type: str, difficulty: int, party_size: int = 1):
        self.puzzle_type = puzzle_type
        self.difficulty = difficulty
        self.party_size = party_size
        self.attempts = 0
        self.max_attempts = 3
        self.solved = False
        self.data = self._generate_puzzle_data()
    
    def _generate_puzzle_data(self) -> Dict[str, Any]:
        if self.puzzle_type == PuzzleType.LOGIC:
            return self._generate_logic_puzzle()
        elif self.puzzle_type == PuzzleType.PATTERN:
            return self._generate_pattern_puzzle()
        elif self.puzzle_type == PuzzleType.SEQUENCE:
            return self._generate_sequence_puzzle()
        elif self.puzzle_type == PuzzleType.MEMORY:
            return self._generate_memory_puzzle()
        elif self.puzzle_type == PuzzleType.RIDDLE:
            return self._generate_riddle_puzzle()
        elif self.puzzle_type == PuzzleType.MATH:
            return self._generate_math_puzzle()
        return {}
    
    def _generate_logic_puzzle(self) -> Dict[str, Any]:
        puzzles = [
            {
                'name': 'Three Skeletons',
                'description': 'A logical deduction puzzle',
                'question': 'Three wither skeletons guard three doors. One door leads to treasure, one to traps, and one circles back. One skeleton always lies, one always tells the truth, and one answers randomly. What do you ask?',
                'options': [
                    'Ask the first skeleton which door the second skeleton would say is safe',
                    'Ask all three skeletons which door is safe',
                    'Ask the first skeleton if the second is truthful, then ask the indicated door',
                    'Open doors at random'
                ],
                'correct_index': 0
            },
            {
                'name': 'Chest Code',
                'description': 'A mathematical deduction puzzle',
                'question': 'A chest requires a 4-digit code. Clues: All digits are different, sum is 20, first digit is 2x the last, middle two digits are consecutive.',
                'options': ['8254', '8365', '8452', '9254'],
                'correct_index': 1
            },
            {
                'name': 'Lever Combination',
                'description': 'A logical combination puzzle',
                'question': 'Five levers control a door. Red and blue must both be up or both down. Green must be opposite of red. Yellow must match blue. Orange is independent. What combination opens the door?',
                'options': [
                    'All up',
                    'Red up, Blue up, Green down, Yellow down, Orange up',
                    'Red down, Blue down, Green up, Yellow down, Orange up',
                    'All down'
                ],
                'correct_index': 2
            }
        ]
        
        puzzle = random.choice(puzzles)
        return puzzle
    
    def _generate_pattern_puzzle(self) -> Dict[str, Any]:
        patterns = [
            {
                'name': 'Color Pattern',
                'sequence': ['🟥', '🟦', '🟥', '🟦', '🟥', '?'],
                'options': ['🟥', '🟦', '🟩', '🟨'],
                'correct_index': 1,
                'description': 'Complete the pattern',
                'question': 'What color comes next?'
            },
            {
                'name': 'Growth Pattern',
                'sequence': ['⬜', '⬜⬜', '⬜⬜⬜', '⬜⬜⬜⬜', '?'],
                'options': ['⬜⬜⬜⬜', '⬜⬜⬜⬜⬜', '⬜⬜⬜', '⬜⬜'],
                'correct_index': 1,
                'description': 'What comes next in the sequence?',
                'question': 'Which option completes the pattern?'
            },
            {
                'name': 'Number Pattern',
                'sequence': ['2', '4', '8', '16', '?'],
                'options': ['20', '24', '32', '64'],
                'correct_index': 2,
                'description': 'Complete the number pattern',
                'question': 'What number comes next?'
            }
        ]
        
        puzzle = random.choice(patterns)
        return puzzle
    
    def _generate_sequence_puzzle(self) -> Dict[str, Any]:
        sequences = [
            {
                'name': 'Color Simon',
                'type': 'color_simon',
                'sequence': [random.choice(['🔴', '🔵', '🟢', '🟡']) for _ in range(3 + self.difficulty)],
                'description': 'Memorize and repeat this color sequence',
                'question': 'Repeat the color sequence you saw'
            },
            {
                'name': 'Number Sequence',
                'type': 'number_sequence',
                'sequence': [random.randint(1, 9) for _ in range(4 + self.difficulty)],
                'description': 'Remember this number sequence',
                'question': 'Enter the number sequence'
            },
            {
                'name': 'Direction Path',
                'type': 'direction_sequence',
                'sequence': [random.choice(['⬆️', '⬇️', '⬅️', '➡️']) for _ in range(3 + self.difficulty)],
                'description': 'Follow this path in order',
                'question': 'Repeat the directional sequence'
            }
        ]
        
        puzzle = random.choice(sequences)
        return puzzle
    
    def _generate_memory_puzzle(self) -> Dict[str, Any]:
        grid_size = min(4, 2 + self.difficulty)
        items = ['💎', '⚔️', '🛡️', '🗝️', '📜', '🪙', '🎁', '⭐']
        
        num_pairs = min(grid_size, 4)
        selected_items = random.sample(items, num_pairs)
        pairs = selected_items + selected_items
        random.shuffle(pairs)
        
        grid = []
        for i in range(0, len(pairs), grid_size):
            grid.append(pairs[i:i+grid_size])
        
        return {
            'name': 'Memory Match',
            'type': 'memory_match',
            'grid_size': grid_size,
            'items': pairs,
            'grid': grid,
            'description': 'Study the grid below for a few seconds!',
            'question': f'Memorize the positions! You need to match {num_pairs} pairs. (Simplified: just type "match" to solve for now)',
            'num_pairs': num_pairs
        }
    
    def _generate_riddle_puzzle(self) -> Dict[str, Any]:
        riddles = [
            {
                'name': 'Keys and Space',
                'riddle': 'I have keys but no locks, space but no room. You can enter but cannot leave. What am I?',
                'question': 'I have keys but no locks, space but no room. You can enter but cannot leave. What am I?',
                'description': 'Solve this riddle',
                'options': ['A chest', 'A keyboard', 'A prison', 'A map'],
                'correct_index': 1
            },
            {
                'name': 'The More You Take',
                'riddle': 'The more you take, the more you leave behind. What am I?',
                'question': 'The more you take, the more you leave behind. What am I?',
                'description': 'Solve this riddle',
                'options': ['Footsteps', 'Time', 'Memories', 'Coins'],
                'correct_index': 0
            },
            {
                'name': 'Thirteen Hearts',
                'riddle': 'What has 13 hearts but no organs?',
                'question': 'What has 13 hearts but no organs?',
                'description': 'Solve this riddle',
                'options': ['A zombie', 'A deck of cards', 'A tree', 'Love'],
                'correct_index': 1
            }
        ]
        
        puzzle = random.choice(riddles)
        return puzzle
    
    def _generate_math_puzzle(self) -> Dict[str, Any]:
        difficulty_range = 10 + (self.difficulty * 10)
        
        operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            a = random.randint(1, difficulty_range)
            b = random.randint(1, difficulty_range)
            answer = a + b
            question = f'{a} + {b} = ?'
        elif operation == '-':
            answer = random.randint(1, difficulty_range)
            b = random.randint(1, answer)
            a = answer + b
            question = f'{a} - {b} = ?'
        else:
            a = random.randint(2, min(12, 2 + self.difficulty))
            b = random.randint(2, min(12, 2 + self.difficulty))
            answer = a * b
            question = f'{a} × {b} = ?'
        
        wrong_answers = [answer + random.randint(1, 5), answer - random.randint(1, 5), answer + random.randint(10, 20)]
        options = [str(answer)] + [str(w) for w in wrong_answers]
        random.shuffle(options)
        
        return {
            'name': 'Math Challenge',
            'description': 'Solve the mathematical equation',
            'question': question,
            'options': options,
            'correct_index': options.index(str(answer))
        }
    
    def attempt_solve(self, answer: Any) -> Tuple[bool, str]:
        self.attempts += 1
        
        if self.puzzle_type in [PuzzleType.LOGIC, PuzzleType.PATTERN, PuzzleType.RIDDLE, PuzzleType.MATH]:
            correct_index = self.data.get('correct_index', 0)
            
            try:
                if isinstance(answer, str):
                    answer_index = int(answer)
                else:
                    answer_index = answer
            except (ValueError, TypeError):
                remaining = self.max_attempts - self.attempts
                if remaining > 0:
                    return False, f'Invalid input! Please enter a number 0-{len(self.data.get("options", [])) - 1}. {remaining} attempts remaining.'
                else:
                    return False, 'Puzzle failed! Invalid input.'
            
            if answer_index == correct_index:
                self.solved = True
                return True, 'Correct! Puzzle solved!'
            else:
                remaining = self.max_attempts - self.attempts
                if remaining > 0:
                    return False, f'Incorrect! {remaining} attempts remaining.'
                else:
                    return False, 'Puzzle failed! No attempts remaining.'
        
        elif self.puzzle_type == PuzzleType.SEQUENCE:
            expected_sequence = self.data.get('sequence', [])
            
            if isinstance(answer, str):
                answer_parts = answer.replace(',', ' ').split()
                
                if self.data.get('type') == 'number_sequence':
                    try:
                        answer_sequence = [int(x) for x in answer_parts]
                    except ValueError:
                        remaining = self.max_attempts - self.attempts
                        return False, f'Invalid input! Enter numbers separated by spaces. {remaining} attempts remaining.'
                else:
                    answer_sequence = answer_parts
            else:
                answer_sequence = answer
            
            if answer_sequence == expected_sequence:
                self.solved = True
                return True, 'Sequence matched perfectly!'
            else:
                remaining = self.max_attempts - self.attempts
                if remaining > 0:
                    return False, f'Wrong sequence! {remaining} attempts remaining.'
                else:
                    return False, 'Puzzle failed! Sequence was incorrect.'
        
        elif self.puzzle_type == PuzzleType.MEMORY:
            if isinstance(answer, str) and answer.lower() == 'match':
                self.solved = True
                return True, 'Memory puzzle solved! (Simplified completion)'
            
            remaining = self.max_attempts - self.attempts
            if remaining > 0:
                return False, f'Type "match" to solve this memory puzzle. {remaining} attempts remaining.'
            else:
                return False, 'Puzzle failed! No attempts remaining.'
        
        return False, 'Invalid puzzle type'
    
    def get_hint(self) -> Optional[str]:
        if self.attempts < 1:
            return None
        
        if self.puzzle_type == PuzzleType.LOGIC:
            return 'Think about what information you can trust and what you cannot...'
        elif self.puzzle_type == PuzzleType.PATTERN:
            sequence = self.data.get('sequence', [])
            return f'Look for repeating elements or mathematical progressions... The pattern has {len(sequence)} elements shown.'
        elif self.puzzle_type == PuzzleType.SEQUENCE:
            seq_type = self.data.get('type', '')
            sequence = self.data.get('sequence', [])
            if seq_type == 'color_simon':
                return f'The color sequence has {len(sequence)} colors. Type them in order using emojis: {" ".join(set(sequence))}'
            elif seq_type == 'number_sequence':
                return f'The number sequence has {len(sequence)} numbers. Type them separated by spaces (e.g., "1 2 3 4")'
            elif seq_type == 'direction_sequence':
                return f'The direction sequence has {len(sequence)} arrows. Type them in order using arrow emojis.'
            return f'The sequence has {len(sequence)} elements...'
        elif self.puzzle_type == PuzzleType.MEMORY:
            grid_size = self.data.get('grid_size', 2)
            items = self.data.get('items', [])
            unique_items = list(set(items))
            return f'Memory grid is {grid_size}x{grid_size}. Unique items: {" ".join(unique_items)}. Match pairs by position!'
        elif self.puzzle_type == PuzzleType.RIDDLE:
            return 'Think literally and metaphorically at the same time...'
        elif self.puzzle_type == PuzzleType.MATH:
            question = self.data.get('question', '')
            return f'Double-check your calculation for: {question}'
        
        return None
    
    def get_reward_multiplier(self) -> float:
        if not self.solved:
            return 0.0
        
        attempts_penalty = 1.0 - (0.2 * (self.attempts - 1))
        difficulty_bonus = 1.0 + (self.difficulty * 0.2)
        party_bonus = 1.0 + (self.party_size * 0.1)
        
        return max(0.5, attempts_penalty * difficulty_bonus * party_bonus)


class PuzzleSystem:
    
    @classmethod
    def create_puzzle(cls, difficulty: int, party_size: int = 1) -> Puzzle:
        puzzle_types = [
            PuzzleType.LOGIC,
            PuzzleType.PATTERN,
            PuzzleType.SEQUENCE,
            PuzzleType.RIDDLE,
            PuzzleType.MATH
        ]
        
        puzzle_type = random.choice(puzzle_types)
        return Puzzle(puzzle_type, difficulty, party_size)
    
    @classmethod
    def calculate_damage_on_failure(cls, difficulty: int, player_stats: Dict[str, Any]) -> int:
        base_damage = 30 + (difficulty * 20)
        defense = player_stats.get('defense', 0)
        
        damage_reduction = defense / (defense + 100)
        damage_reduction = min(0.75, damage_reduction)
        
        final_damage = int(base_damage * (1 - damage_reduction))
        
        return max(10, final_damage)
    
    @classmethod
    def calculate_puzzle_rewards(cls, puzzle: Puzzle, floor_difficulty: int) -> Dict[str, Any]:
        if not puzzle.solved:
            return {'coins': 0, 'xp': 0, 'bonus_loot_chance': 0}
        
        multiplier = puzzle.get_reward_multiplier()
        
        base_coins = 100 + (floor_difficulty * 50)
        base_xp = 20 + (floor_difficulty * 10)
        
        return {
            'coins': int(base_coins * multiplier),
            'xp': int(base_xp * multiplier),
            'bonus_loot_chance': min(0.5, 0.1 + (multiplier * 0.2))
        }
