import discord
from discord.ext import commands
import asyncio
import inscriptions
import configparser
import random
import datetime

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
config_api = config['api_server']
config_discord = config['discord']
config_cron = config['cron']

api_url_base = config_api['api_url_base']
api_token = config_api['api_token']
api_days_check_min = config_api['days_check_min']
api_days_check_max = config_api['days_check_max']
discord_token = config_discord['discord_token']
discord_server = config_discord['server']
discord_channel = config_discord['channel']
discord_icon = config_discord['icon']
discord_messages = config_discord['messages'].split('\n')
discord_images = config_discord['images'].split('\n')
cron_hours = int(config_cron['hours'])
cron_minutes = int(config_cron['minutes'])


class BdwBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the... background.
        self.bg_task = self.loop.create_task(self.background_task())

    def find_user(self, nick):
        for guild in self.guilds:
            user = next((m for m in guild.members if str.lower(nick) in str.lower(m.display_name)), None)
            if user is not None:
                return user

        return None

    async def check_signed_in_users_for_next_raid(self, force_next=False, date=None):
        guild = next((g for g in self.guilds if g.name == discord_server), None)
        if guild is not None:
            channel = next((c for c in guild.channels if c.name == discord_channel), None)
            if channel is not None:
                next_raid_inscriptions = inscriptions.check_next_raid_inscriptions(api_url_base,
                                                                                   api_token,
                                                                                   force_next,
                                                                                   api_days_check_min,
                                                                                   api_days_check_max,
                                                                                   date)
                if next_raid_inscriptions is not None:
                    not_checked_in_users = next_raid_inscriptions['not_checked_in_users']
                    if len(not_checked_in_users) > 0:
                        message = ''
                        for not_checked_in_user in not_checked_in_users:
                            user = self.find_user(not_checked_in_user)
                            message += '- ' + not_checked_in_user
    # TODO: Not working on smartphones :(
    #                        if user is not None:
    #                            message += ' (' + user.mention + ')'
                            message += '\n'

                        embed = discord.Embed(title='Raid du ' + next_raid_inscriptions['date'],
                                              description=random.choice(discord_messages), color=0x309bf3)
                        embed.set_thumbnail(url=discord_icon)
                        embed.set_image(url=random.choice(discord_images))
                        embed.add_field(name='Non inscrits:', value=message, inline=False)
                        await channel.send(embed=embed)
                        await channel.send('@here')

    async def background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.datetime.now()
            if now.hour == cron_hours and now.minute == cron_minutes:
                await self.check_signed_in_users_for_next_raid()
            await asyncio.sleep(60)


description = '''Bot inscription BdW'''

intents = discord.Intents.default()
intents.members = True

bot = BdwBot(command_prefix='!', description=description, intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def check_next_raid(context):
    await context.message.delete()
    await bot.check_signed_in_users_for_next_raid(force_next=True)


@bot.command()
async def check_raid(context, date_str):
    if date_str is not None:
        try:
            date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
            await bot.check_signed_in_users_for_next_raid(date=date)
        except ValueError:
            await context.message.author.send("Erreur de commande !checkraid: la date doit être au format dd/mm/yyyy")

    await context.message.delete()


bot.run(discord_token)
