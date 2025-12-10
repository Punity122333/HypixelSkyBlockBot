import discord
from discord.ui import View, Button
from components.buttons.wiki_buttons import (
    WikiFirstButton,
    WikiPreviousButton,
    WikiNextButton,
    WikiLastButton
)

class WikiPaginationView(View):
    def __init__(self, pages: list, title: str):
        super().__init__(timeout=180)
        self.pages = pages
        self.title = title
        self.current_page = 0
        
        self.first_page = WikiFirstButton(self)
        self.prev_page = WikiPreviousButton(self)
        self.next_page = WikiNextButton(self)
        self.last_page = WikiLastButton(self)
        
        self.add_item(self.first_page)
        self.add_item(self.prev_page)
        self.add_item(self.next_page)
        self.add_item(self.last_page)
        
        self.update_buttons()
    
    def update_buttons(self):
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page >= len(self.pages) - 1
        self.last_page.disabled = self.current_page >= len(self.pages) - 1
    
    def get_embed(self):
        embed = discord.Embed(
            title=f"📚 {self.title} Wiki" if self.current_page == 0 else None,
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)}")
        return embed
    
    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True