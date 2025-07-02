import discord
from discord.ext.commands import Bot

intents = discord.Intents(members=True,guilds=True)
bot=Bot(command_prefix=None,intents = intents)

import os
basepath=os.path.dirname(os.path.abspath(__file__))
from dotenv import load_dotenv
load_dotenv(basepath+'/../data/.env')

ICP_BIT_SERVER_ID=951810185205280778
DEV_COM_SERVER_ID=1379867449050140752
MOD_ROLE=951811319370248213
STUDENT_ROLE=1068069232841068544
DEV_ROLE=951812307133030430
BIT_DEV_LEAD_ROLE=1317105223566626848
DEV_COM_LEAD_ROLE=1379871219184308254

@bot.event
async def on_ready() -> None:
    print('------')
    bit_server = bot.get_guild(ICP_BIT_SERVER_ID)
    dev_server = bot.get_guild(DEV_COM_SERVER_ID)
    mod=bit_server.get_role(MOD_ROLE)
    student=bit_server.get_role(STUDENT_ROLE)
    dev=bit_server.get_role(DEV_ROLE)

    dev_server_lead=dev_server.get_role(DEV_COM_LEAD_ROLE)
    bit_server_dev_lead=bit_server.get_role(BIT_DEV_LEAD_ROLE)

    devs=[]
    dev_leads=[]
    async for member in dev_server.fetch_members(limit=None):
        devs.append(member.id)
        if dev_server_lead in member.roles: dev_leads.append(member.id)

    for memb in dev.members:
        if bit_server_dev_lead in memb.roles and memb.id not in dev_leads: await memb.remove_roles(bit_server_dev_lead)
        if memb.bot: continue
        if not student in memb.roles: continue
        if mod in memb.roles: continue
        if not memb.id in devs: await memb.remove_roles(dev)

    async for member in bit_server.fetch_members(limit=None):
        if member.id in devs:
            try: await member.add_roles(dev)
            except: pass
        if member.id in dev_leads:
            try: await member.add_roles(bit_server_dev_lead)
            except: pass

    print("Done")
    sys.exit()

bot.run(os.getenv("bot_token"))
