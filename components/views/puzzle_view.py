from typing import TYPE_CHECKING
import discord
from discord.ui import View, Button
import random
from utils.systems.puzzle_system import Puzzle, PuzzleType
import asyncio

if TYPE_CHECKING:
    from main import SkyblockBot
    from components.views.dungeon_view import DungeonView
    

class PuzzleView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, puzzle: Puzzle, dungeon_view: "DungeonView"):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.puzzle = puzzle
        self.dungeon_view = dungeon_view
        self.setup_buttons()
    
    def setup_buttons(self):
        if 'options' in self.puzzle.data:
            for i, option in enumerate(self.puzzle.data['options']):
                button_style = [discord.ButtonStyle.primary, discord.ButtonStyle.success, discord.ButtonStyle.danger, discord.ButtonStyle.secondary][i % 4]
                button = Button(label=f"{option[:80]}", style=button_style, custom_id=f"option_{i}")
                button.callback = self.create_callback(i)
                self.add_item(button)
        
        elif self.puzzle.puzzle_type == PuzzleType.SEQUENCE:
            seq_type = self.puzzle.data.get('type', '')
            
            if seq_type == 'color_simon':
                colors = ['🔴', '🔵', '🟢', '🟡']
                for i, color in enumerate(colors):
                    button = Button(label=color, style=discord.ButtonStyle.secondary, custom_id=f"seq_{i}")
                    button.callback = self.create_sequence_callback(color)
                    self.add_item(button)
            
            elif seq_type == 'direction_sequence':
                directions = {'⬆️': 'up', '⬇️': 'down', '⬅️': 'left', '➡️': 'right'}
                for emoji, direction in directions.items():
                    button = Button(label=emoji, style=discord.ButtonStyle.secondary, custom_id=f"dir_{direction}")
                    button.callback = self.create_sequence_callback(emoji)
                    self.add_item(button)
            
            elif seq_type == 'number_sequence':
                for i in range(1, 10):
                    button = Button(label=str(i), style=discord.ButtonStyle.secondary, custom_id=f"num_{i}")
                    button.callback = self.create_sequence_callback(str(i))
                    self.add_item(button)
            
            submit_btn = Button(label="✅ Submit Sequence", style=discord.ButtonStyle.green, custom_id="submit_seq", row=4)
            submit_btn.callback = self.submit_sequence
            self.add_item(submit_btn)
            
            clear_btn = Button(label="🔄 Clear", style=discord.ButtonStyle.gray, custom_id="clear_seq", row=4)
            clear_btn.callback = self.clear_sequence
            self.add_item(clear_btn)
            
            self.sequence_input = []
        
        elif self.puzzle.puzzle_type == PuzzleType.MEMORY:
            solve_btn = Button(label="✅ I Memorized It!", style=discord.ButtonStyle.green, custom_id="solve_memory")
            solve_btn.callback = self.solve_memory
            self.add_item(solve_btn)
        
        hint_btn = Button(label="💡 Get Hint", style=discord.ButtonStyle.blurple, custom_id="hint", row=4)
        hint_btn.callback = self.show_hint
        self.add_item(hint_btn)
    
    def create_callback(self, option_index: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your puzzle!", ephemeral=True)
                return
            
            success, message = self.puzzle.attempt_solve(option_index)
            
            if success:
                embed = discord.Embed(
                    title="✅ Puzzle Solved!",
                    description=message,
                    color=discord.Color.green()
                )
                
                self.dungeon_view.current_puzzle = None
                self.dungeon_view.secrets_found += random.randint(1, 3)
                coins = random.randint(50, 150)
                self.dungeon_view.coins_gained_in_run += coins
                
                embed.add_field(name="Rewards", value=f"💰 {coins} coins\n✨ Secrets found!", inline=False)
                
                for child in self.children:
                    if isinstance(child, Button):
                        child.disabled = True

                await interaction.response.edit_message(embed=embed, view=self)

                await asyncio.sleep(2)
                dungeon_embed = discord.Embed(
                    title=f"🏰 {self.dungeon_view.floor_name} - Room {self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}",
                    description="Puzzle solved! Continue exploring.",
                    color=discord.Color.blue()
                )
                dungeon_embed.add_field(name="❤️ Health", value=f"{self.dungeon_view.current_health or 0}/{self.dungeon_view.max_health or 0}", inline=True)
                dungeon_embed.add_field(name="🗝️ Keys", value=str(self.dungeon_view.keys), inline=True)
                dungeon_embed.add_field(name="✨ Secrets", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)

                # Fix: Use interaction.followup.edit_message if possible, otherwise do nothing
                try:
                    if interaction.message is not None:
                        await interaction.followup.edit_message(message_id=interaction.message.id, embed=dungeon_embed, view=self.dungeon_view)
                except Exception:
                    pass
            else:
                embed = discord.Embed(
                    title="❌ Incorrect!",
                    description=message,
                    color=discord.Color.red()
                )
                
                if self.puzzle.attempts >= self.puzzle.max_attempts:
                    self.dungeon_view.current_puzzle = None
                    self.dungeon_view.puzzles_failed += 1
                    damage = random.randint(20, 40)
                    self.dungeon_view.current_health = (self.dungeon_view.current_health or 0) - damage
                    self.dungeon_view.total_damage += damage
                    
                    embed.add_field(name="Penalty", value=f"💥 Took {damage} damage from puzzle failure!", inline=False)
                    
                    for child in self.children:
                        if isinstance(child, Button):
                            child.disabled = True

                    await interaction.response.edit_message(embed=embed, view=self)

                    await asyncio.sleep(2)
                    dungeon_embed = discord.Embed(
                        title=f"🏰 {self.dungeon_view.floor_name} - Room {self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}",
                        description="Puzzle failed! Continue with caution.",
                        color=discord.Color.blue()
                    )
                    dungeon_embed.add_field(name="❤️ Health", value=f"{self.dungeon_view.current_health or 0}/{self.dungeon_view.max_health or 0}", inline=True)
                    dungeon_embed.add_field(name="🗝️ Keys", value=str(self.dungeon_view.keys), inline=True)
                    dungeon_embed.add_field(name="✨ Secrets", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)

                    try:
                        if interaction.message is not None:
                            await interaction.followup.edit_message(message_id=interaction.message.id, embed=dungeon_embed, view=self.dungeon_view)
                    except Exception:
                        pass
                else:
                    await interaction.response.edit_message(embed=embed, view=self)
        return callback
    
    def create_sequence_callback(self, value: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your puzzle!", ephemeral=True)
                return
            
            self.sequence_input.append(value)
            # Fix: Use the embed you just sent, not interaction.message.embeds[0]
            embed = discord.Embed(
                title="Sequence Input",
                description=f"Current sequence: {' '.join(self.sequence_input)}",
                color=discord.Color.purple()
            )
            await interaction.response.edit_message(embed=embed, view=self)
        return callback
    
    async def submit_sequence(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your puzzle!", ephemeral=True)
            return
        
        expected = self.puzzle.data.get('sequence', [])
        
        if self.puzzle.data.get('type') == 'number_sequence':
            try:
                actual = [int(x) for x in self.sequence_input]
            except:
                actual = self.sequence_input
        else:
            actual = self.sequence_input
        
        success = (actual == expected)
        
        if success:
            self.puzzle.solved = True
            message = "Sequence matched perfectly!"
        else:
            self.puzzle.attempts += 1
            remaining = self.puzzle.max_attempts - self.puzzle.attempts
            if remaining > 0:
                message = f"Wrong sequence! {remaining} attempts remaining."
            else:
                message = "Puzzle failed! Sequence was incorrect."
        
        if success:
            embed = discord.Embed(
                title="✅ Puzzle Solved!",
                description=message,
                color=discord.Color.green()
            )
            
            self.dungeon_view.current_puzzle = None
            self.dungeon_view.secrets_found += random.randint(1, 3)
            coins = random.randint(50, 150)
            self.dungeon_view.coins_gained_in_run += coins
            
            embed.add_field(name="Rewards", value=f"💰 {coins} coins\n✨ Secrets found!", inline=False)
            
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)

            await asyncio.sleep(2)
            dungeon_embed = discord.Embed(
                title=f"🏰 {self.dungeon_view.floor_name} - Room {self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}",
                description="Puzzle solved! Continue exploring.",
                color=discord.Color.blue()
            )
            dungeon_embed.add_field(name="❤️ Health", value=f"{self.dungeon_view.current_health or 0}/{self.dungeon_view.max_health or 0}", inline=True)
            dungeon_embed.add_field(name="🗝️ Keys", value=str(self.dungeon_view.keys), inline=True)
            dungeon_embed.add_field(name="✨ Secrets", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)

            try:
                if interaction.message is not None:
                    await interaction.followup.edit_message(message_id=interaction.message.id, embed=dungeon_embed, view=self.dungeon_view)
            except Exception:
                pass
        else:
            embed = discord.Embed(
                title="❌ Incorrect!",
                description=message,
                color=discord.Color.red()
            )
            
            if self.puzzle.attempts >= self.puzzle.max_attempts:
                self.dungeon_view.current_puzzle = None
                self.dungeon_view.puzzles_failed += 1
                damage = random.randint(20, 40)
                self.dungeon_view.current_health = (self.dungeon_view.current_health or 0) - damage
                self.dungeon_view.total_damage += damage
                
                embed.add_field(name="Penalty", value=f"💥 Took {damage} damage from puzzle failure!", inline=False)
                
                for child in self.children:
                    if isinstance(child, Button):
                        child.disabled = True

                await interaction.response.edit_message(embed=embed, view=self)

                await asyncio.sleep(2)
                dungeon_embed = discord.Embed(
                    title=f"🏰 {self.dungeon_view.floor_name} - Room {self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}",
                    description="Puzzle failed! Continue with caution.",
                    color=discord.Color.blue()
                )
                dungeon_embed.add_field(name="❤️ Health", value=f"{self.dungeon_view.current_health or 0}/{self.dungeon_view.max_health or 0}", inline=True)
                dungeon_embed.add_field(name="🗝️ Keys", value=str(self.dungeon_view.keys), inline=True)
                dungeon_embed.add_field(name="✨ Secrets", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)

                try:
                    if interaction.message is not None:
                        await interaction.followup.edit_message(message_id=interaction.message.id, embed=dungeon_embed, view=self.dungeon_view)
                except Exception:
                    pass
            else:
                self.sequence_input = []
                embed.set_footer(text="Sequence cleared. Try again!")
                await interaction.response.edit_message(embed=embed, view=self)

    async def clear_sequence(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your puzzle!", ephemeral=True)
            return
        
        self.sequence_input = []
        embed = discord.Embed(
            title="Sequence Cleared",
            description="Sequence cleared!",
            color=discord.Color.purple()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def solve_memory(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your puzzle!", ephemeral=True)
            return
        
        self.puzzle.solved = True
        
        embed = discord.Embed(
            title="✅ Puzzle Solved!",
            description="You successfully memorized all the pairs!",
            color=discord.Color.green()
        )
        
        self.dungeon_view.current_puzzle = None
        self.dungeon_view.secrets_found += random.randint(1, 3)
        coins = random.randint(50, 150)
        self.dungeon_view.coins_gained_in_run += coins
        
        embed.add_field(name="Rewards", value=f"💰 {coins} coins\n✨ Secrets found!", inline=False)
        
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

        await asyncio.sleep(2)
        dungeon_embed = discord.Embed(
            title=f"🏰 {self.dungeon_view.floor_name} - Room {self.dungeon_view.rooms_cleared}/{self.dungeon_view.total_rooms}",
            description="Puzzle solved! Continue exploring.",
            color=discord.Color.blue()
        )
        dungeon_embed.add_field(name="❤️ Health", value=f"{self.dungeon_view.current_health or 0}/{self.dungeon_view.max_health or 0}", inline=True)
        dungeon_embed.add_field(name="🗝️ Keys", value=str(self.dungeon_view.keys), inline=True)
        dungeon_embed.add_field(name="✨ Secrets", value=f"{self.dungeon_view.secrets_found}/{self.dungeon_view.max_secrets}", inline=True)

        try:
            if interaction.message is not None:
                await interaction.followup.edit_message(message_id=interaction.message.id, embed=dungeon_embed, view=self.dungeon_view)
        except Exception:
            pass

    async def show_hint(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your puzzle!", ephemeral=True)
            return
        
        hint = self.puzzle.get_hint()
        
        if hint:
            attempts_remaining = self.puzzle.max_attempts - self.puzzle.attempts
            embed = discord.Embed(
                title=f"💡 Puzzle Hint",
                description=hint,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Attempts remaining: {attempts_remaining}/{self.puzzle.max_attempts}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ No hints available for this puzzle!", ephemeral=True)
