from typing import Dict, Any, List, Optional
import math


class GradientScaling:
    
    @staticmethod
    def exponential_scale(base_value: float, level: int, growth_rate: float = 1.15) -> float:
        return base_value * (growth_rate ** level)
    
    @staticmethod
    def logarithmic_scale(base_value: float, level: int, scale_factor: float = 2.0) -> float:
        return base_value * (1 + scale_factor * math.log(1 + level))
    
    @staticmethod
    def sigmoid_scale(base_value: float, level: int, midpoint: float = 10.0, steepness: float = 0.5) -> float:
        sigmoid = 1 / (1 + math.exp(-steepness * (level - midpoint)))
        return base_value + (base_value * 2 * sigmoid)
    
    @staticmethod
    def polynomial_scale(base_value: float, level: int, degree: float = 1.5) -> float:
        return base_value * (level ** degree)
    
    @staticmethod
    def diminishing_returns_scale(base_value: float, level: int, soft_cap: float = 20.0) -> float:
        if level <= soft_cap:
            return base_value * level
        else:
            soft_cap_value = base_value * soft_cap
            excess = level - soft_cap
            diminished = soft_cap_value + (base_value * math.sqrt(excess))
            return diminished

    @staticmethod
    def linear_scale(base_value: float, level: int, increment: float = 1.0) -> float:
        return base_value + (level * increment)
    
    


