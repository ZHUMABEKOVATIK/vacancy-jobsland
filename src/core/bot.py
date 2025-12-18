from aiogram import Bot
from dotenv import load_dotenv
from typing import AsyncIterator, Union
from aiogram.types import FSInputFile
from pathlib import Path
import os
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Union

from src.core.i18n.notification import get_approve_format, get_notification_format
from src.core.callbacks import ModAction
from src.core.i18n.vacancy.vacancy_types import TgPost

def get_group_id() -> int:
    raw = os.getenv("GROUP_ID")
    if not raw:
        raise RuntimeError("GROUP_ID not set")
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(f"GROUP_ID must be integer, got: {raw}")

class SendMessageConfig:
    def __init__(self, chat_id: int, message: str, message_id: int) -> None:
        self.chat_id = chat_id
        self.message = message
        self.message_id = message_id

class UserTelegramData:
    def __init__(self, full_name: str, chat_id: int, lastname: str, username: str) -> None:
        self.chat_id = chat_id
        self.full_name = full_name
        self.lastname = lastname
        self.username = username

class BotConfig:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def getBot(self) -> Bot:
        return self.bot
    
    async def get_id(self):
        me = await self.bot.get_me()
        return me.id
    
    async def send_message(self, chat_id: Union[int, str], message: str) -> SendMessageConfig:
        msg = await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        return SendMessageConfig(chat_id=msg.chat.id, message_id=msg.message_id, message=msg.text)
    
    async def get_user_with_chat_id(self, telegram_id: int) -> UserTelegramData:
        telegram_user = await self.bot.get_chat(telegram_id)
        return UserTelegramData(
            full_name=telegram_user.full_name, 
            chat_id=telegram_user.id, 
            lastname=telegram_user.last_name,
            username=telegram_user.username
        )

    async def get_chat_id(self, channel_username: str):
        if not channel_username.startswith("@"):
            channel_username = "@" + channel_username
        chat = await self.bot.get_chat(f"{channel_username}")
        return chat.id
    
    async def send_notification(self, request_id: int, chat_id: Union[int, str], lang_code: str):
        text = get_notification_format(request_id, lang_code)
        msg = await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return SendMessageConfig(chat_id=msg.chat.id, message=msg.text, message_id=msg.message_id)
    
    async def send_notification_approve(self, request_id: int, chat_id: Union[int, str], lang_code: str, channel_username: str):
        text = get_approve_format(request_id, lang_code, channel_username) 
        msg = await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return SendMessageConfig(chat_id=msg.chat.id, message=msg.text, message_id=msg.message_id)
    
    async def send_message_group(self, post_id, text: str, vacancy_type: str) -> SendMessageConfig:
        group_id = get_group_id()
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Принять",
                  callback_data=ModAction(action="accept", vacancy_type=vacancy_type, vacancy_id=post_id, token="...").pack())
        kb.button(text="❌ Отклонить",
                  callback_data=ModAction(action="reject", vacancy_type=vacancy_type, vacancy_id=post_id, token="...").pack())
        kb.adjust(2)
        msg = await self.bot.send_message(chat_id=group_id, text=text, parse_mode='HTML', reply_markup=kb.as_markup())
        return SendMessageConfig(chat_id=msg.chat.id, message=msg.text, message_id=msg.message_id)
    
    async def send_photo_group(self, post_id: int, text: str, vacancy_type: str, photo_url: str | None = None):
        group_id = get_group_id()
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Принять",
                  callback_data=ModAction(action="accept", vacancy_type=vacancy_type, vacancy_id=post_id, token="...").pack())
        kb.button(text="❌ Отклонить",
                  callback_data=ModAction(action="reject", vacancy_type=vacancy_type, vacancy_id=post_id, token="...").pack())
        kb.adjust(2)
        if photo_url is not None:
            msg = await self.bot.send_photo(chat_id=group_id, caption=text, photo=photo_url, parse_mode='HTML', reply_markup=kb.as_markup())
        else:
            msg = await self.bot.send_message(chat_id=group_id, text=text, parse_mode='HTML', reply_markup=kb.as_markup())
        return SendMessageConfig(chat_id=msg.chat.id, message=msg.caption, message_id=msg.message_id)
    
    # ---------------------------------------------------------------------------
    async def send_post(self, chat_id: Union[int, str], post: TgPost) -> SendMessageConfig:
        # Telegram ограничивает caption для фото ~1024 символа.
        def split_for_caption(text: str):
            if len(text) <= 2024:
                return text, None
            return text[:1020] + "…", text  # краткая подпись + полное сообщение следом

        if post.photo_path:
            # локальный файл или URL
            if post.photo_path.startswith("http"):
                photo = post.photo_path
            else:
                photo = FSInputFile(post.photo_path)  # локальный путь
            caption, full = split_for_caption(post.text)
            msg = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=post.parse_mode,
            )
            # если текст длиннее — досылаем полную версию отдельным сообщением
            if full:
                await self.bot.send_message(chat_id=chat_id, text=full, parse_mode=post.parse_mode)
        else:
            msg = await self.bot.send_message(
                chat_id=chat_id,
                text=post.text,
                parse_mode=post.parse_mode,
            )

        return SendMessageConfig(chat_id=msg.chat.id, message_id=msg.message_id, message=post.text)


async def get_bot_config() -> AsyncIterator[BotConfig]:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN not set in .env")
    bot = Bot(token=token)
    try:
        yield BotConfig(bot)
    finally:
        await bot.session.close()
    