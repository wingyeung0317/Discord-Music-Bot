import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
from discord import app_commands
import asyncio
import os
import glob
import config
import functions

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
    await functions.play(ctx, url, bot)
    

# 在此處填入你的 bot token
bot.run(config.TOKEN)