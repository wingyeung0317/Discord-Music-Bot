import yt_dlp
import os
import glob
import asyncio
import discord
from tqdm import tqdm
from discord.utils import get
from discord.ext.commands import Bot
from functools import partial
import re

async def play(ctx: discord.Interaction, url: str, bot:Bot):
    await ctx.response.defer()
    error = 0
    # 取得使用者目前所在的語音頻道
    voice_channel = ctx.user.voice.channel
    if voice_channel is None:
        # 若使用者不在任何語音頻道，回傳錯誤訊息
        await ctx.response.send_message("You need to be in a voice channel to play music")
    # 取得 bot 的音訊連線物件
    vc = get(bot.voice_clients, guild=ctx.guild)
    msg = await ctx.followup.send(content="Trying to download", wait=True)
    try:
        files = glob.glob('./audio/*')
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)
    try:
        # progress_hooks = partial(hook, msg=msg)
        ydl_opts = {'outtmpl': "./audio/%(id)s.%(ext)s", 
                    'format': 'bestaudio', 
                    # 'progress_hooks': [progress_hooks], 
                    'noplaylist': True}
        # 下載音樂
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
        try:
            # 播放音樂
            if vc and vc.is_connected():
                # 若 bot 已經連線至語音頻道，則加入使用者所在的語音頻道
                await vc.move_to(voice_channel)
            else:
                # 若 bot 尚未連線至語音頻道，則加入使用者所在的語音頻道
                vc = await voice_channel.connect()
                
            if vc.is_playing():
                vc.stop()
            vc.play(discord.FFmpegPCMAudio(source=f"{filename}"))
        except Exception as e:
            error = 1
            await msg.edit(content="Video is downloaded but play error, please try try again.")
            print(e)
            raise e
        await msg.edit(content=f"Playing: {url} \n This bot is updated by killicit.wy")
    except Exception as e:
        if error != 1:
            await msg.edit(content="Error: maybe this song can't be downloaded or connection error, You may try again later.")
            print(e)

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