import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
from discord import app_commands
import asyncio
import os
import glob
import config

# 設定 bot 的前綴字元
bot = commands.Bot(command_prefix='m.', intents=discord.Intents.all())

# 透過事件處理註冊 ready 事件，Bot 啟動時會自動觸發
@bot.event
async def on_ready():
    print(f"{bot.user} is now running!")
    try:
        files = glob.glob('./audio/*')
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)
    try:
        syncedCMD = await bot.tree.sync()
        print(f"Synced {len(syncedCMD)} commands")
    except Exception as e:
        print(e)
    await bot.change_presence(
        activity=discord.Activity(name='its code contributor: killicit.wy', type=discord.ActivityType.listening)
    )

# 建立一個 play 指令，用於播放音樂
@bot.tree.command(name='play')
@app_commands.describe(url = "Enter the youtube link here")
async def play(ctx: discord.Interaction, url: str):
    await ctx.response.defer()
    asyncio.sleep(50)
    error = 0
    # 取得使用者目前所在的語音頻道
    voice_channel = ctx.user.voice.channel
    if voice_channel is None:
        # 若使用者不在任何語音頻道，回傳錯誤訊息
        await ctx.response.send_message("You need to be in a voice channel to play music")
    # 取得 bot 的音訊連線物件
    vc = get(bot.voice_clients, guild=ctx.guild)
    # 播放音樂
    if vc and vc.is_connected():
        # 若 bot 已經連線至語音頻道，則加入使用者所在的語音頻道
        await vc.move_to(voice_channel)
    else:
        # 若 bot 尚未連線至語音頻道，則加入使用者所在的語音頻道
        vc = await voice_channel.connect()
        
    if vc.is_playing():
        vc.stop()
    
    try:
        files = glob.glob('./audio/*')
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)
    try:
        ydl_opts = {'outtmpl': './audio/%(title)s-%(id)s.mp4', 'format': 'mp4'}
        # 下載音樂
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        error = 1
    
    vc.play(discord.FFmpegPCMAudio(source=f"{filename}"))
    
    if error == 1 :
        await ctx.followup.send("Error: maybe this sone can't be downloaded or connection error, You may try again later.", ephemeral=True)
    else:
        await ctx.followup.send(f"Playing: {url} \n This bot is updated by killicit.wy")

# 在此處填入你的 bot token
bot.run(config.TOKEN)