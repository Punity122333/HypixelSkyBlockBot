# Achievement Integration Examples

This guide shows how to integrate the achievement system into various commands.

## Import Statement

Add this import at the top of your command file:
```python
from utils.systems.achievement_system import AchievementSystem
```

## 1. Skill-Based Commands (Mining, Farming, Combat, etc.)

When updating skills, check for skill achievements:

```python
# After updating skill level
new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)

# Check for skill achievements
await AchievementSystem.check_skill_achievements(
    self.bot.db, 
    interaction, 
    interaction.user.id, 
    'mining',  # skill name
    new_level  # current level
)
```

## 2. Combat Commands

When tracking kills:

```python
# After defeating an enemy
stats = await self.bot.db.get_player_stats(interaction.user.id)
total_kills = stats.get('total_kills', 0) + 1

await self.bot.db.update_player_stats(interaction.user.id, total_kills=total_kills)

# Check combat achievements
await AchievementSystem.check_combat_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    kills=total_kills
)
```

## 3. Wealth/Economy Commands

When updating coins:

```python
# After adding/removing coins
player = await self.bot.db.get_player(interaction.user.id)
total_wealth = player['coins'] + player.get('bank_balance', 0)

# Check wealth achievements
await AchievementSystem.check_wealth_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    wealth=total_wealth
)
```

## 4. Collection Commands

When updating collections:

```python
# After updating a collection
collection_data = await self.bot.db.get_collection(interaction.user.id, 'wheat')
tier = collection_data.get('tier', 0)

# Check collection achievements
await AchievementSystem.check_collection_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    'wheat',  # collection name
    tier      # collection tier
)
```

## 5. Dungeon Commands

When completing dungeons:

```python
# After completing a dungeon
stats = await self.bot.db.get_player_dungeon_stats(interaction.user.id)
dungeon_count = stats.get('dungeons_completed', 0)

# Check dungeon achievements
await AchievementSystem.check_dungeon_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    dungeon_count
)
```

## 6. Slayer Commands

When completing slayers:

```python
# After completing a slayer
slayer_progress = await self.bot.db.get_slayer_progress(interaction.user.id)
total_slayers = sum(s.get('kills', 0) for s in slayer_progress.values())

# Check slayer achievements
await AchievementSystem.check_slayer_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    total_slayers
)
```

## 7. Minion Commands

When placing minions:

```python
# After placing a minion
minions = await self.bot.db.get_user_minions(interaction.user.id)
unique_minions = len(set(m['minion_type'] for m in minions))

# Check minion achievements
await AchievementSystem.check_minion_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    unique_minions
)
```

## 8. Auction Commands

When creating auctions:

```python
# After creating an auction
auctions = await self.bot.db.get_player_auctions(interaction.user.id)
auction_count = len(auctions)

# Check auction achievements
await AchievementSystem.check_auction_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    auction_count
)
```

## 9. Bazaar Commands

When profiting from bazaar:

```python
# After a successful bazaar flip
total_profit = await self.bot.db.get_total_bazaar_profit(interaction.user.id)

# Check bazaar profit achievements
await AchievementSystem.check_bazaar_profit_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    total_profit
)
```

## 10. Pet Commands

When obtaining or leveling pets:

```python
# After getting a new pet
pet = await self.bot.db.get_pet(pet_id)
rarity_value = {'COMMON': 1, 'UNCOMMON': 2, 'RARE': 3, 'EPIC': 4, 'LEGENDARY': 5}[pet['rarity']]

# Check pet rarity achievement
await AchievementSystem.check_pet_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    pet_rarity=rarity_value,
    pet_level=pet.get('level', 1)
)
```

## 11. HOTM (Heart of the Mountain) Commands

When upgrading HOTM:

```python
# After upgrading HOTM tier
hotm_data = await self.bot.db.get_hotm_data(interaction.user.id)
hotm_tier = hotm_data.get('hotm_tier', 0)

# Check HOTM achievements
await AchievementSystem.check_hotm_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    hotm_tier
)
```

## 12. Fairy Soul Commands

When collecting fairy souls:

```python
# After collecting a fairy soul
collected_souls = await self.bot.db.get_collected_fairy_souls(interaction.user.id)
soul_count = len(collected_souls)

# Check fairy soul achievements
await AchievementSystem.check_fairy_soul_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    soul_count
)
```

## 13. First-Time Actions

For first-time actions (mining, farming, fishing, etc.):

```python
# Check if this is the player's first time doing this action
progression = await self.bot.db.get_player_progression(interaction.user.id)
if not progression.get('first_mine_date'):
    import time
    await self.bot.db.update_progression(
        interaction.user.id,
        first_mine_date=int(time.time())
    )
    
    # Unlock first mine achievement
    await AchievementSystem.unlock_single_achievement(
        self.bot.db,
        interaction,
        interaction.user.id,
        'first_mine'
    )
```

## 14. Death Commands

When a player dies:

```python
# After player death
stats = await self.bot.db.get_player_stats(interaction.user.id)
death_count = stats.get('deaths', 0) + 1
await self.bot.db.update_player_stats(interaction.user.id, deaths=death_count)

# Check death achievements (cursed)
await AchievementSystem.check_death_achievements(
    self.bot.db,
    interaction,
    interaction.user.id,
    death_count
)
```

## Best Practices

1. **Always check after state changes**: Check achievements after updating player stats/progress
2. **Use appropriate check functions**: Use the specific check function for the type of achievement
3. **Don't worry about duplicates**: The system automatically prevents duplicate unlocks
4. **Notifications are automatic**: The system will notify players when they unlock achievements
5. **Check multiple related achievements**: If an action affects multiple achievement types, check them all

## Full Example: Mining Command

Here's a complete example integrating multiple achievement checks:

```python
@app_commands.command(name="mine", description="Go mining")
async def mine(self, interaction: discord.Interaction):
    await interaction.response.defer()
    
    # ... mining logic ...
    
    # Check if first time mining
    progression = await self.bot.db.get_player_progression(interaction.user.id)
    if not progression.get('first_mine_date'):
        import time
        await self.bot.db.update_progression(
            interaction.user.id,
            first_mine_date=int(time.time())
        )
        await AchievementSystem.unlock_single_achievement(
            self.bot.db, interaction, interaction.user.id, 'first_mine'
        )
    
    # Update mining skill
    new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
    await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)
    
    # Check skill achievements
    await AchievementSystem.check_skill_achievements(
        self.bot.db, interaction, interaction.user.id, 'mining', new_level
    )
    
    # Update collections
    await self.bot.db.update_collection(interaction.user.id, 'cobblestone', amount)
    collection_data = await self.bot.db.get_collection(interaction.user.id, 'cobblestone')
    
    # Check collection achievements
    await AchievementSystem.check_collection_achievements(
        self.bot.db, interaction, interaction.user.id, 'cobblestone', collection_data['tier']
    )
    
    # Update wealth
    player = await self.bot.db.get_player(interaction.user.id)
    total_wealth = player['coins'] + player.get('bank_balance', 0)
    
    # Check wealth achievements
    await AchievementSystem.check_wealth_achievements(
        self.bot.db, interaction, interaction.user.id, total_wealth
    )
    
    # Send result embed
    await interaction.followup.send(embed=embed)
```

## Notes

- The achievement system loads all achievements from the database dynamically
- New achievements can be added via SQL migrations without code changes
- All achievement checking is done through the `AchievementSystem` helper class
- Achievements are only unlocked once per player (automatic duplicate prevention)
- Players receive ephemeral notifications when unlocking achievements
