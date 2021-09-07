import re
import time
from vcbot.config import Var
from pyrogram import filters, Client
from datetime import datetime
from vcbot.player import Player
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from vcbot import UB, to_delete, StartTime, group_calls
from vcbot.helpers.utils import get_readable_time, is_ytlive

@UB.on_message(filters.command('ping', '.'))
async def ping_msg_handler(_, m: Message):
    to_be_edited = await m.reply('`Pinging..`')
    start_ms = datetime.now()
    uptime = get_readable_time((time.time() - StartTime))
    end = datetime.now()
    ms = (end - start_ms).microseconds / 1000
    calls_ping = await group_calls.ping
    print(calls_ping)
    await to_be_edited.edit('🏓 **Pong**\n`⟶` MS: {}\n`⟶` PyTgCalls ping: {}\n`⟶` Uptime: {}'.format(ms, calls_ping, uptime))

@UB.on_message(filters.user(Var.SUDO) & filters.command('play', '.'))
async def play_msg_handler(_, m: Message):
    status = await m.reply("Searching!")
    chat_id = m.chat.id
    player = Player(chat_id)
    is_file = False
    is_live = False
    try:
        query = m.text.split(' ', 1)[1]
    except IndexError:
        query = None
    if query:
        if:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', url).group(1)
            is_live = await is_ytlive(link)
        else:
            link = query
            ...
        is_file = False
    if m.reply_to_message:
        if m.reply_to_message.video:
            is_file = True
            med = m.reply_to_message
        # todo
    if is_live:
        return await m.reply("Error: This is a live link.\nTip: use !stream command.")
    await status.edit("Downloading...")
    p = await player.play_or_queue(link, m, is_file, med)
    await status.edit("Streaming...!" if p else "Queued")

@UB.on_message(filters.user(Var.SUDO) & filters.command('leave', '.'))
async def leave_handler(_, m: Message):
    player = Player(m.chat.id)
    await player.leave_vc()
