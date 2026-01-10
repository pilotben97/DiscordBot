import os
import discord
from discord import Embed
from discord.ext import commands, tasks
import requests
import time
import asyncio
import aiohttp
import csv
from dotenv import load_dotenv
from discord.ext import commands, tasks

from datetime import datetime, timezone, timedelta

from Classes.Aircraft import Aircraft # My class
from Classes.ADSBData import ADSBData # My class
from HelperFiles.import_uscg import process_uscg_aircraft_csv
from HelperFiles.activity_log_handler import log_activity, load_aircraft_adsb_from_activity


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ADSB_API_KEY = os.getenv("ADSB_API_KEY")

headers = {
    "X-RapidAPI-Key": ADSB_API_KEY,
    "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
}

uscg_file = './Data/USCG Air Asset Bases - Assets.csv'
fallback_file = './Data/fallbackFile.csv'

ALLOWED_CHANNEL_ID = {1368666897301635192, 1368746401026015252}
RAZOR_SERVER_BOT_CH_ID = 1368666897301635192

#process_uscg_aircraft_csv(fallback_file)
uscg_aircraft_list = process_uscg_aircraft_csv(uscg_file)
uscg_hex_string = ",".join(ac.hexCode for ac in uscg_aircraft_list)

#create Discord bot
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)



#print(f"Loaded {len(uscg_aircraft_list)} aircraft.")
#print(f"HEX string: {uscg_hex_string}")



async def get_fleet_moving(hex_code_list, aircraft_list, notify, channel):
    url = f"https://adsbexchange-com1.p.rapidapi.com/v2/icao/{hex_code_list}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        aircraft = data.get("ac", [])

        if not aircraft:
            if(notify):
                await channel.send("❌ No listed aircraft are currently moving.")
            return
        
        all_fields = set()
        moving = []
        for ac in aircraft:
            all_fields.update(ac.keys())

            hexcode = ac.get("hex", "").upper()
            on_ground = ac.get("gnd", True)  # Default to True if missing
            speed = ac.get("gs", 0.0) # Get groundspeed, default to 0

            #For testing to see what is causing speed check error
            #print(speed,df[df['Hex Code'] == hexcode].iloc[0]['Callsign'])

            
            match_info = next((ac for ac in aircraft_list if ac.hexCode == hexcode), None)

            # Filter out only keys that are defined in ADSBData
            allowed_fields = ADSBData().__dict__.keys()
            filtered_ac = {k: v for k, v in ac.items() if k in allowed_fields}
            adsb_obj = ADSBData(**filtered_ac)

            if not on_ground or speed > 5:
                if match_info:
                    match_info.lastSeenDate = datetime.now(timezone.utc) # update last seen time to now
                moving.append((match_info, adsb_obj))  # use ADSBData, not raw dict

            #print(f"\n\n{match_info}")

        if moving:
            #print(moving[0])
            await log_activity(moving)

            clickable_url = "https://globe.adsbexchange.com/?icao="
            output_lines = ["✅ Aircraft currently moving:"]

            for aircraft, adsb in moving:
                cs_abbr = aircraft.callsignAbbr or "Unknown"
                cs_full = aircraft.callsign
                tail = aircraft.tailNumber
                icao = aircraft.icao or "N/A"
                airport = aircraft.lastAirport or "ZZZZ"
                squawk = adsb.squawk or "----"
                operator = aircraft.operator or "Unknown"

                line = f"Callsign (Abr): {cs_abbr}"
                
                # Append if different
                if cs_full and cs_full != cs_abbr:
                    line += f" | Callsign: {cs_full}"
                if tail and tail != cs_abbr:
                    line += f" | Tail: {tail}"

                line += f" | ICAO: {icao} | Last Airport: {airport} | Squawk: {squawk} | Operator: {operator}"
                output_lines.append(line)

            # Send to console or Discord (e.g., inside a code block)
            formatted_output = "\n".join(output_lines)

            # Append all hex codes as comma-separated values
            clickable_url += ",".join([aircraft.hexCode.upper() for aircraft, _ in moving])

            embed = discord.Embed(
                title="🛫 View Active Aircraft on ADS-B Exchange",
                description=f"[Click here to view on ADS-B]({clickable_url})",
                color=discord.Color.green()
            )
            try:
                await channel.send(content=formatted_output, embed=embed)
            except discord.HTTPException as e:
                await channel.send("⚠️ Unable to send message due to formatting or size limits.")
                print(f"Discord HTTPException: {e}")
            except discord.Forbidden:
                print("Bot doesn't have permission to send messages to this channel.")
            except discord.NotFound:
                print("Channel not found.")
            except Exception as e:
                print(f"Unexpected error when sending message: {e}")

                
            return moving

