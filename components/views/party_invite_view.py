import discord
from discord.ui import View, Button
from utils.systems.party_system import PartySystem
from components.buttons.party_invite_buttons import (
    PartyInviteAcceptButton,
    PartyInviteDeclineButton
)

class PartyInviteView(View):
    def __init__(self, user_id: int, party_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.party_id = party_id
        
        self.add_item(PartyInviteAcceptButton(self))
        self.add_item(PartyInviteDeclineButton(self))