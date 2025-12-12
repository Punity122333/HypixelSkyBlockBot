# Hypixel SkyBlock Bot

A comprehensive Discord bot that brings the complete Hypixel SkyBlock experience to Discord! Featuring advanced game mechanics, persistent database storage, real-time economy simulation, and 75+ interactive commands across all major game systems.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Game Systems](#game-systems)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Commands](#commands)
- [Database](#database)
- [Wiki System](#wiki-system)
- [Development](#development)
- [Contributing](#contributing)

---

## Overview

This Discord bot recreates the authentic Hypixel SkyBlock experience with:

- **75+ Interactive Commands** - Complete coverage of all game systems
- **Persistent SQLite Database** - All progress saved automatically
- **Real-Time Economy** - Bazaar, Auction House, Stock Market with bot traders
- **Advanced Combat** - Multiple locations, bosses, dungeons, and slayer quests
- **11 Skills** - Complete progression system with rewards
- **Automation** - 40+ minion types working 24/7
- **Pet Collection** - 30+ pets with unique abilities and leveling
- **Social Features** - Co-ops, parties, trading, and leaderboards
- **Event System** - Dynamic events with special bonuses
- **Comprehensive Wiki** - In-game help system with detailed guides

---

## Features

### Economy & Trading

- **Bank System** - Secure storage with interest earnings
- **Bazaar** - Instant trading with buy/sell orders
- **Auction House** - Bid on items or use BIN (Buy It Now)
- **Stock Market** - Trade 8 stocks with real-time price fluctuations
- **Player Trading** - Secure direct trades with confirmation system
- **Merchants** - Rotating special deals from traveling merchants
- **Market Analytics** - Price tracking, graphs, and flip statistics

### Combat & Dungeons

- **6+ Combat Locations** - Hub, Spider's Den, Crimson Isle, The End, Nether, Deep Caverns
- **Interactive Combat** - Real-time health bars and strategic abilities
- **Boss Fights** - Unique mechanics and valuable rewards
- **Dungeon System** - 7 floors + Master Mode with puzzles and secrets
- **Slayer Quests** - 4 slayer types (Zombie, Spider, Wolf, Enderman), 5 tiers each
- **Party System** - Coordinate with friends for dungeons
- **Party Finder** - Browse and join open parties
- **Bestiary** - Track mob kills and unlock rewards

### Skills & Progression

- **11 Skills** - Mining, Farming, Combat, Fishing, Foraging, Enchanting, Alchemy, Taming, Carpentry, Runecrafting, Dungeoneering
- **50-60 Levels** per skill with permanent stat bonuses
- **Collection System** - Track gathered resources, unlock recipes
- **Achievements** - 50+ badges for accomplishments
- **Heart of the Mountain** - Advanced mining skill tree with perks
- **242 Fairy Souls** - Collectible power-ups with permanent bonuses
- **Progression Tracking** - Detailed stats and milestone tracking

### Inventory & Items

- **Complete Inventory System** - Organize and manage items
- **Equipment Slots** - Weapons, armor, tools, accessories
- **Crafting** - 100+ recipes with material requirements
- **Enchanting** - Powerful enchantments up to level X
- **Reforging** - Modify item stats and bonuses
- **Ender Chest** - Extended storage space
- **Wardrobe** - Quick armor set switching
- **Talisman Pouch** - Collect talismans for stat bonuses

### Automation & Pets

- **40+ Minion Types** - Automated resource gathering
- **25 Minion Slots** - Unlock through collection
- **Minion Upgrades** - Fuel, storage, auto-selling, compactors
- **30+ Pet Types** - Each with unique abilities
- **Pet Leveling** - Level pets to 100 with XP
- **6 Rarity Tiers** - Common to Mythic with scaling bonuses
- **Pet Items** - Candies, skins, and stat boosters

### Social Features

- **Co-op System** - Permanent alliances with shared resources
- **Permissions** - Configurable roles (Owner, Admin, Member)
- **Shared Island** - Collaborate on building and minions
- **Party System** - Temporary groups for dungeons
- **Trading** - Safe player-to-player exchanges
- **Leaderboards** - Compete in multiple categories

### Events & Specials

- **Dynamic Events** - Rotating bonuses and challenges
- **Event Effects** - XP multipliers, fortune, coin boosts
- **Daily Quests** - Repeatable objectives with rewards
- **Special Merchants** - Limited-time offers
- **Seasonal Events** - Holiday celebrations with unique rewards

---

## Game Systems

### Combat System

```text
Locations: Hub → Spider's Den → Crimson Isle → The End → Nether → Deep Caverns
Difficulty: Easy → Medium → Hard → Very Hard → Extreme → ????
Features: Interactive combat, boss fights, slayer quests, dungeon runs
Rewards: Coins, items, XP, rare drops, collection progress
```

### Skill Progression

```text
11 Skills: Each levels 1-50 (some to 60)
XP Requirements: Exponential scaling
Benefits: Stat bonuses, area unlocks, recipe access, perks
Tracking: /skills command shows all progress
```

### Economy Flow

```text
Earning: Gathering → Selling → Quests → Trading → Investments
Spending: Tools → Gear → Upgrades → Minions → Luxury Items
Advanced: Flipping → Stock Trading → Auction Sniping
```

### Minion System

```text
Placement: Up to 25 slots on your island
Production: 24/7 automated resource generation
Upgrades: Speed boosters, storage, auto-sell
Profit: Passive income while offline
```

---

## Architecture

### Modular Design

```text
main.py                 # Bot entry point and setup
├── cogs/              # Command modules (39 cogs)
│   ├── commands/      # Game commands
│   └── events/        # Event handlers
├── database/          # Data persistence layer
│   ├── core.py        # Database connection
│   ├── players.py     # Player data
│   ├── inventory.py   # Items and storage
│   ├── market.py      # Economy systems
│   └── ...            # More specialized modules
├── utils/             # Helper utilities
│   ├── systems/       # Game logic systems
│   ├── stat_calculator.py
│   ├── player_manager.py
│   └── ...
└── components/        # UI components
    ├── views/         # Interactive menus
    ├── buttons/       # Button handlers
    └── modals/        # Input forms
```

### Technology Stack

- **Python 3.12+** - Core language
- **discord.py 2.0+** - Discord API wrapper
- **aiosqlite** - Async SQLite database
- **matplotlib** - Market graphs and charts
- **dotenv** - Environment configuration

---

## Project Structure

```text
HypixelSkyblockBot/
├── main.py                    # Bot entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── skyblock.db               # SQLite database (auto-created)
│
├── cogs/                     # Discord cogs
│   ├── commands/             # 39 command modules
│   │   ├── admin.py         # Admin commands
│   │   ├── combat.py        # Combat system
│   │   ├── gathering.py     # Mining, farming, etc.
│   │   ├── bazaar.py        # Bazaar trading
│   │   ├── auction.py       # Auction house
│   │   ├── dungeons.py      # Dungeon system
│   │   └── ...              # 32 more modules
│   └── events/              # Event handlers
│
├── database/                # Database layer
│   ├── __init__.py         # Database initialization
│   ├── core.py             # Core DB functions
│   ├── players.py          # Player management
│   ├── inventory.py        # Inventory system
│   ├── market.py           # Market systems
│   ├── skills.py           # Skill tracking
│   ├── hotm.py             # Heart of the Mountain
│   ├── bestiary.py         # Mob tracking
│   ├── coop.py             # Co-op system
│   └── ...                 # 15+ more modules
│
├── utils/                  # Utilities
│   ├── systems/           # Game logic systems
│   │   ├── combat_system.py
│   │   ├── gathering_system.py
│   │   ├── economy_system.py
│   │   ├── dungeon_system.py
│   │   ├── market_system.py
│   │   └── ...
│   ├── stat_calculator.py  # Dynamic stats
│   ├── player_manager.py   # Player handling
│   ├── game_data.py        # Game data access
│   ├── autocomplete.py     # Command autocomplete
│   └── ...
│
├── components/            # UI Components
│   ├── views/            # Interactive menus
│   ├── buttons/          # Button handlers
│   └── modals/           # Input modals
│
├── migrations/           # Database migrations
│   ├── scripts/         # SQL migration files
│   └── migration_runner.py
│
├── wiki/                # In-game wiki pages
│   ├── getting_started.txt
│   ├── combat.txt
│   ├── skills.txt
│   └── ...              # 20+ guide pages
│
└── backups/             # Automatic DB backups
```

---

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Discord Bot Token
- Discord Application ID

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd HypixelSkyblockBot
```

1. **Create virtual environment**

```bash
python -m venv skyenv
source skyenv/bin/activate  # On Windows: skyenv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Configure environment**

Create a `.env` file in the root directory:

```env
TOKEN=your_discord_bot_token_here
APPID=your_application_id_here
DEV_GUILD_ID=your_test_guild_id_here (optional)
```

1. **Run the bot**

```bash
python main.py
```

The bot will:

- Initialize the database automatically
- Load all command modules
- Sync commands to Discord
- Start the market simulation
- Begin accepting commands!

---

## Configuration

### Environment Variables

- `TOKEN` - Your Discord bot token (required)
- `APPID` - Your Discord application ID (required)
- `DEV_GUILD_ID` - Test guild ID for development (optional)

### Bot Permissions

Required Discord permissions:

- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Use External Emojis
- Add Reactions
- Use Slash Commands

### Intents

The bot requires these intents:

- Guild Messages
- Guild Members
- Message Content

---

## Commands

### Beginner

- `/begin` - Start your SkyBlock journey
- `/claim_starter_pack` - Get initial items and coins
- `/profile` - View your profile and stats
- `/help` - Interactive help menu
- `/wiki <topic>` - Search the wiki

### Skills & Gathering

- `/mine` - Mine ores and resources
- `/farm` - Farm crops
- `/fish` - Go fishing
- `/forage` - Chop trees
- `/skills` - View all skill levels
- `/taming` - Level up taming skill
- `/carpentry` - Improve carpentry skill
- `/runecrafting` - Level runecrafting

### Combat

- `/fight <location>` - Fight monsters
- `/boss <boss>` - Challenge a boss
- `/combat_locations` - View all combat areas
- `/slayer` - Start slayer quests
- `/bestiary` - View mob kill tracker

### Dungeons

- `/dungeon <floor>` - Enter a dungeon
- `/party` - Manage your party
- `/party_finder` - Find dungeon groups

### Economy

- `/bank` - Access your bank
- `/bazaar` - Open the bazaar
- `/auction` - Browse auctions
- `/stocks` - Trade stocks
- `/trade <user>` - Trade with a player
- `/merchants` - View merchant deals

### Items & Inventory

- `/inventory` - View your inventory
- `/craft <item>` - Craft items
- `/enchant <item> <enchantment> <level>` - Enchant gear
- `/collections` - View collections
- `/talisman_pouch` - Manage talismans

### Minions & Pets

- `/minions` - Manage minions
- `/pets` - View pet collection
- `/island` - Visit your island

### Progression

- `/progression` - View progression path
- `/hotm` - Heart of the Mountain
- `/fairy_souls` - Check fairy soul progress
- `/search_fairy_soul` - Search for a soul
- `/badges` - View your badges
- `/quests` - View available quests

### Social

- `/coop` - Manage your co-op
- `/leaderboard` - View rankings
- `/market_graphs` - View market analytics

### Admin (Owner Only)

- `/reload_cog <cog>` - Reload a command module
- `/sync_commands` - Sync commands to Discord

---

## Database

### Schema Overview

The bot uses SQLite with 25+ tables:

### Player Data

- `players` - Core player information
- `skills` - Skill levels and XP
- `player_stats` - Combat and gathering stats
- `player_progression` - Milestones and achievements

### Inventories and Items

- `inventory` - Player items
- `equipped_items` - Currently equipped gear
- `ender_chest` - Extra storage
- `collections` - Resource collections

### Economy Related

- `bazaar_products` - Bazaar item listings
- `bazaar_orders` - Active buy/sell orders
- `auctions` - Auction house listings
- `stocks` - Stock market data
- `player_stocks` - Player portfolios

### Combat & Progression

- `bestiary` - Mob kill tracking
- `slayer_progress` - Slayer quest data
- `dungeon_runs` - Dungeon completion history
- `hotm_data` - Heart of the Mountain progress

### Social System

- `coops` - Co-op alliances
- `coop_members` - Co-op membership
- `party_finder_listings` - Open parties

### Automation System

- `minions` - Placed minions
- `pets` - Player pets
- `pet_data` - Pet stats and levels

### Backup System

- Automatic backups before migrations
- Manual backups in `/backups` folder
- Backup naming: `skyblock_backup_YYYYMMDD_HHMMSS.zip`

---

## Wiki System

The bot includes a comprehensive in-game wiki:

### Available Topics

- Getting Started - First steps guide
- Skills - All 11 skills explained
- Mining, Farming, Fishing, Foraging - Gathering guides
- Combat - Combat mechanics and strategies
- Dungeons - Complete dungeon guide
- Slayer - Slayer quest system
- Bazaar - Trading strategies
- Auction - Auction house tips
- Stocks - Investment guide
- Pets - Pet collection guide
- Minions - Automation guide
- HOTM - Heart of the Mountain
- Enchanting - Enchantment system
- And many more!

### Usage

```text
/wiki <topic>     # View a specific guide
/help             # Interactive help menu
/commands         # Complete command list
```

---

## Development

### Adding New Commands

1. Create a new file in `cogs/commands/`
2. Inherit from `commands.Cog`
3. Add `@app_commands.command` decorator
4. Implement `async def setup(bot)` function

### Adding New Features

1. Create system in `utils/systems/`
2. Add database methods in `database/`
3. Create UI components in `components/`
4. Update wiki documentation

### Database Migrations

1. Create SQL file in `migrations/scripts/`
2. Name format: `YYYYMMDD_description.sql`
3. Run automatically on bot startup

### Testing

```bash
# Set DEV_GUILD_ID in .env for instant command sync
# Test in your development server before production
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update wiki documentation
5. Test thoroughly
6. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and modular
- Comment complex logic

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Inspired by Hypixel SkyBlock
- Built with discord.py
- Community feedback and contributions

---

## Support

- Open an issue for bugs or feature requests
- Check the wiki for gameplay help
- Use `/help` in Discord for command information

---
