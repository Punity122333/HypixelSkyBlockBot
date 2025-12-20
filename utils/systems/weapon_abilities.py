from typing import Dict, Any, Optional

class WeaponAbilities:
    
    @staticmethod
    async def has_ability(db, item_id: str) -> bool:
        return await db.weapon_abilities.has_ability(item_id)
    
    @staticmethod
    async def get_ability(db, item_id: str) -> Optional[Dict[str, Any]]:
        return await db.weapon_abilities.get_weapon_ability(item_id)
    
    @staticmethod
    async def calculate_ability_damage(
        db,
        item_id: str,
        player_stats: Dict[str, Any],
        weapon_damage: int
    ) -> float:
        ability = await db.weapon_abilities.get_weapon_ability(item_id)
        
        if not ability:
            return 0.0
        
        base_multiplier = ability.get('base_damage_multiplier', 1.0)
        intel_scaling = ability.get('intelligence_scaling', 0.0)
        str_scaling = ability.get('strength_scaling', 0.0)
        ability_dmg_scaling = ability.get('ability_damage_scaling', 0.0)
        
        intelligence = player_stats.get('intelligence', 0)
        strength = player_stats.get('strength', 0)
        ability_damage_stat = player_stats.get('ability_damage', 0)
        
        base_damage = weapon_damage * base_multiplier
        
        intel_bonus = intelligence * intel_scaling * base_damage
        str_bonus = strength * str_scaling * base_damage
        ability_bonus = ability_damage_stat * ability_dmg_scaling * base_damage
        
        total_damage = base_damage + intel_bonus + str_bonus + ability_bonus
        
        coins_scaling = ability.get('coins_scaling', 0.0)
        max_bonus = ability.get('max_bonus_damage', 0)
        if coins_scaling > 0 and max_bonus > 0:
            player = await db.get_player(player_stats.get('user_id', 0))
            if player:
                coins = player.get('coins', 0)
                coin_bonus = min(coins * coins_scaling, max_bonus)
                total_damage += coin_bonus
        
        hits = ability.get('hits', 1)
        arrows = ability.get('arrows', 1)
        multiplier = max(hits, arrows)
        
        return total_damage * multiplier
    
    @staticmethod
    async def apply_ability_effects(
        db,
        item_id: str,
        user_id: int,
        damage_dealt: float,
        target_health: int
    ) -> Dict[str, Any]:
        ability = await db.weapon_abilities.get_weapon_ability(item_id)
        
        if not ability:
            return {}
        
        effects = {}
        
        lifesteal = ability.get('lifesteal_percent', 0)
        if lifesteal > 0:
            heal_amount = int(damage_dealt * lifesteal / 100)
            effects['heal'] = heal_amount
        
        defense_boost = ability.get('defense_boost', 0)
        duration = ability.get('duration', 0)
        if defense_boost > 0 and duration > 0:
            effects['defense_buff'] = {
                'amount': defense_boost,
                'duration': duration
            }
        
        aoe_radius = ability.get('aoe_radius', 0)
        if aoe_radius > 0:
            effects['aoe'] = True
            effects['aoe_radius'] = aoe_radius
        
        wither_effect = ability.get('wither_effect', 0)
        if wither_effect:
            effects['wither'] = True
        
        teleport_distance = ability.get('teleport_distance', 0)
        if teleport_distance > 0:
            effects['teleport'] = teleport_distance
        
        piercing = ability.get('piercing', 0)
        if piercing:
            effects['piercing'] = True
        
        return effects
