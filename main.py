import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import json


with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    TOKEN = config['token']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

last_activity = {}

'''
====================================================================================
MUSIC CODE START --------------------------------------------------------------------
====================================================================================
'''

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'executable': r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queue = []


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.image = data.get("thumbnails")[0]["url"]

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        # print(data)

        if 'entries' in data:
            data = data['entries'][0]
        # print(data["thumbnails"][0]["url"])
        # print(data["duration"])
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@bot.event
async def on_ready():
    print(f'Logado como {bot.user.name}')
    bot.loop.create_task(check_inactive())


@bot.command()
async def onlinetest(ctx):
    em = discord.Embed(title='Caça Esportiva (LTDA)', description=' ', color=0x41BFBF)
    em.add_field(name='Online test', value='Coe coe.')
    await ctx.send(embed=em)


class QueueEntry:
    def __init__(self, player, author):
        self.player = player
        self.author = author


@bot.command(name='play', aliases=['p'])
async def play(ctx, url):
    if not ctx.author.voice:
        return await ctx.send("Você precisa estar em um canal de voz para usar este comando.")

    channel = ctx.author.voice.channel
    player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)

    if ctx.voice_client and ctx.voice_client.is_playing():
        queue.append(QueueEntry(player, ctx.author))
        await ctx.send(f'**{player.title}** foi adicionada à fila por {ctx.author.display_name}.')
    else:
        sessionChannel = await channel.connect()
        sessionChannel.guild.voice_client.play(player, after=lambda e: print(f'Player Error: {e}')
                                               if e else None)


@bot.command(name='stop', aliases=['Stop'])
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send('O bot nao está em uma chamada de voz.')


@bot.command(name='pause', aliases=['Pause'])
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
    else:
        await ctx.send('Nenhuma música está sendo reproduzida no momento.')


@bot.command(name='resume', aliases=['Resume', 'r'])
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
    else:
        await ctx.send('A múscia não está pausada.')


@bot.command(name='skip', aliases=['Skip', 's', 'S'])
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()

        if queue:
            next_song = queue.pop(0)
            ctx.voice_client.play(next_song, after=lambda e: print(f'Player error: {e}' if e else None))
            await ctx.send(f'**{next_song.title}** está tocando agora.')
        else:
            await ctx.send('Fila de reprodução vazia. Use "!play" ou "!p" para adicionar mais múscias.')
    else:
        await ctx.send('Nenhuma múscia está sendo reproduzina no momento.')


@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    if queue:
        embed = discord.Embed(title=f'Fila de Reprodução: {len(queue)} musica(s)', color=0x41BFBF)
        for index, queue_entry in enumerate(queue):
            embed.add_field(
                name=f"{index + 1}. {queue_entry.player.title}",
                value=f"Requisitado por: {queue_entry.author.display_name}",
                inline=False
            )
        await ctx.send(embed=embed)
    else:
        await ctx.send('A fila de reprodução está vazia.')


async def check_inactive():
    while True:
        for channel_id, last_time in last_activity.items():
            if asyncio.get_event_loop().time() - last_time > 120:
                channel = bot.get_channel(channel_id)
                if channel and channel.guild.voice_client:
                    await channel.guild.voice_client.disconnect()
                    del last_activity[channel_id]
        await asyncio.sleep(60)


'''
====================================================================================
MUSIC CODE END ----------------------------------------------------------------------
====================================================================================
'''


@bot.command(name='info', aliases=['i'])
async def info_embed(ctx):
    embed1 = discord.Embed(title='Caça Esportiva (LDTA)', description='Sobre o Grupo',
                                 color=0x41BFBF)

    embed1.set_image(url=r'https://encrypted-tbn0.gstatic.com/'
                         r'images?q=tbn:ANd9GcSYlHi_VIJ4xV--8CFg'
                         r'mKAuhlWnfndBnk5si4X6kEn6ZdW2trmduM9QE'
                         r'ArUv6Hra8Isiss&usqp=CAU')

    embed1.add_field(name='Status', value='Bot em desenvolvimento', inline=False)

    # BARROKA
    embed2 = discord.Embed(title='Membros Oficiais 1/9', color=0xffffff)
    embed2.add_field(name='Arthur Rossiter', value='Barroka mcz (Forjador)', inline=False)

    # PERES
    embed3 = discord.Embed(title='Membros Oficiais 2/9', color=0x000000)
    embed3.add_field(name='FPeres', value='apenas FPeres (Análise)', inline=False)
    embed3.set_image(url='')

    # CABRAL
    embed4 = discord.Embed(title='Membros Oficiais 3/9', color=0xffffff)
    embed4.add_field(name='Vitor Cabral', value='o Estupra penis (Esculápio)', inline=False)
    embed4.set_image(url='')

    # VINICIUS
    embed5 = discord.Embed(title='Membros Oficiais 4/9', color=0x000000)
    embed5.add_field(name='Gabriel Vinicius', value='o Inimigo da moda (Concierge)', inline=False)
    embed5.set_image(url=r'https://i.imgur.com/LLngs90.jpg?1')

    # PEDRINHO
    embed6 = discord.Embed(title='Membros Oficiais 5/9', color=0xffffff)
    embed6.add_field(name='Pedro Lyra', value='o KASSANI99A (Emissário)', inline=False)
    embed6.set_image(url='')

    # JH
    embed7 = discord.Embed(title='Membros Oficiais 6/9', color=0x000000)
    embed7.add_field(name='Joao Henrique', value='jh rebola neles (Flanelinha)', inline=False)
    embed7.set_image(url=r'https://i.imgur.com/USfhl5K.jpg')

    # KHAZENN
    embed8 = discord.Embed(title='Membros Oficiais 7/9', color=0xffffff)
    embed8.add_field(name='Victor Lôbo', value='Khazenn (Sentinela)', inline=False)
    embed8.set_image(url='')

    # ACIOLI
    embed9 = discord.Embed(title='Membros Oficiais 8/9', color=0x000000)
    embed9.add_field(name='Gabriel Acioli', value='acioli o homi (Contrabandista)', inline=False)
    embed9.set_image(url='')

    # EU MESMO
    embed10 = discord.Embed(title='Membros Oficiais 9/9', color=0x000000)
    embed10.add_field(name='Gabriel Leão', value='Somende Dela (Conservador)', inline=False)
    embed10.set_image(url='')

    pages = [
        embed1,
        embed2,
        embed3,
        embed4,
        embed5,
        embed6,
        embed7,
        embed8,
        embed9,
        embed10
    ]

    current_page = 0
    message = await ctx.send(embed=pages[current_page])

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=240.0, check=check)

            if str(reaction.emoji) == "➡️":
                current_page = (current_page + 1) % len(pages)
            elif str(reaction.emoji) == "⬅️":
                current_page = (current_page - 1) % len(pages)

            await message.edit(embed=pages[current_page])
            await message.remove_reaction(reaction, user)

        except TimeoutError:
            break

bot.run(TOKEN)
