import logging
from secret_manager import SecretManager
from typing import Optional

class Notifier:
    def __init__(self):
        self.secrets = SecretManager()
        self.telegram_token = self.secrets.get_secret('wilsons-raiders/creds', 'TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = self.secrets.get_secret('wilsons-raiders/creds', 'TELEGRAM_CHAT_ID')
        self.matrix_homeserver = self.secrets.get_secret('wilsons-raiders/creds', 'MATRIX_HOMESERVER')
        self.matrix_user = self.secrets.get_secret('wilsons-raiders/creds', 'MATRIX_USER')
        self.matrix_password = self.secrets.get_secret('wilsons-raiders/creds', 'MATRIX_PASSWORD')
        self.matrix_room = self.secrets.get_secret('wilsons-raiders/creds', 'MATRIX_ROOM')

    def send_telegram(self, message: str) -> bool:
        if not self.telegram_token or not self.telegram_chat_id:
            logging.warning('Telegram credentials not set.')
            return False
        try:
            from telegram import Bot
            bot = Bot(token=self.telegram_token)
            bot.send_message(chat_id=self.telegram_chat_id, text=message)
            return True
        except Exception as e:
            logging.error(f'Telegram send error: {e}')
            return False

    def send_matrix(self, message: str) -> bool:
        if not self.matrix_homeserver or not self.matrix_user or not self.matrix_password or not self.matrix_room:
            logging.warning('Matrix credentials not set.')
            return False
        try:
            from nio import AsyncClient
            import asyncio
            async def send():
                client = AsyncClient(self.matrix_homeserver, self.matrix_user)
                await client.login(self.matrix_password)
                await client.room_send(
                    room_id=self.matrix_room,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": message}
                )
                await client.close()
            asyncio.run(send())
            return True
        except Exception as e:
            logging.error(f'Matrix send error: {e}')
            return False
