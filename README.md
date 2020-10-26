# BDW Bot

a quick made bot that will check inscriptions for the next raid on a eqdkp-plus website and post messages on discord.
For now, one instance of the bot can only be linked to one discord server, due to cron(...ish) functionnality.

## Functionnalities
- Every day at a fixed hour, check inscriptions on the website. If the raid is in a fixed period, send a discord message on a fixed channel from a fixed discord server.
- By typing `!check_next_raid` in a discord channel, check inscriptions for the next raid on the website (without checking when that raid will be) and send a discord message on a fixed channel from a fixed discord server.
- By typing `!check_raid dd/mm/yyyy` in a discord channel, check inscriptions for the raid at the given date on the website and send a discord message on a fixed channel from a fixed discord server.
- The message will be an embeded one, containing the list of not checked-in users. If a discord user is found containing the character name, he will be tagged.

## Configuration
All the needed constants must be in a `config.ini` file. An example is provided.
### [api_server]
- `api_token`: api token from the EQDKP-Plus website (read-only api token is sufficent)
- `api_url_base`: your website url (http://www.yourwebsite.com)
- `days_check_min` & `days_check_max`: Period when the next raid must be checked when cron is called
- `site_inscription_url_pattern`: url for the inscription site with a placeholder for the raid id (http://www.yourwebsite.com/index.php/Calendar/Calendarevent/{}.html?)
### [discord]
- `discord_token`: the discord bot token (check https://discordpy.readthedocs.io/en/latest/discord.html for more information)
- `server`: name of the fixed discord server
- `channel`: name of the fixed discord channel
- `icon`: url to the icon for the embeded message
- `messages`: messages for the embeded message, separated by a carriage return. One will be selected randomly
- `images`: urls to images for the embeded message, separated by a carriage return. One will be selected randomly
### [cron]
- `hours`: hours of the time to daily check the inscriptions
- `minutes`:  minutes of the time to daily check the inscriptions