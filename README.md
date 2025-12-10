# Hypixel Skyblock Bot

A comprehensive Discord bot for managing and simulating Hypixel Skyblock gameplay, featuring database-backed game logic, modular command system, event listeners, and stat tracking. Built with Python and Discord.py, it supports advanced features like auctions, bazaar, dungeons, skills, pets, and more.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Commands Overview](#commands-overview)
- [Usage](#usage)
- [Extending the Bot](#extending-the-bot)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Discord Bot Commands**: Modular command system for game actions, including admin, auction, bank, bazaar, collections, combat, crafting, dungeons, economy stats, enchanting, events, gathering, inventory, island, leaderboard, marketplace, merchants, minions, misc, pets, profile, progression, quests, skills, slayer, stocks, tool progression.
- **Event Listeners**: Handles game and Discord events for dynamic gameplay, including custom game events and Discord triggers.
- **Database Integration**: Uses SQLite (`skyblock.db`) for persistent player, inventory, market, skills, and world data. All game actions are tracked and stored for consistency and recovery.
- **Migration System**: SQL and Python-based migrations for evolving the database schema. Includes backup and restore tools for safe upgrades.
- **Utilities**: Stat calculators, achievement tracking, event effects, compatibility layer, and more for advanced game logic and analytics.
- **Backup & Restore**: Database backup scripts and migration tools to prevent data loss.
- **Extensible**: Easily add new commands, events, game systems, or database models.
- **Stock Market & Bazaar**: Simulated trading systems for in-game economy.
- **Minion & Pet Management**: Track, upgrade, and manage minions and pets with custom logic.
- **Quests & Achievements**: Progression tracking, quest rewards, and achievement unlocks.

---

## Architecture

The bot is organized into modular components:

- **Commands**: Each game action is a separate module under `cogs/commands/`, making it easy to add or modify commands.
- **Events**: Game and Discord events are handled in `cogs/events/`, allowing for dynamic responses and gameplay.
- **Database Layer**: All persistent data is managed in `database/`, with separate modules for players, inventory, market, skills, and world logic. Uses async SQLite for performance.
- **Migration System**: Database schema changes are managed via SQL scripts and Python migration runners in `migrations/`.
- **Utilities**: Helper modules in `utils/` provide stat calculations, player management, game data access, and more.
- **Virtual Environment**: The `skyenv/` folder contains a Python virtual environment for dependency isolation.

---

## Project Structure

```text
main.py                  # Bot entry point
requirements.txt         # Python dependencies
skyblock.db              # SQLite database
cogs/                    # Command and event modules
  commands/              # Individual command modules
  events/                # Event listeners
  __init__.py            # Cog loader

database/                # Database logic
  core.py                # Core DB functions
  events.py              # Event DB logic
  game_data.py           # Game data DB logic
  inventory.py           # Inventory DB logic
  market.py              # Market DB logic
  players.py             # Player DB logic
  skills.py              # Skills DB logic
  world.py               # World DB logic

utils/                   # Utility modules
  stat_calculator.py     # Stat calculation logic
  player_manager.py      # Player management
  game_data.py           # Game data access
  event_effects.py       # Event effect logic
  ...                    # More utilities

migrations/              # Migration system
  migration_runner.py    # Migration runner
  migration_system.py    # Migration logic
  scripts/               # SQL migration scripts
  backups/               # Database backups

deprecated/              # Old migration scripts
skyenv/                  # Python virtual environment
```

---

## Getting Started

1. **Clone the repository**:

   ```sh
   git clone <repo-url>
   cd HypixelSkyblockBot
   ```

2. **Set up the Python environment**:

   - (Recommended) Use the provided virtual environment in `skyenv/` or create your own:

     ```sh
     python3 -m venv skyenv
     source skyenv/bin/activate
     ```

3. **Install dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure Discord bot token**:

   - Add your bot token in `main.py` or via environment variable. See comments in `main.py` for details.

5. **Initialize or migrate the database**:

   - Use migration scripts in `migrations/scripts/` or run Python migration tools in `migrations/` or `deprecated/` as needed.

6. **Run the bot**:

   ```sh
   python main.py
   ```

---

## Commands Overview

Below is a comprehensive list of all available commands and their functions:

### Admin

- `/reload_cog <cog>`: Reload a specific cog module.
- `/sync_commands [force]`: Force sync commands to Discord.
- `/clear_sync_cache [guild_id]`: Clear command sync cache for a guild.

### Auction House

- `/ah_create <item_id> <starting_bid> <duration_hours> [amount] [bin_price]`: Create an auction for an item.
- `/ah_browse`: Browse active auctions.
- `/ah_bid <auction_id> <bid_amount>`: Place a bid on an auction.
- `/ah_bin <auction_id>`: Buy an auction instantly (Buy It Now).
- `/ah_my`: View your auctions.

### Bank

- `/bank`: View your bank balance.
- `/deposit <amount>`: Deposit coins to your bank.
- `/withdraw <amount>`: Withdraw coins from your bank.
- `/pay <user> <amount>`: Pay coins to another player.

### Bazaar

- `/bz_prices <item_id>`: View bazaar prices for an item.
- `/bz_buy <item_id> <amount>`: Instantly buy items from bazaar.
- `/bz_sell <item_id> <amount>`: Instantly sell items to bazaar.
- `/bz_order_buy <item_id> <price> <amount>`: Place a buy order.
- `/bz_order_sell <item_id> <price> <amount>`: Place a sell order.
- `/bz_myorders`: View your active orders.
- `/bz_cancel <order_id>`: Cancel an order.
- `/bz_list`: List bazaar items.

### Collections

- `/collections [category]`: View your collections with tiers and rewards.
- `/collection_info <item>`: Get detailed info about a specific collection.
- `/collection_rewards`: View collection tier rewards and category bonuses.
- `/collection_leaderboard [item]`: View top collectors.

### Combat

- `/fight <location>`: Fight monsters interactively in various locations.
- `/combat_locations`: View all combat locations and their requirements.

### Crafting

- `/craft <item> [quantity]`: Craft an item.
- `/recipes`: View available crafting recipes.
- `/reforge <item>`: Reforge items.
- `/reforges`: View reforges.

### Dungeons

- `/dungeon <floor>`: Enter a dungeon and interact with its features.
- `/dungeon_score`: View your dungeon score.

### Economy Stats

- `/flip_stats`: View your bazaar flipping statistics.
- `/market_trends`: View current market trends.
- `/auction_insights`: View auction house insights and bot activity.
- `/economy_overview`: View complete economy overview.

### Enchanting

- `/enchant <item> <enchantment> <level>`: Enchant an item.
- `/anvil <item1> <item2>`: Combine items in the anvil.

### Events

- `/events`: View active SkyBlock events.
- `/calendar`: View the SkyBlock calendar.

### Gathering

- `/mine`: Go mining and collect resources.
- `/farm`: Farm crops.
- `/fish`: Go fishing.
- `/forage`: Chop trees.
- `/taming`: Level up your taming skill.

### Inventory

- `/inventory`: View your inventory.
- `/enderchest`: View your ender chest.
- `/wardrobe`: View and manage your wardrobe.
- `/accessories`: View your accessory bag.

### Island

- `/island`: Visit your private island.
- `/search_fairy_soul`: Search for a fairy soul.
- `/fairy_souls`: Check your fairy soul progress.

### Leaderboard

- `/leaderboard <category>`: View leaderboards (richest, net worth, skill average, catacombs, slayer XP).

### Marketplace

- `/trade_interactive <user>`: Trade with another player interactively.

### Merchants

- `/merchants`: View available merchant deals.
- `/merchant_buy <deal_id>`: Buy from a merchant.
- `/merchant_sell <deal_id>`: Sell to a merchant.

### Minions

- `/minions`: View and manage your minions.
- `/minion_upgrade <minion_id>`: Upgrade a minion.
- `/minion_storage <minion_id>`: View minion storage.

### Misc

- Various utility and fun commands (see `misc.py`).

### Pets

- `/pets`: View and manage your pets.
- `/pet_equip <pet_id>`: Equip a pet.
- `/pet_unequip`: Unequip your active pet.

### Profile

- `/profile`: View your SkyBlock profile.
- `/stats`: View your detailed stats.

### Progression

- `/guide`: View the beginner's guide.
- `/tips`: Get trading and economy tips.
- `/progression`: View your progression and milestones.

### Quests

- `/quests`: View available quests.
- `/claim_quest <quest_id>`: Claim a completed quest reward.
- `/daily_reward`: Claim your daily reward.

### Skills

- `/skills`: View all your skills.
- `/alchemy`: Brew potions.
- `/carpentry`: Improve your carpentry skill.
- `/runecrafting`: Level up your runecrafting.
- `/social`: Increase your social skill.

### Slayer

- `/slayer <boss> <tier>`: Fight a slayer boss.
- `/slayer_stats`: View your slayer statistics.

### Stocks

- `/stocks`: View the stock market.
- `/portfolio`: View your stock portfolio.
- `/stock_info <symbol>`: Get detailed information about a stock.
- `/stock_buy <symbol> <shares>`: Buy stocks.
- `/stock_sell <symbol> <shares>`: Sell stocks.

### Tool Progression

- `/progression_path`: View your tool progression path.

---

## Usage

- **Bot Commands**: Interact with the bot via Discord using supported commands. See `cogs/commands/` for available commands and usage examples.
- **Event Listeners**: Game and Discord events are handled automatically. You can add custom listeners in `cogs/events/`.
- **Database Operations**: All game actions are tracked in the database. Use migration and backup tools to manage schema and data.
- **Extending the Bot**:
  - Add new commands in `cogs/commands/` and register them in the cog loader.
  - Add event listeners in `cogs/events/`.
  - Extend database models in `database/` and update migrations.
  - Add helper logic in `utils/` for new features.

---

## Extending the Bot

- **Add a Command**: Create a new Python file in `cogs/commands/` and define your command logic. Register it in the cog loader.
- **Add an Event Listener**: Add a new listener in `cogs/events/` to handle custom game or Discord events.
- **Update Database Models**: Modify or add new models in `database/` and create migration scripts in `migrations/scripts/`.
- **Add Utilities**: Place helper functions or classes in `utils/` for stat calculations, data management, etc.
- **Testing**: Use the provided migration and backup tools to safely test new features.

---

## Contributing

Pull requests and issues are welcome! Please follow best practices:

- Write clear, documented code.
- Add docstrings and comments for new modules and functions.
- Update the README and migration scripts as needed.
- Test your changes before submitting.
- Respect the project structure and naming conventions.

---

## License

This project is for educational purposes and is not affiliated with Hypixel. See LICENSE for details.

---

## Credits

- Inspired by Hypixel Skyblock and the Discord.py community.
- Special thanks to contributors and testers.
