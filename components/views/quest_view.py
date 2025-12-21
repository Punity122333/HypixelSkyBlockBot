import discord
from components.buttons.quest_buttons import (
    QuestActiveButton,
    QuestCompletedButton,
    QuestPreviousButton,
    QuestNextButton,
    QuestClaimButton
)

class QuestMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'active'
        self.page = 0
        self.items_per_page = 5
        self.active_quests = []
        self.completed_quests = []
        self.user_quests_data = []
        
        self._update_buttons()
    
    async def load_quests(self):
        quests_from_db = await self.bot.game_data.get_all_game_quests()
        
        if quests_from_db:
            quest_data = {}
            for quest in quests_from_db:
                quest_data[quest['quest_id']] = quest
        else:
            quest_data = {}
        
        for quest_id in quest_data.keys():
            existing_quest = await self.bot.db.get_quest(self.user_id, quest_id)
            if not existing_quest:
                await self.bot.db.create_quest(self.user_id, quest_id, 0)
        
        user_quests = await self.bot.db.get_user_quests(self.user_id)
        
        self.active_quests = []
        self.completed_quests = []
        self.user_quests_data = []
        
        for idx, quest in enumerate(user_quests):
            quest_id = quest['quest_id']
            quest_info = await self.bot.game_data.get_game_quest(quest_id)
            if not quest_info:
                continue
            
            if quest_info['requirement_type'] == 'collection':
                current_amount = await self.bot.db.get_collection(self.user_id, quest_info['requirement_item'])
            else:
                current_amount = quest['progress']
            
            required_amount = quest_info['requirement_amount']
            
            quest_entry = {
                'serial': idx + 1,
                'quest_id': quest_id,
                'name': quest_info['name'],
                'description': quest_info['description'],
                'current': current_amount,
                'required': required_amount,
                'reward_coins': quest_info['reward_coins'],
                'reward_items': quest_info['reward_items'],
                'completed': quest['completed'],
                'claimed': quest['claimed']
            }
            
            self.user_quests_data.append(quest_entry)
            
            if quest['completed'] and quest['claimed']:
                self.completed_quests.append(quest_entry)
            elif quest['completed'] and not quest['claimed']:
                self.active_quests.append(quest_entry)
            else:
                self.active_quests.append(quest_entry)
                
                if current_amount >= required_amount and not quest['completed']:
                    await self.bot.db.complete_quest(self.user_id, quest_id)
                    quest_entry['completed'] = True
    
    async def get_embed(self):
        if self.current_view == 'active':
            return await self.get_active_embed()
        elif self.current_view == 'completed':
            return await self.get_completed_embed()
        else:
            return await self.get_active_embed()
    
    async def get_active_embed(self):
        embed = discord.Embed(
            title="📜 Active Quests",
            description="Complete quests to earn rewards!",
            color=discord.Color.gold()
        )
        
        if not self.active_quests:
            embed.description = "No active quests available!"
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.active_quests))
            page_quests = self.active_quests[start:end]
            
            for quest in page_quests:
                if quest['completed'] and not quest['claimed']:
                    value = f"✅ **COMPLETE - Ready to claim!**\nReward: 💰 {quest['reward_coins']:,} coins"
                    if quest['reward_items']:
                        items_text = ", ".join([f"{amount}x {item_id}" for item_id, amount in quest['reward_items']])
                        value += f"\n🎁 {items_text}"
                    value += f"\nUse claim button or `/quest claim {quest['serial']}`"
                else:
                    progress_bar = self.create_progress_bar(quest['current'], quest['required'])
                    value = f"{quest['description']}\nProgress: {quest['current']}/{quest['required']} {progress_bar}\nReward: 💰 {quest['reward_coins']:,} coins"
                
                embed.add_field(
                    name=f"#{quest['serial']}: {quest['name']}",
                    value=value,
                    inline=False
                )
        
        total_pages = (len(self.active_quests) + self.items_per_page - 1) // self.items_per_page if self.active_quests else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} | Use buttons to navigate")
        return embed
    
    async def get_completed_embed(self):
        embed = discord.Embed(
            title="✅ Completed Quests",
            description=f"You've completed {len(self.completed_quests)} quests!",
            color=discord.Color.green()
        )
        
        if not self.completed_quests:
            embed.description = "No completed quests yet!"
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.completed_quests))
            page_quests = self.completed_quests[start:end]
            
            quest_names = []
            for quest in page_quests:
                quest_names.append(f"#{quest['serial']}: {quest['name']} - 💰 {quest['reward_coins']:,} coins")
            
            embed.add_field(
                name="Completed",
                value="\n".join(quest_names) if quest_names else "None",
                inline=False
            )
        
        total_pages = (len(self.completed_quests) + self.items_per_page - 1) // self.items_per_page if self.completed_quests else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    def create_progress_bar(self, current: int, required: int, length: int = 10) -> str:
        filled = int((current / required) * length) if required > 0 else 0
        filled = min(filled, length)
        empty = length - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def _update_buttons(self):
        self.clear_items()
        
        active_button = QuestActiveButton(self)
        self.add_item(active_button)
        
        completed_button = QuestCompletedButton(self)
        self.add_item(completed_button)
        
        data_list = self.active_quests if self.current_view == 'active' else self.completed_quests
        
        if data_list:
            total_pages = (len(data_list) + self.items_per_page - 1) // self.items_per_page
            if total_pages > 1:
                prev_button = QuestPreviousButton(self)
                self.add_item(prev_button)
                
                next_button = QuestNextButton(self)
                self.add_item(next_button)
        
        claim_button = QuestClaimButton(self)
        self.add_item(claim_button)
