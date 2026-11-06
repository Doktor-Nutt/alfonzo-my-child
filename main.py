import discord
import io
import os
from discord.ext import commands
from dotenv import load_dotenv
from locket import makesweet

load_dotenv()

YOUR_BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def test(ctx, member: discord.Member = None):
    sender_avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    target_avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embedSender = discord.Embed(title=f"{ctx.author.name}'s Avatar", color=discord.Color.green())
    embed.set_image(url=target_avatar_url)
    embedSender.set_image(url=sender_avatar_url)
    await ctx.send(embed=embed)
    await ctx.send(embed=embedSender)


@bot.command()
async def locket(ctx, member: discord.Member):
    async with ctx.typing():
        # display_avatar falls back to the default avatar; force a static PNG for makesweet
        sender_avatar = await ctx.author.display_avatar.replace(format="png", size=512).read()
        target_avatar = await member.display_avatar.replace(format="png", size=512).read()
        try:
            gif = await makesweet("heart-locket.zip", [sender_avatar, target_avatar])
        except Exception as e:
            await ctx.send(f"Couldn't make the locket: {e}")
            return
    await ctx.send(file=discord.File(io.BytesIO(gif), "locket.gif"))


@locket.error
async def locket_error(ctx, error):
    if isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
        await ctx.send("Usage: `!locket @user`")
    else:
        raise error


bot.run(YOUR_BOT_TOKEN)