class DungeonScaling:
    
    FLOOR_DIFFICULTY = {
        'entrance': 1,
        'floor1': 2,
        'floor2': 3,
        'floor3': 5,
        'floor4': 7,
        'floor5': 10,
        'floor6': 15,
        'floor7': 20,
        'm1': 25,
        'm2': 30,
        'm3': 40,
        'm4': 50,
        'm5': 65,
        'm6': 80,
        'm7': 100
    }
    
    @classmethod
    def get_floor_difficulty(cls, floor_id: str) -> int:
        return cls.FLOOR_DIFFICULTY.get(floor_id, 1)
    
    @classmethod
    def scale_mob_health(cls, floor_id: str, party_size: int, player_stats: Dict[str, Any]) -> int:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        base_health = GradientScaling.exponential_scale(100, difficulty, 1.35)
        
        party_multiplier = 1 + (party_size - 1) * 0.5
        
        avg_player_strength = player_stats.get('strength', 0)
        player_scaling = 1 + (avg_player_strength / 500)
        
        final_health = int(base_health * party_multiplier * player_scaling)
        
        return max(50, final_health)
    
    @classmethod
    def scale_mob_damage(cls, floor_id: str, party_size: int) -> int:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        base_damage = GradientScaling.exponential_scale(15, difficulty, 1.25)
        
        party_multiplier = 1 + (party_size - 1) * 0.3
        
        final_damage = int(base_damage * party_multiplier)
        
        return max(10, final_damage)
    
    @classmethod
    def scale_coin_rewards(cls, floor_id: str, score: int, secrets_found: int, party_size: int) -> int:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        base_coins = GradientScaling.logarithmic_scale(500, difficulty, 3.0)
        
        score_multiplier = 1 + (score / 500)
        score_multiplier = GradientScaling.sigmoid_scale(score_multiplier, score, 200, 0.01)
        
        secrets_bonus = GradientScaling.diminishing_returns_scale(50, secrets_found, 15)
        
        party_multiplier = 0.8 + (party_size * 0.15)
        
        final_coins = int((base_coins * score_multiplier + secrets_bonus) * party_multiplier)
        
        return max(100, final_coins)
    
    @classmethod
    def scale_xp_rewards(cls, floor_id: str, score: int, party_size: int) -> int:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        base_xp = GradientScaling.polynomial_scale(50, difficulty, 1.4)
        
        score_multiplier = 1 + (score / 1000)
        
        party_bonus = 1 + (party_size * 0.1)
        
        final_xp = int(base_xp * score_multiplier * party_bonus)
        
        return max(20, final_xp)
    
    @classmethod
    def scale_loot_rarity(cls, floor_id: str, score: int, magic_find: float, secrets_found: int) -> float:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        base_chance = 0.05 + (difficulty * 0.02)
        
        score_bonus = GradientScaling.logarithmic_scale(0, score, 0.1)
        
        magic_find_bonus = magic_find / 100
        magic_find_bonus = GradientScaling.diminishing_returns_scale(magic_find_bonus, int(magic_find), 200)
        
        secrets_bonus = GradientScaling.diminishing_returns_scale(0.01, secrets_found, 20)
        
        final_chance = base_chance + score_bonus + magic_find_bonus + secrets_bonus
        
        return min(0.95, final_chance)
    
    @classmethod
    def calculate_puzzle_difficulty(cls, floor_id: str, room_number: int, total_rooms: int) -> int:
        base_difficulty = cls.get_floor_difficulty(floor_id) // 5
        
        progress_factor = room_number / total_rooms
        progress_difficulty = int(progress_factor * 3)
        
        return max(1, base_difficulty + progress_difficulty)
    
    @classmethod
    def calculate_damage_scaling(cls, floor_id: str, player_stats: Dict[str, Any], party_stats: Optional[List[Dict[str, Any]]] = None) -> float:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        avg_stats = player_stats
        if party_stats:
            total_strength = sum(s.get('strength', 0) for s in party_stats)
            avg_stats = {'strength': total_strength / len(party_stats)}
        
        strength = avg_stats.get('strength', 0)
        
        base_multiplier = 1.0
        difficulty_scaling = GradientScaling.logarithmic_scale(0, difficulty, 0.2)
        strength_scaling = GradientScaling.logarithmic_scale(0, int(strength), 0.05)
        
        total_multiplier = base_multiplier + difficulty_scaling + strength_scaling
        
        return max(0.5, total_multiplier)
    
    @classmethod
    def calculate_reward_distribution(cls, total_reward: int, party_members: List[Dict[str, Any]]) -> Dict[int, int]:
        party_size = len(party_members)
        
        if party_size == 1:
            return {party_members[0]['user_id']: total_reward}
        
        base_share = total_reward // party_size
        remainder = total_reward % party_size
        
        distribution = {}
        for i, member in enumerate(party_members):
            share = base_share
            if i < remainder:
                share += 1
            distribution[member['user_id']] = share
        
        return distribution
    
    @classmethod
    def calculate_floor_requirements(cls, floor_id: str) -> Dict[str, int]:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        required_level = max(0, difficulty * 2 - 2)
        required_gear_score = max(0, int(GradientScaling.exponential_scale(50, difficulty, 1.3)))
        required_catacombs = max(0, difficulty // 3)
        
        return {
            'level': required_level,
            'gear_score': required_gear_score,
            'catacombs_level': required_catacombs
        }
    
    @classmethod
    def calculate_dungeon_score(
        cls,
        floor_id: str,
        rooms_cleared: int,
        total_rooms: int,
        secrets_found: int,
        max_secrets: int,
        deaths: int,
        damage_taken: int,
        puzzles_failed: int,
        time_bonus: int = 0,
        party_size: int = 1
    ) -> int:
        difficulty = cls.get_floor_difficulty(floor_id)
        
        base_score = 100
        
        room_completion = (rooms_cleared / total_rooms) if total_rooms > 0 else 0
        room_score = int(GradientScaling.logarithmic_scale(100, int(room_completion * 100), 1.5))
        
        secret_completion = (secrets_found / max_secrets) if max_secrets > 0 else 0
        secret_score = int(GradientScaling.sigmoid_scale(100, int(secret_completion * 100), 50, 0.1))
        
        survival_score = max(0, int(GradientScaling.diminishing_returns_scale(100, deaths, 3)))
        damage_penalty = int(GradientScaling.logarithmic_scale(0, damage_taken // 10, 0.5))
        
        puzzle_score = max(0, 50 - (puzzles_failed * 10))
        
        party_bonus = int(party_size * 5) if party_size > 1 else 0
        
        total_score = (
            base_score +
            room_score +
            secret_score +
            survival_score -
            damage_penalty +
            puzzle_score +
            time_bonus +
            party_bonus
        )
        
        if secret_completion >= 1.0:
            total_score += 100
        elif secret_completion >= 0.8:
            total_score += 50
        
        difficulty_multiplier = 1 + (difficulty * 0.1)
        total_score = int(total_score * difficulty_multiplier)
        
        return max(0, total_score)
