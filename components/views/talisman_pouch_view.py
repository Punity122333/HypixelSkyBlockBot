import discord
from components.buttons.talisman_pouch_menu_buttons import (
    TalismanMainButton,
    TalismanAddButton,
    TalismanRemoveButton,
    TalismanPreviousButton,
    TalismanNextButton
)
from components.buttons.upgrade_talisman_pouch_button import UpgradeTalismanPouchButton

class TalismanPouchMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.page = 0
        self.items_per_page = 10
        self.talisman_list = []
        
        self.main_button = TalismanMainButton(self)
        self.add_button = TalismanAddButton(self)
        self.remove_button = TalismanRemoveButton(self)
        self.prev_button = TalismanPreviousButton(self)
        self.next_button = TalismanNextButton(self)
        self.upgrade_button = UpgradeTalismanPouchButton(self)
        
        self._update_buttons()
    
    async def load_talismans(self):
        from utils.systems.talisman_pouch_system import TalismanPouchSystem
        self.talisman_list = await TalismanPouchSystem.get_talisman_pouch(self.bot.db, self.user_id)
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'manage':
            return await self.get_manage_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        from utils.systems.talisman_pouch_system import TalismanPouchSystem
        
        talismans = await TalismanPouchSystem.get_talisman_pouch(self.bot.db, self.user_id)
        bonuses = await TalismanPouchSystem.get_talisman_bonuses(self.bot.db, self.user_id)
        current_capacity = await self.bot.db.get_talisman_pouch_capacity(self.user_id)
        
        embed = discord.Embed(
            title=f"📿 Talisman Pouch",
            description=f"Talismans provide passive stat bonuses\n{len(talismans)}/{current_capacity} slots used",
            color=discord.Color.purple()
        )
        
        if bonuses:
            stat_list = []
            for stat, value in bonuses.items():
                stat_display = stat.replace('_', ' ').title()
                stat_list.append(f"**{stat_display}:** +{value}")
            
            embed.add_field(name="📊 Total Stat Bonuses", value="\n".join(stat_list) if stat_list else "No bonuses", inline=False)
        else:
            embed.add_field(name="📊 Total Stat Bonuses", value="No bonuses", inline=False)
        
        if talismans:
            talisman_preview = []
            for i, talisman_data in enumerate(talismans[:5]):
                talisman_id = talisman_data['talisman_id']
                item = await self.bot.game_data.get_item(talisman_id)
                if item:
                    talisman_preview.append(f"{i+1}. **{item.name}** ({item.rarity})")
            
            if talisman_preview:
                embed.add_field(name="📿 Equipped Talismans (Preview)", value="\n".join(talisman_preview), inline=False)
            
            if len(talismans) > 5:
                embed.add_field(name="", value=f"*+{len(talismans) - 5} more... (View in Manage tab)*", inline=False)
        
        embed.set_footer(text="Use buttons to manage your talisman pouch")
        return embed
    
    async def get_manage_embed(self):
        from utils.systems.talisman_pouch_system import TalismanPouchSystem
        
        if not self.talisman_list:
            await self.load_talismans()
        
        current_capacity = await self.bot.db.get_talisman_pouch_capacity(self.user_id)
        
        embed = discord.Embed(
            title=f"📿 Manage Talisman Pouch",
            description=f"{len(self.talisman_list)}/{current_capacity} slots used",
            color=discord.Color.purple()
        )
        
        if not self.talisman_list:
            embed.add_field(name="No Talismans", value="Your pouch is empty. Use Add to equip talismans!", inline=False)
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.talisman_list))
            page_talismans = self.talisman_list[start:end]
            
            talisman_text = ""
            for i, talisman_data in enumerate(page_talismans):
                slot = talisman_data['slot']
                talisman_id = talisman_data['talisman_id']
                item = await self.bot.game_data.get_item(talisman_id)
                if item:
                    stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}" for k, v in item.stats.items()])
                    talisman_text += f"**Slot {slot+1}:** {item.name} ({item.rarity})\n{stats_str}\n\n"
            
            if talisman_text:
                embed.add_field(name="Equipped Talismans", value=talisman_text, inline=False)
        
        total_pages = (len(self.talisman_list) + self.items_per_page - 1) // self.items_per_page if self.talisman_list else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.add_button)
        self.add_item(self.remove_button)
        self.add_item(self.upgrade_button)
        
        if self.current_view == 'manage' and self.talisman_list:
            total_pages = (len(self.talisman_list) + self.items_per_page - 1) // self.items_per_page
            if total_pages > 1:
                self.add_item(self.prev_button)
                self.add_item(self.next_button)
