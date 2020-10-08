import discord
import asyncio


class ClientWithBackgroundTask(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def background_task(self):
        await self.wait_until_ready()
        counter = 0
        while not self.is_closed():
            counter += 1
            for channel in client.get_all_channels():
                if channel.name == 'botplace':
                    await channel.send(counter)
            await asyncio.sleep(60) # task runs every 5 seconds


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
                await channel.send('Hellllllo ' + message.author.name + ' bitch ! <3')
        await message.delete()

client.run('NzYzNzkwNDEzMjE0NjQ2Mjkz.X381QQ.XTbzcsJ-gqXzYVkU0y1dB-5tdTw')