from typing import Dict, Any, Optional
import random

class WeaponAbilities:
    
    ABILITIES = {
        'hyperion': {
            'name': 'Wither Impact',
            'mana_cost': 150,
            'cooldown': 2,
            'base_damage_multiplier': 50.0,
            'intelligence_scaling': 0.08,
            'strength_scaling': 0.012,
            'ability_damage_scaling': 0.04,
            'aoe_radius': 10,
            'wither_effect': True,
            'description': 'Deal massive AOE damage based on your intelligence. True destruction.'
        },
        'valkyrie': {
            'name': 'Wither Impact',
            'mana_cost': 150,
            'cooldown': 2,
            'base_damage_multiplier': 40.0,
            'intelligence_scaling': 0.065,
            'strength_scaling': 0.01,
            'ability_damage_scaling': 0.035,
            'aoe_radius': 10,
            'description': 'Deal massive AOE damage based on your intelligence'
        },
        'astraea': {
            'name': 'Wither Impact',
            'mana_cost': 150,
            'cooldown': 2,
            'base_damage_multiplier': 35.0,
            'intelligence_scaling': 0.055,
            'strength_scaling': 0.008,
            'ability_damage_scaling': 0.03,
            'aoe_radius': 10,
            'description': 'Deal massive AOE damage based on your intelligence'
        },
        'scylla': {
            'name': 'Wither Impact',
            'mana_cost': 150,
            'cooldown': 2,
            'base_damage_multiplier': 30.0,
            'intelligence_scaling': 0.045,
            'strength_scaling': 0.007,
            'ability_damage_scaling': 0.025,
            'aoe_radius': 10,
            'description': 'Deal massive AOE damage based on your intelligence'
        },
        'aspect_of_the_dragons': {
            'name': 'Dragon Rage',
            'mana_cost': 100,
            'cooldown': 1,
            'base_damage_multiplier': 6.0,
            'strength_scaling': 0.012,
            'ability_damage_scaling': 0.015,
            'description': 'Shoot a fireball that deals extra damage'
        },
        'shadow_fury': {
            'name': 'Shadow Fury',
            'mana_cost': 150,
            'cooldown': 1,
            'base_damage_multiplier': 12.0,
            'strength_scaling': 0.01,
            'hits': 5,
            'description': 'Strike the enemy 5 times rapidly'
        },
        'livid_dagger': {
            'name': 'Throw',
            'mana_cost': 50,
            'cooldown': 0.5,
            'base_damage_multiplier': 5.5,
            'strength_scaling': 0.008,
            'description': 'Throw your dagger at an enemy'
        },
        'giants_sword': {
            'name': 'Giants Slam',
            'mana_cost': 100,
            'cooldown': 3,
            'base_damage_multiplier': 18.0,
            'strength_scaling': 0.03,
            'aoe_radius': 5,
            'description': 'Slam the ground dealing massive damage to nearby enemies'
        },
        'terminator': {
            'name': 'Termination',
            'mana_cost': 60,
            'cooldown': 0,
            'base_damage_multiplier': 8.0,
            'arrows': 5,
            'strength_scaling': 0.01,
            'description': 'Shoot 5 arrows at once'
        },
        'juju_shortbow': {
            'name': 'Triple Shot',
            'mana_cost': 40,
            'cooldown': 0,
            'base_damage_multiplier': 4.5,
            'arrows': 3,
            'strength_scaling': 0.008,
            'description': 'Shoot 3 arrows at once'
        },
        'aspect_of_the_end': {
            'name': 'Instant Transmission',
            'mana_cost': 50,
            'cooldown': 0,
            'teleport_distance': 8,
            'description': 'Teleport 8 blocks ahead'
        },
        'flower_of_truth': {
            'name': 'Heat-Seeking Rose',
            'mana_cost': 100,
            'cooldown': 1,
            'base_damage_multiplier': 7.0,
            'strength_scaling': 0.01,
            'piercing': True,
            'description': 'Throw a tracking rose that pierces enemies'
        },
        'midas_sword': {
            'name': 'Greed',
            'coins_scaling': 0.00001,
            'max_bonus_damage': 2000,
            'description': 'Deal bonus damage based on coins in purse'
        },
        'reaper_scythe': {
            'name': 'Reap',
            'mana_cost': 120,
            'cooldown': 2,
            'base_damage_multiplier': 10.0,
            'strength_scaling': 0.015,
            'intelligence_scaling': 0.02,
            'aoe_radius': 8,
            'lifesteal_percent': 50,
            'description': 'Deal AOE damage and heal based on damage dealt'
        },
        'yeti_sword': {
            'name': 'Ice Shield',
            'mana_cost': 80,
            'cooldown': 5,
            'defense_boost': 300,
            'duration': 5,
            'strength_scaling': 0.01,
            'description': 'Gain massive defense for 5 seconds'
        },
        'necron_blade': {
            'name': 'Necron\'s Wrath',
            'mana_cost': 200,
            'cooldown': 3,
            'base_damage_multiplier': 22.0,
            'intelligence_scaling': 0.035,
            'strength_scaling': 0.015,
            'ability_damage_scaling': 0.02,
            'aoe_radius': 15,
            'description': 'Unleash devastating wither power'
        },
        'atomsplit_katana': {
            'name': 'Atomic Split',
            'mana_cost': 180,
            'cooldown': 2,
            'base_damage_multiplier': 20.0,
            'strength_scaling': 0.02,
            'aoe_radius': 7,
            'description': 'Split atoms and deal massive damage'
        },
        'dark_claymore': {
            'name': 'Dark Slash',
            'mana_cost': 150,
            'cooldown': 2.5,
            'base_damage_multiplier': 24.0,
            'strength_scaling': 0.025,
            'lifesteal_percent': 30,
            'description': 'Deal massive damage and heal based on damage dealt'
        }
    }
    
    @classmethod
    def get_ability(cls, weapon_id: str) -> Optional[Dict[str, Any]]:
        return cls.ABILITIES.get(weapon_id)
    
    @classmethod
    async def calculate_ability_damage(cls, weapon_id: str, stats: Dict[str, Any], weapon_damage: int) -> float:
        ability = cls.get_ability(weapon_id)
        if not ability:
            return 0
        
        base_damage = 5 + weapon_damage
        strength_bonus = stats.get('strength', 0)
        intelligence = stats.get('intelligence', 0)
        ability_damage_bonus = stats.get('ability_damage', 0)
        
        base_weapon_damage = (base_damage + strength_bonus / 5) * (1 + strength_bonus / 100)
        
        multiplier = ability.get('base_damage_multiplier', 3.0)
        
        if 'intelligence_scaling' in ability:
            int_scaling = ability['intelligence_scaling']
            multiplier *= (1 + intelligence * int_scaling)
        
        if 'strength_scaling' in ability:
            str_scaling = ability['strength_scaling']
            multiplier *= (1 + strength_bonus * str_scaling)
        
        if 'ability_damage_scaling' in ability:
            ab_scaling = ability['ability_damage_scaling']
            multiplier *= (1 + ability_damage_bonus * ab_scaling)
        
        total_damage = base_weapon_damage * multiplier * (1 + ability_damage_bonus / 100)
        
        if ability.get('hits', 1) > 1:
            total_damage *= ability['hits']
        
        if ability.get('arrows', 1) > 1:
            total_damage *= ability['arrows']
        
        return total_damage
    
    @classmethod
    def get_mana_cost(cls, weapon_id: str) -> int:
        ability = cls.get_ability(weapon_id)
        if not ability:
            return 50
        return ability.get('mana_cost', 50)
    
    @classmethod
    def has_ability(cls, weapon_id: str) -> bool:
        return weapon_id in cls.ABILITIES
