import os
import time
import signal
import asyncio
import subprocess
from vcbot.config import Var
from pyrogram import Client
from pytgcalls import StreamType
from pyrogram.types import Message
from pytgcalls.types import Update
from pytgcalls.pytgcalls import PyTgCalls
from vcbot import UB, queues, to_delete, group_calls, ff_sempai
from vcbot.helpers.utils import transcode, tg_download, yt_download
from pytgcalls.types.input_stream import (
    VideoParameters,
    AudioParameters,
    InputAudioStream,
    InputVideoStream,
    InputStream
)
#
# base from https://github.com/TeamUltroid/Ultroid/blob/dev/vcbot/__init__.py
# Thanks to TeamUltroid :)

ms = {}
now_playing = []

@group_calls.on_stream_end()
async def on_stream_end(client: PyTgCalls, update: Update):
    cms = time.time()
    if k:= ms.get(update.chat_id):
        if cms-k < 10:
            return
    ms[update.chat_id] = cms
    anything = queues.get(update.chat_id, False)
    player = Player(update.chat_id)
    if anything:
        next = queues.get(update.chat_id)
        video , is_path, user = next
        suc, err = await player.play_file(video, is_path, change=True)
        if not suc:
            await UB.send_message(update.chat_id, str(err))
        else:
            await UB.send_message(update.chat_id, "Now playing: {}\nRequested by: {}".format(video, user.mention(style="md")))
        return True
    else:
        await player.leave_vc()


class Player:
    def __init__(self, chat_id):
        self._current_chat = chat_id

    async def play_file(self, file, is_path=False, change=False):
        if not is_path:
            file, _ = await yt_download(file)
        else:
            file = await tg_download(file)
        audio, video = await transcode(file)
        self.add_to_trash(audio)
        self.add_to_trash(video)
        while not os.path.exists(video) and not os.path.exists(audio):
            await asyncio.sleep(0.1)
        if change:
            await self.change_source(video, audio)
        else:
            await self.join_play(video, audio)
        return True, None

    async def join_play(self, video, audio, width=Var.WIDTH, height=Var.HEIGHT, fps=Var.FPS, bitrate=Var.BITRATE):
        await group_calls.join_group_call(
            self._current_chat,
            InputStream(
              InputAudioStream(
                audio,
                AudioParameters(
                    bitrate=bitrate,
                ),
            ),
            InputVideoStream(
                video,
                VideoParameters(
                    width=width,
                    height=height,
                    frame_rate=fps,
                ),
            ),
            ),
            stream_type=StreamType().pulse_stream
        )
        now_playing.append(self._current_chat)

    async def change_source(self, video, audio, width=Var.WIDTH, height=Var.HEIGHT, fps=Var.FPS, bitrate=Var.BITRATE):
        await group_calls.change_stream(
            self._current_chat,
            InputStream(
              InputAudioStream(
                audio,
                AudioParameters(
                    bitrate=bitrate,
                ),
            ),
            InputVideoStream(
                video,
                VideoParameters(
                    width=width,
                    height=height,
                    frame_rate=fps,
                ),
            ),
            ),
            stream_type=StreamType().pulse_stream
        )
        if not self._current_chat in now_playing:
            now_playing.append(self._current_chat)
    
    async def play_or_queue(self, vid, m: Message, is_path=False, change=False):
        anything = queues.get(self._current_chat, False)
        if not self._current_chat in now_playing:
            suc, err = await self.play_file(vid, is_path)
            if not suc:
                await UB.send_message(self._current_chat, str(err))
            return True
        else:
            data = [vid, is_path, m.from_user]
            pos = queues.add(self._current_chat, data)
            await m.reply(f"Added to queue #{pos}")
            return False
            
    async def leave_vc(self):
        await group_calls.leave_group_call(self._current_chat)
        pid = await self.terminate_ffmpeg()
        status = f"Terminated FFmpeg with PID `{pid}`" if \
            pid else ""
        status += "\nSuccessfully left vc!"
        now_playing.remove(self._current_chat)
        self.clear_played()
        await UB.send_message(self._current_chat, status)

    async def terminate_ffmpeg(self):
        if x:= ff_sempai.get(self._current_chat):
            try:
                x.terminate()
            except (RuntimeError or RuntimeWarning):
                await x.terminate()
            return x.pid
    
    def clear_played(self):
        print("Deleting")
        files = to_delete.get(self._current_chat, [])
        for i in files:
            try:
                os.remove(i)
                print("Removed {}".format(i))
            except BaseException:
                print("Couldn't remove {}".format(i))
            files.remove(i)
    
    def add_to_trash(self, file):
        if x:= to_delete.get(self._current_chat):
            try:
                if x:
                    to_delete[self._current_chat].append(file)
                else:
                    to_delete[self._current_chat] = [file]
            except (IndexError or AttributeError):
                pass
