# Achievement System Quick Reference

## Quick Integration Checklist

For each command that updates player progress:

- [ ] Import AchievementSystem
- [ ] Update player stats/progress
- [ ] Call appropriate achievement check method
- [ ] (Optional) Check for first-time achievements

## Common Achievement Patterns

### Pattern 1: Skill Updates
```python
from utils.systems.achievement_system import AchievementSystem

# After updating skill
await AchievementSystem.check_skill_achievements(
    self.bot.db, interaction, interaction.user.id, 
    'mining',  # skill name
    new_level  # current level
)
```

### Pattern 2: First Time Actions
```python
progression = await self.bot.db.get_player_progression(interaction.user.id)
if not progression or not progression.get('first_mine_date'):
    import time
    await self.bot.db.update_progression(
        interaction.user.id, first_mine_date=int(time.time())
    )
    await AchievementSystem.unlock_single_achievement(
        self.bot.db, interaction, interaction.user.id, 'first_mine'
    )
```

### Pattern 3: Count-Based Achievements
```python
# Track and check count
stats = await self.bot.db.get_player_stats(interaction.user.id)
total_kills = stats.get('total_kills', 0) + 1
await self.bot.db.update_player_stats(interaction.user.id, total_kills=total_kills)

await AchievementSystem.check_combat_achievements(
    self.bot.db, interaction, interaction.user.id, kills=total_kills
)
```

## Achievement Check Methods

| Method | When to Use | Parameters |
|--------|-------------|------------|
| `check_skill_achievements()` | After skill XP gain | skill_name, level |
| `check_wealth_achievements()` | After coins change | total_wealth |
| `check_combat_achievements()` | After defeating enemy | kills, wins |
| `check_collection_achievements()` | After collection update | collection_name, tier |
| `check_dungeon_achievements()` | After dungeon complete | dungeon_count |
| `check_slayer_achievements()` | After slayer complete | slayer_count |
| `check_minion_achievements()` | After placing minion | unique_minion_count |
| `check_auction_achievements()` | After creating auction | auction_count |
| `check_bazaar_profit_achievements()` | After bazaar trade | total_profit |
| `check_pet_achievements()` | After getting/leveling pet | pet_rarity, pet_level |
| `check_fairy_soul_achievements()` | After collecting soul | soul_count |
| `check_hotm_achievements()` | After HOTM upgrade | hotm_tier |
| `check_death_achievements()` | After player death | death_count |
| `unlock_single_achievement()` | For specific achievements | achievement_id |

## First-Time Achievement IDs

- `first_mine` - First block mined
- `first_farm` - First crop harvested  
- `first_fish` - First fish caught
- `first_forage` - First tree chopped
- `first_craft` - First item crafted
- `first_kill` - First enemy defeated
- `first_auction` - First auction created
- `first_bazaar` - First bazaar transaction
- `first_dungeon` - First dungeon completed
- `first_slayer` - First slayer completed
- `first_minion` - First minion placed
- `first_enchant` - First item enchanted
- `first_reforge` - First item reforged
- `first_pet` - First pet obtained

## Requirement Types in Database

| Type | Description | Example |
|------|-------------|---------|
| `skill_level` | Skill level threshold | mining_50 |
| `coins` | Total wealth | wealth_1m |
| `kills` | Total enemy kills | kills_1000 |
| `dungeons` | Dungeons completed | dungeon_100 |
| `slayers` | Slayers completed | slayer_50 |
| `minions` | Unique minions | minions_25 |
| `auctions` | Auctions created | auction_100 |
| `profit` | Bazaar profit | bazaar_profit_1m |
| `collection_tier` | Collection tier | collection_tier_5 |
| `pet_rarity` | Pet rarity (1-5) | pet_legendary |
| `pet_level` | Pet level | pet_level_100 |
| `fairy_souls` | Souls collected | fairy_soul_100 |
| `hotm_tier` | HOTM tier | hotm_tier_10 |
| `deaths` | Times died | death_100 |
| `crafts` | Items crafted | craft_1000 |
| `enchants` | Items enchanted | enchant_100 |
| `reforges` | Items reforged | reforge_100 |
| `action` | One-time action | first_mine |

## Command Integration Status

✅ Already integrated:
- gathering.py (skills + first-time)
- crafting.py (crafts + first craft + legendary)
- enchanting.py (enchants + first enchant + max level)

🔧 Need integration:
- combat.py (kills)
- dungeons.py (completions)
- slayer.py (completions)
- minions.py (placement)
- pets.py (acquisition/leveling)
- auction.py (creation)
- bazaar.py (profits)
- collections.py (tiers)
- hotm.py (tiers)
- profile.py (wealth)
- All other skill commands

## Testing

```bash
# Run achievement tests
python test_achievements.py

# Run migration
python -m migrations.migration_runner

# Check database
sqlite3 skyblock.db "SELECT COUNT(*) FROM game_achievements;"
```

## Adding New Achievements

1. Create migration file in `migrations/scripts/`
2. Insert achievement:
```sql
INSERT OR IGNORE INTO game_achievements 
(achievement_id, name, description, category, icon, requirement_type, requirement_value) 
VALUES
('your_id', 'Name', 'Description', 'Category', '🎯', 'requirement_type', value);
```
3. Run migration
4. Achievement automatically works!

## Troubleshooting

**Achievement not unlocking?**
- Check requirement_type matches what you're checking
- Verify requirement_value is correct
- Ensure stats are being updated before check

**Duplicate notifications?**
- System prevents duplicates automatically
- If seeing duplicates, check if calling twice

**No notification?**
- Check interaction is passed correctly
- Verify achievement exists in database
- Check requirement is met

## Full Example

```python
# At top of file
from utils.systems.achievement_system import AchievementSystem

# In command
@app_commands.command(name="mine")
async def mine(self, interaction: discord.Interaction):
    await interaction.response.defer()
    
    # 1. Check first time
    progression = await self.bot.db.get_player_progression(interaction.user.id)
    if not progression.get('first_mine_date'):
        import time
        await self.bot.db.update_progression(
            interaction.user.id, first_mine_date=int(time.time())
        )
        await AchievementSystem.unlock_single_achievement(
            self.bot.db, interaction, interaction.user.id, 'first_mine'
        )
    
    # 2. Mining logic here...
    
    # 3. Update skill
    new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
    await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)
    
    # 4. Check skill achievements
    await AchievementSystem.check_skill_achievements(
        self.bot.db, interaction, interaction.user.id, 'mining', new_level
    )
    
    # 5. Update collection
    collection = await self.bot.db.get_collection(interaction.user.id, 'cobblestone')
    
    # 6. Check collection achievements
    await AchievementSystem.check_collection_achievements(
        self.bot.db, interaction, interaction.user.id, 'cobblestone', collection['tier']
    )
    
    # 7. Update wealth
    player = await self.bot.db.get_player(interaction.user.id)
    wealth = player['coins'] + player.get('bank_balance', 0)
    
    # 8. Check wealth achievements
    await AchievementSystem.check_wealth_achievements(
        self.bot.db, interaction, interaction.user.id, wealth
    )
    
    # 9. Send response
    await interaction.followup.send(embed=embed)
```
