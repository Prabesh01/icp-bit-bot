import discord
from discord.ext.commands import Bot

intents = discord.Intents(members=True,guilds=True)
bot=Bot(command_prefix=None,intents = intents)

import os, json
basepath=os.path.dirname(os.path.abspath(__file__))
from dotenv import load_dotenv
load_dotenv(basepath+'/../data/.env')
attendance_file=basepath+'/../data/attendance.json'

attendee=[]
with open(attendance_file, 'r') as f: attendance_data = json.load(f)
for date,users in attendance_data.items():
    for user in users:
        if not user in attendee: attendee.append(user)

ICP_BIT_SERVER_ID=951810185205280778
MOD_ROLE=951811319370248213
STUDENT_ROLE=1068069232841068544
HOH_ROLE=1286851007812472915

@bot.event
async def on_ready() -> None:
    print('------')
    bit_server = bot.get_guild(ICP_BIT_SERVER_ID)
    mod=bit_server.get_role(MOD_ROLE)
    student=bit_server.get_role(STUDENT_ROLE)
    hoh=bit_server.get_role(HOH_ROLE)

    for memb in hoh.members:
        if memb.bot: continue
        if not student in memb.roles: continue
        if mod in memb.roles: continue
        if not str(memb.id) in attendee: await memb.remove_roles(hoh)
    print("Done")
    sys.exit()

bot.run(os.getenv("bot_token"))
