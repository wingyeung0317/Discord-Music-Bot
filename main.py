import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
from discord import app_commands
import asyncio
import os
import glob
import config
from functions import *

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

# 建立一個 play 指令，以播放音樂
@bot.tree.command(name='play')
@app_commands.describe(url = "Enter the youtube link here")
async def play(ctx: discord.Interaction, url: str):
    global player
    player = Player(ctx, url, bot, False)
    await player.start()

# 建立一個 loop 指令，以loop音樂
@bot.tree.command(name='loop')
@app_commands.describe(url = "Enter the youtube link here")
async def loop(ctx: discord.Interaction, url: str):
    global player
    player = Player(ctx, url, bot, True)
    await player.start()

@bot.tree.command(name='pause')
async def pause(ctx: discord.Interaction):
    await player.pause()
    await ctx.response.send_message("paused")
    
@bot.tree.command(name='resume')
async def resume(ctx: discord.Interaction):
    await player.resume()
    await ctx.response.send_message("resumed")
    
@bot.tree.command(name='stop')
async def stop(ctx: discord.Interaction):
    await player.stop()
    await ctx.response.send_message("stopped")

# 在 ./config.py 填入你的 bot token
# TOKEN = "Your Token"
bot.run(config.TOKEN)