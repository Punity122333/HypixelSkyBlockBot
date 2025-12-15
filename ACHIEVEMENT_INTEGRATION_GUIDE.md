# Achievement System Integration Guide

## Overview
The new achievement system is database-driven and checks for achievements dynamically. This guide shows how to integrate achievement checking into commands.

## Setup

### Import Required Modules
```python
from utils.systems.achievement_system import AchievementSystem
```

## Common Achievement Patterns

### 1. First-Time Actions

When a player does something for the first time:

```python
# Example: First mine
import time
progression = await self.bot.db.get_player_progression(user_id)
if not progression or not progression.get('first_mine_date'):
    await self.bot.db.update_progression(
        user_id,
        first_mine_date=int(time.time())
    )
    await AchievementSystem.unlock_single_achievement(
        self.bot.db, interaction, user_id, 'first_mine'
    )
```

### 2. Skill Level Achievements

After updating a skill:

```python
# After skill XP is added and level is calculated
new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
await self.bot.db.update_skill(user_id, 'mining', xp=new_xp, level=new_level)

# Check skill achievements (handles all skill milestones automatically)
await AchievementSystem.check_skill_achievements(
    self.bot.db, interaction, user_id, 'mining', new_level
)
```

### 3. Wealth Achievements

After coins are added/changed:

```python
player = await self.bot.db.get_player(user_id)
await AchievementSystem.check_wealth_achievements(
    self.bot.db, interaction, user_id, player['coins']
)
```

### 4. Combat Achievements

After combat:

```python
# Get total kills from stats
stats = await self.bot.db.get_player_stats(user_id)
total_kills = stats.get('kills', 0)

await AchievementSystem.check_combat_achievements(
    self.bot.db, interaction, user_id, kills=total_kills
)
```

### 5. Gathering Achievements

After gathering resources:

```python
await AchievementSystem.check_gathering_achievements(
    self.bot.db, interaction, user_id, resource_type='cobblestone', amount=1
)
```

### 6. Collection Achievements

When collection tier increases:

```python
collection = await self.bot.db.get_collection(user_id, 'wheat')
await AchievementSystem.check_collection_achievements(
    self.bot.db, interaction, user_id, 'wheat', collection['tier']
)
```

### 7. Specific Single Achievements

For unique one-off achievements:

```python
# Example: First dungeon completion
await AchievementSystem.unlock_single_achievement(
    self.bot.db, interaction, user_id, 'first_dungeon'
)
```

## Achievement Categories in Database

All achievements are stored in `game_achievements` table with these categories:
- **First Time** - First actions
- **Wealth** - Coin milestones
- **Skills** - Skill level milestones
- **Combat** - Kill count milestones
- **Dungeons** - Dungeon completions
- **Slayer** - Slayer quest completions
- **Minions** - Minion-related achievements
- **Trading** - Auction/bazaar achievements
- **Collections** - Collection tier achievements
- **Mining** - HOTM-related achievements
- **Pets** - Pet-related achievements
- **Exploration** - Fairy souls, etc.
- **Special** - Unique achievements
- **Cursed** - Funny/negative achievements

## Integration Checklist by Command Type

### Mining Commands (`/mine`, etc.)
- [x] First mine achievement
- [x] Skill level achievements (mining_5, mining_10, etc.)
- [ ] Gathering achievements for first cobblestone, etc.
- [ ] Collection achievements for mining collections
- [ ] HOTM tier achievements

### Farming Commands (`/farm`)
- [x] First farm achievement
- [x] Skill level achievements (farming_5, farming_10, etc.)
- [ ] Gathering achievements for first crop
- [ ] Collection achievements for farming collections

### Fishing Commands (`/fish`)
- [ ] First fish achievement
- [ ] Skill level achievements
- [ ] Sea creature achievements

### Foraging Commands (`/forage`)
- [ ] First forage achievement
- [ ] Skill level achievements
- [ ] Tree spirit kills

### Combat Commands (`/fight`, `/dungeon`, `/slayer`)
- [ ] First kill achievement
- [ ] Kill count milestones (10, 100, 1000, etc.)
- [ ] First dungeon/slayer achievements
- [ ] Dungeon/slayer completion milestones
- [ ] Boss kill achievements

### Crafting Commands (`/craft`, `/enchant`, `/reforge`)
- [ ] First craft/enchant/reforge achievements
- [ ] Enchanting skill achievements

### Trading Commands (`/ah_create`, `/bz_buy`, `/bz_sell`)
- [ ] First auction/bazaar achievements
- [ ] Auction creation milestones
- [ ] Bazaar profit milestones

### Economy Commands (`/bank`, `/coins`)
- [x] Wealth achievements (automatically checked)
- [ ] Bank balance achievements

### Minion Commands (`/minion_place`, etc.)
- [ ] First minion achievement
- [ ] Minion count achievements
- [ ] All slots unlocked achievement

### Pet Commands (`/pet`)
- [ ] First pet achievement
- [ ] Pet rarity achievements
- [ ] Pet level achievements

### Collection Commands
- [ ] Collection tier achievements
- [ ] Collection category completion

### Miscellaneous
- [ ] Death achievements (in combat loss)
- [ ] Broke achievement (when coins = 0)
- [ ] Co-op creation
- [ ] Party hosting
- [ ] Museum donations
- [ ] Fairy soul collection

## Example: Full Integration in a Command

```python
@app_commands.command(name="mine", description="Go mining")
async def mine(self, interaction: discord.Interaction, location: str):
    await interaction.response.defer()
    user_id = interaction.user.id
    
    # Check first time
    progression = await self.bot.db.get_player_progression(user_id)
    if not progression or not progression.get('first_mine_date'):
        import time
        await self.bot.db.update_progression(
            user_id,
            first_mine_date=int(time.time())
        )
        await AchievementSystem.unlock_single_achievement(
            self.bot.db, interaction, user_id, 'first_mine'
        )
    
    # Do mining logic...
    result = await GatheringSystem.mine(self.bot.db, user_id, location)
    
    # Update skill
    new_level = result['new_level']
    await AchievementSystem.check_skill_achievements(
        self.bot.db, interaction, user_id, 'mining', new_level
    )
    
    # Check gathering achievement
    await AchievementSystem.check_gathering_achievements(
        self.bot.db, interaction, user_id, 'cobblestone', 1
    )
    
    # Check collection achievements if tier changed
    collection = await self.bot.db.get_collection(user_id, 'cobblestone')
    await AchievementSystem.check_collection_achievements(
        self.bot.db, interaction, user_id, 'cobblestone', collection['tier']
    )
    
    # Send result
    embed = discord.Embed(title="Mining Complete!", ...)
    await interaction.followup.send(embed=embed)
```

## Notes

- Achievement notifications are sent automatically via `AchievementSystem.check_and_notify()`
- Multiple achievements can be unlocked in one action
- All achievement checks are non-blocking and won't cause errors if they fail
- The system prevents duplicate unlocks automatically
- Achievement data is loaded from the database, not hardcoded

## Adding New Achievements

To add new achievements, insert into the `game_achievements` table:

```sql
INSERT INTO game_achievements (achievement_id, name, description, category, icon, requirement_type, requirement_value) 
VALUES ('my_new_achievement', 'Achievement Name', 'Description', 'Category', '🎉', 'action', 1);
```

Then use in code:

```python
await AchievementSystem.unlock_single_achievement(
    self.bot.db, interaction, user_id, 'my_new_achievement'
)
```
