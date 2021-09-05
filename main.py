from pyrogram import Client as Bot
from callsmusic import run
from pyrogram import idle
import logging
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_NAME
import time
import asyncio

loop = asyncio.get_event_loop()


bot = Bot(
    ":memory:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers")
)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger('__name__') 


print("Lets Roll Boiss$$$")

bot.start()
run()
idle()
