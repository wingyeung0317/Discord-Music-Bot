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

# User Triggered Player
async def player(ctx, url, bot, loop=False):
    await ctx.response.defer()
    # Play music
    try:
        # init
        voice_channel = get_voice_channel(ctx)
        vc = get_voice_client(bot, ctx)
        delete_temp()

        # Download
        msg = await ctx.followup.send(content="Trying to download", wait=True)
        try:
            file = download_music(url)
        except Exception as e:
            await raise_except(e, msg, content="Error: maybe this song can't be downloaded or connection error, You may try again later.")

        # Play
        try:
            await play_music(vc, voice_channel, file, loop)
        except Exception as e:
            await raise_except(e, msg, content="Audio is downloaded but error on play, please try again.")
        await msg.edit(content=f"Playing: {url} \n This bot is updated by killicit.wy")
    # handle unexpected error
    except Exception as e:
        print(e)
        await ctx.followup.send(content="Error")

# 取得使用者目前所在的語音頻道 -> voice_channel
def get_voice_channel(ctx: discord.Interaction):
    try:
        voice_channel = ctx.user.voice.channel
        return voice_channel
    except:
        # 若使用者不在任何語音頻道，回傳錯誤訊息
        if ctx.user.voice is None:
            try: asyncio.get_event_loop().create_task(ctx.followup.send("You need to be in a voice channel to play music"))
            except: pass
            raise Exception("User not in voice channel")
        # Other errors
        else:
            raise

# 取得 bot 的音訊連線物件 -> vc
def get_voice_client(bot:Bot, ctx: discord.Interaction):
    vc = get(bot.voice_clients, guild=ctx.guild)
    return vc

# Delete Temporary files
def delete_temp():
    try:
        # Delete audio files
        files = glob.glob('./audio/*')
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)

# 下載音樂
def download_music(url):
    # progress_hooks = partial(hook, msg=msg)
    ydl_opts = {'outtmpl': "./audio/%(id)s.%(ext)s", 
                'format': 'bestaudio', 
                # 'progress_hooks': [progress_hooks], 
                'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        filename = ydl.prepare_filename(info)
        return filename

# 播放音樂
async def play_music(vc, voice_channel, file, loop):
    if vc and vc.is_connected():
        # 若 bot 已經連線至語音頻道，則加入使用者所在的語音頻道
        await vc.move_to(voice_channel)
    else:
        # 若 bot 尚未連線至語音頻道，則加入使用者所在的語音頻道
        vc = await voice_channel.connect()
    # stop music if playing
    if vc.is_playing():
        vc.stop()
        # delay 0.1s to decrease error chance
        await asyncio.sleep(0.1)
    if loop == False:
        vc.play(discord.FFmpegPCMAudio(source=f"{file}"))
    else:
        repeat_play(voice_channel.guild, vc, file)

def repeat_play(guild, vc, file):
    vc.play(discord.FFmpegPCMAudio(source=f"{file}"), after=lambda e: repeat_play(guild, vc, file))

# Print error to client and raise Exception again
async def raise_except(e, msg, content):
    print(e)
    await msg.edit(content=content)
    raise e

# def hook(d, msg):
#     # progress = tqdm(total=100)
#     # o=0
#     if d['status'] == 'finished':
#         file_tuple = os.path.split(os.path.abspath(d['filename']))
#         print("Done downloading {}".format(file_tuple[1]))
#     if d['status'] == 'downloading':
#         p = d['_percent_str']
#         p = re.findall(r'\d{1,3}\.\d', p)[0]
#         p = float(p)
#         asyncio.get_event_loop().create_task(msg.edit(content="Downloading: `{} `%".format(p)))