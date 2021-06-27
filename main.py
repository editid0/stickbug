import discord, aiohttp, os, io, time
from gsbl.stick_bug import StickBug
from PIL import Image
from typing import Optional, Union
from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents(members=False,presences=False,bans=False,messages=True,emojis=False,guilds=True,integrations=False,invites=False,reactions=False,typing=False,voice_states=False,webhooks=False)

bot = commands.Bot(command_prefix='.', intents=intents)

load_dotenv()

async def get_bytes(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(str(url)) as response:
            image_bytes = await response.read()
    return image_bytes

@bot.event
async def on_ready():
    print('Ready.')

@bot.event
async def on_command_error(ctx, error):
    return

@bot.command(aliases=['gsbl'])
@commands.max_concurrency(1, per=commands.cooldowns.BucketType.default, wait=True)# only 1 command at a time, forms a queue of invokes
async def get_stick_bugged_lol(ctx, url:Optional[Union[discord.Member, str]]):
    if not url:
        if not ctx.message.attachments:
            return await ctx.send('You didn\'t provide an attachment or image url.')
        else:
            url = ctx.message.attachments[0].url
    if isinstance(url, discord.Member):
        url = str(url.avatar_url)
    start_time = time.perf_counter()
    img_bytes = await get_bytes(url)
    msg = await ctx.send('Fetched image. (25%)')
    img_bytes = io.BytesIO(img_bytes)
    img_bytes.seek(0)
    img = Image.open(img_bytes,'r')
    await msg.edit(content='Converted image. (50%)')
    stick_bug = StickBug(img)
    stick_bug.video_resolution = (1280, 720)
    await msg.edit(content='Set video resolution. (75%)')
    async with ctx.typing():
        stick_bug.save_video(f'vid-{ctx.message.id}.mp4')
    await msg.edit(content='Processed video. (100%)')
    file = discord.File(f'vid-{ctx.message.id}.mp4')
    end_time = time.perf_counter()
    round_trip = round(float(end_time - start_time), 2)
    await ctx.send(f'Time taken: {round_trip} seconds.',file=file)
    await msg.delete()
    try:
        os.remove(f'vid-{ctx.message.id}.mp4')
    except:
        print('Failed to delete file.')

try:
    token = open('token.txt').read().strip()
except:
    token = os.getenv('TOKEN').strip()

bot.run(token)
