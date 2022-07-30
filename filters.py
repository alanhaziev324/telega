from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

host = "127.0.0.1"
user = "postgres"
password = "postgres"
db_name = "postgres"


class IsAdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin
