import discord
from gsbl.stick_bug import StickBug
from PIL import Image
from typing import Optional
import aiohttp
from dotenv import load_dotenv
import os
from discord.ext import commands

intents = discord.Intents(members=False,presences=False,bans=False,messages=True,emojis=False,guilds=True,integrations=False,invites=False,reactions=False,typing=False,voice_states=False,webhooks=False)

bot = commands.Bot(command_prefix='gsbl ', intents=intents)

load_dotenv()

async def get_bytes(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(str(url)) as response:
            image_bytes = await response.read()
    return image_bytes

@bot.event
async def on_ready():
    print('Ready.')

@bot.command()
async def get_stick_bugged_lol(ctx, url:Optional[str]):
    if not url:
        if not ctx.message.attachments:
            return await ctx.send('You didn\'t provide an attachment or image url.')
        else:
            url = ctx.message.attachments[0].url
    img_bytes = await get_bytes(url)
    img_bytes.seek(0)
    img = Image.open(img_bytes,'r')
    await ctx.send('20% done.')
    stick_bug = StickBug(img)
    stick_bug.video_resolution = (1280, 720)
    vid = stick_bug.video
    sb.save_video(f'vid-{ctx.message.id}.mp4')
    file = discord.File(f'vid-{ctx.message.id}.mp4')
    await ctx.send(file=file)

try:
    token = open('token.txt').read().strip()
except:
    token = os.getenv('TOKEN').strip()

bot.run(token)