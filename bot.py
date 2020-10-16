import discord
import asyncio
import inscriptions

at = 'ro79da0d2a0b72b0f0e7207ff97bf45a8e9a7d7990038850'
aub = 'http://bdw-amnnenar.fr/api.php'


class ClientWithBackgroundTask(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the... background.
        self.bg_task = self.loop.create_task(self.background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            channel = next((c for c in self.get_all_channels() if c.name == 'botplace'), None)
            if channel is not None:
                not_checked_in_users = inscriptions.check_next_raid_inscriptions(5, aub, at)
                if len(not_checked_in_users) > 0:
                    message = '@here\nLes connards pas inscrits pour le prochain raid sont:\n'
                    for not_checked_in_user in not_checked_in_users:
                        # not working for now because of discrod limitations :(
                        user = next((m for m in self.users if str.lower(not_checked_in_user) in str.lower(m.name)), None)
                        if user is not None:
                            message += user.mention + '\n'
                        else:
                            message += '- ' + not_checked_in_user + '\n'
                    await channel.send(message)

            await asyncio.sleep(15)


client = ClientWithBackgroundTask()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        for channel in client.get_all_channels():
            if channel.name == 'botplace':
                await channel.send(f"{message.author.mention}")
        await message.delete()

client.run('NzYzNzkwNDEzMjE0NjQ2Mjkz.X381QQ.XTbzcsJ-gqXzYVkU0y1dB-5tdTw')