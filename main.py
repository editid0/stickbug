import discord, aiohttp, os, io, time
from gsbl.stick_bug import StickBug
from PIL import Image
from typing import Optional, Union
from dotenv import load_dotenv
from discord.ext import commands
from async_lru import alru_cache as cache

max_cache_size = 64

intents = discord.Intents(members=False,presences=False,bans=False,messages=True,emojis=False,guilds=True,integrations=False,invites=False,reactions=False,typing=False,voice_states=False,webhooks=False)

bot = commands.Bot(command_prefix='.', intents=intents)

bot.url1 = None
bot.ctx = None

load_dotenv()

async def get_bytes(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(str(url)) as response:
            image_bytes = await response.read()
    return image_bytes

@cache(maxsize=max_cache_size)
async def do_stickbug(u_id, url):
    img_bytes = await get_bytes(url)
    img_bytes = io.BytesIO(img_bytes)
    img_bytes.seek(0)
    img = Image.open(img_bytes,'r')
    stick_bug = StickBug(img)
    stick_bug.video_resolution = (1280, 720)#Change to 1920, 1080 if you want 1080p, will take longer
    stick_bug.save_video(f'vid-{u_id}.mp4')
    m = open(f'vid-{u_id}.mp4', 'rb')
    return discord.File(fp = m, filename='stickbug.mp4')
    # return f'vid-{ctx.message.id}.mp4'

@bot.event
async def on_ready():
    print('Ready.')

@bot.event
async def on_command_error(ctx, error):
    raise error
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
    async with ctx.typing():
        i = await do_stickbug(ctx.author.id, url)
        await ctx.send(len(i.fp))
        # i.seek(0)
        # f = discord.File(fp=i)
        await ctx.send(file=i)
        await ctx.send(do_stickbug.cache_info())
        os.remove(f'vid-{ctx.author.id}.mp4')
    # await msg.edit(content='Converted image. (50%)')
    # stick_bug = StickBug(img)
    # stick_bug.video_resolution = (1280, 720)
    # await msg.edit(content='Set video resolution. (75%)')
    # async with ctx.typing():
    #     stick_bug.save_video(f'vid-{ctx.message.id}.mp4')
    # await msg.edit(content='Processed video. (100%)')
    # file = discord.File(f'vid-{ctx.message.id}.mp4')
    # end_time = time.perf_counter()
    # round_trip = round(float(end_time - start_time), 2)
    # await ctx.send(f'Time taken: {round_trip} seconds.',file=file)
    # await msg.delete()
    # try:
    #     os.remove(f'vid-{ctx.message.id}.mp4')
    # except:
    #     print('Failed to delete file.')

try:
    token = open('token.txt').read().strip()
except:
    token = os.getenv('TOKEN').strip()

bot.run(token)
