import os
import asyncio
import telegram
from agent.config import Config

class NotificationManager:
    """
    Manages sending notifications via Telegram.
    """

    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        if not self.bot_token:
            print("Warning: TELEGRAM_BOT_TOKEN is not set. Telegram notifications will not work.")
            self.bot = None
        else:
            self.bot = telegram.Bot(token=self.bot_token)

    async def send_message(self, chat_id: str, message: str):
        """
        Sends a text message to a specified Telegram chat ID.
        """
        if not self.bot:
            print(f"Telegram bot not initialized. Message not sent to {chat_id}: {message}")
            return
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            print(f"Message sent to {chat_id}: {message}")
        except telegram.error.TelegramError as e:
            print(f"Error sending Telegram message to {chat_id}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while sending Telegram message: {e}")

    async def send_photo(self, chat_id: str, photo_path: str, caption: str = None):
        """
        Sends a photo to a specified Telegram chat ID.
        """
        if not self.bot:
            print(f"Telegram bot not initialized. Photo not sent to {chat_id}: {photo_path}")
            return
        if not os.path.exists(photo_path):
            print(f"Photo file not found: {photo_path}")
            return
        try:
            with open(photo_path, "rb") as photo_file:
                await self.bot.send_photo(chat_id=chat_id, photo=photo_file, caption=caption)
            print(f"Photo sent to {chat_id}: {photo_path}")
        except telegram.error.TelegramError as e:
            print(f"Error sending Telegram photo to {chat_id}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while sending Telegram photo: {e}")




