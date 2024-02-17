import yt_dlp
import os
import glob
import asyncio
import discord
# from tqdm import tqdm
from discord.utils import get
from discord.ext.commands import Bot
from functools import partial
import re

class Player:
    def __init__(self, ctx: discord.Interaction, url: str, bot: Bot, loop=False) -> None:
        self.ctx = ctx
        self.url = url
        self.bot = bot
        self.loop = loop
        self._voice_channel = self.set_voice_channel()
        self.vc = get(bot.voice_clients, guild=ctx.guild)
        self.not_stop = False

    @property
    def loop(self):
        return self._loop
    
    @loop.setter
    def loop(self, state):
        self._loop = state

    @property
    def voice_channel(self):
        return self._voice_channel
    
    # 取得使用者目前所在的語音頻道 -> _voice_channel
    def set_voice_channel(self):
        try:
            self._voice_channel = self.ctx.user.voice.channel
            return self._voice_channel
        except:
            # 若使用者不在任何語音頻道，回傳錯誤訊息
            if self.ctx.user.voice is None:
                try: asyncio.get_event_loop().create_task(self.ctx.followup.send("You need to be in a voice channel to play music"))
                except: pass
                raise Exception("User not in voice channel")
            # Other errors
            else: raise
    
    async def start(self):
        await self.ctx.response.defer()
        # Play music
        try:
            # init
            delete_temp("./audio/*")

            # Download
            msg = await self.ctx.followup.send(content="Trying to download", wait=True)
            try:
                # file = download_music(self.url, msg, self.bot)
                file = download_music(self.url)
            except Exception as e:
                await raise_except(e, msg, content="Error: maybe this song can't be downloaded or connection error, You may try again later.")

            # Play
            try:
                self.not_stop = False
                if self.vc and self.vc.is_connected():
                    # 若 bot 已經連線至語音頻道，則加入使用者所在的語音頻道
                    await self.vc.move_to(self.voice_channel)
                else:
                    # 若 bot 尚未連線至語音頻道，則加入使用者所在的語音頻道
                    self.vc = await self.voice_channel.connect()
                # stop music
                self.vc.resume()
                self.vc.stop()
                # delay 0.1s to decrease error chance
                await asyncio.sleep(0.1)
                if self.loop == False:
                    self.vc.play(discord.FFmpegPCMAudio(source=f"{file}"))
                else:
                    self.not_stop = True
                    loop_count_msg = await self.ctx.followup.send(content="Loop Count: 0")
                    self.vc.play(discord.FFmpegPCMAudio(source=f"{file}"), after=lambda e: self.vc.client.loop.create_task(self.repeat_play(file, 1, loop_count_msg)))

            except Exception as e:
                await raise_except(e, msg, content="Audio is downloaded but error on play, please try again.")
            await msg.edit(content=f"Playing: {self.url} \n This bot is updated by killicit.wy")

        # handle unexpected error
        except Exception as e:
            print(e)
            await self.ctx.followup.send(content="Error")

    async def stop(self):
        self.vc.resume()
        self.not_stop = False
        self.loop = False
        self.vc.stop()
            
    async def pause(self):
        self.not_stop = False
        self.vc.pause()
            
    async def resume(self):
        self.not_stop = True
        self.vc.resume()

    async def repeat_play(self, url, count, loop_count_msg):
        while self.not_stop:
            self.vc.play(discord.FFmpegPCMAudio(source=url), after=lambda e: self.vc.client.loop.create_task(self.repeat_play(url, count+1, loop_count_msg)))
            await loop_count_msg.edit(content=f"Loop count: {count}")
        if not self.not_stop:
            if self.vc.is_playing():
                self.vc.pause()

# Raise error after edit the msg in discord to error message
def raise_except(e: Exception, msg: discord.WebhookMessage, content: str):
    print(e)
    asyncio.get_event_loop().create_task(msg.edit(content = content))
    raise e

# Delete Temporary files
def delete_temp(path:str):
    try:
        # Delete audio files
        files = glob.glob(path)
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)

# 下載音樂
# def download_music(url, msg, bot):
def download_music(url):
    # progress_hooks = [lambda d: bot.loop.create_task(progress_hook(d, msg))]
    ydl_opts = {'outtmpl': "./audio/%(id)s.%(ext)s", 
                'format': 'bestaudio', 
                # 'progress_hooks': progress_hooks, 
                'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        filename = ydl.prepare_filename(info)
        return filename

# async def progress_hook(d, msg):
#     # progress = tqdm(total=100)
#     # o=0
#     if d['status'] == 'finished':
#         file_tuple = os.path.split(os.path.abspath(d['filename']))
#         print("Done downloading {}".format(file_tuple[1]))
#     if d['status'] == 'downloading':
#         progress = d['_percent_str']
#         speed = d['_speed_str']
#         eta = d['_eta_str']
#         await msg.edit(content=f"Downloading: {progress} Speed: {speed}")