########################################################################### Housekeeping Tasks (Startup, periodic function runs, remove old messages, etc) ###########################################################################

############ On Startup ############
@bot.event
async def on_ready(): #start
    channel = bot.get_channel(RAZOR_SERVER_BOT_CH_ID)
    if channel:
        await channel.send(f'Logged in as {bot.user.name}')

    channel = bot.get_channel(RAZOR_SERVER_BOT_CH_ID)
    if channel is None:
        print(f"❌ Could not find channel ID: {RAZOR_SERVER_BOT_CH_ID}")
        return
    
    await get_fleet_moving(uscg_hex_string, uscg_aircraft_list, True, channel)
    await start_periodic_task(15)

async def start_periodic_task(every_x_minutes: int):
    await bot.wait_until_ready()

    while not bot.is_closed():
        now = datetime.now(timezone.utc)
        minute = now.minute
        remainder = minute % every_x_minutes
        channel = bot.get_channel(RAZOR_SERVER_BOT_CH_ID)
        if channel:
            if remainder == 0:
                delay_seconds = 0
            else:
                next_minute = minute + (every_x_minutes - remainder)
                next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_minute)
                delay_seconds = (next_run - now).total_seconds()

            print(f"⏳ Waiting {int(delay_seconds/60)} m and {int(delay_seconds%60)} s seconds for first run...")
            await asyncio.sleep(delay_seconds)

            while not bot.is_closed():
                #print(f"⏰ Running task at {datetime.now(timezone.utc)}")
                await get_fleet_moving(uscg_hex_string, uscg_aircraft_list, True, channel)
                await asyncio.sleep(every_x_minutes * 60)

        if channel is None:
            print(f"❌ Could not find channel ID: {RAZOR_SERVER_BOT_CH_ID}")
            return

############ Remove old messages (All except "currently moving") made by this bot ############
@bot.command(name="zxclear")
@commands.has_permissions(manage_messages=True)
async def zxclear(ctx):
    bot_user = ctx.bot.user
    channel = ctx.channel

    # Step 1: Filter messages authored by the bot but NOT containing "currently moving"
    def is_deletable(m):
        return m.author == bot_user and "currently moving" not in m.content.lower()

    # Step 2: Fetch recent messages (you can increase the limit if needed)
    messages = [m async for m in channel.history(limit=100) if is_deletable(m)]

    if not messages:
        await ctx.send("✅ No bot messages found that need to be deleted.")
        return

    # Step 3: Ask for confirmation
    await ctx.send(f"⚠️ This will delete {len(messages)} of my messages in this channel (excluding 'currently moving'). React with ✅ to confirm.")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.channel == ctx.channel

    confirm_msg = await ctx.send("Are you sure? React with ✅ within 30 seconds to confirm.")
    await confirm_msg.add_reaction("✅")

    try:
        await ctx.bot.wait_for("reaction_add", timeout=30.0, check=check)
    except:
        await ctx.send("⏳ No confirmation received. Aborting.")
        return

    # Step 4: Delete messages
    for msg in messages:
        try:
            await msg.delete()
            time.sleep(0.5)
        except discord.NotFound:
            continue

    await ctx.send(f"🧹 Deleted {len(messages)} messages.")



    
bot.run(DISCORD_TOKEN)