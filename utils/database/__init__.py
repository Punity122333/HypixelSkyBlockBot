"""
Database module for HypixelSkyblockBot.

This module provides a comprehensive database interface split into logical components:
- base: Core database connection and table creation
- players: Player data and progression
- skills: Skills and collections
- inventory: Inventory and item management
- market: Auction house and bazaar
- game_data: Static game configuration data
- trading: Bot traders and stock market
- pets_minions: Pets and minions
- quests: Quests and daily rewards
"""

from .base import DatabaseBase
from .players import PlayerDatabase
from .skills import SkillsDatabase
from .inventory import InventoryDatabase
from .market import MarketDatabase
from .game_data import GameDataDatabase
from .trading import TradingDatabase
from .pets_minions import PetsMinionsDatabase
from .quests import QuestsDatabase


class GameDatabase(
    PlayerDatabase,
    SkillsDatabase,
    InventoryDatabase,
    MarketDatabase,
    GameDataDatabase,
    TradingDatabase,
    PetsMinionsDatabase,
    QuestsDatabase
):
    """
    Main database class that combines all database functionality through multiple inheritance.
    
    This class inherits from all specialized database classes, providing a single interface
    for all database operations while keeping the implementation modular and organized.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the game database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        # Only need to call the base __init__ once due to cooperative inheritance
        DatabaseBase.__init__(self, db_path)


__all__ = [
    'GameDatabase',
    'DatabaseBase',
    'PlayerDatabase',
    'SkillsDatabase',
    'InventoryDatabase',
    'MarketDatabase',
    'GameDataDatabase',
    'TradingDatabase',
    'PetsMinionsDatabase',
    'QuestsDatabase',
]
