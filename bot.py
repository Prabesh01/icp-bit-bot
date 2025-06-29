import discord
from discord.ext.commands import Bot
from discord import app_commands
import os, json
from datetime import datetime
import traceback
import pytz
import requests
import re
from filelock import FileLock
tz_NP = pytz.timezone('Asia/Kathmandu')


basepath=os.path.dirname(os.path.abspath(__file__))
from dotenv import load_dotenv
load_dotenv(basepath+'/data/.env')
user_file=basepath+'/data/user.json'
attendance_file=basepath+'/data/attendance.json'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot=Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

ICP_BIT_SERVER_ID=951810185205280778
GRADUATE_ROLE_ID=1388086092636491848
STUDENT_ROLE=1068069232841068544

def read_json(fname):
    file=basepath+'/data/'+fname+'.json'
    with FileLock(file + '.lock'):
        with open(file, 'r') as f:
            return json.load(f)


def write_json(fname, data):
    file=basepath+'/data/'+fname+'.json'
    with FileLock(file + '.lock'):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)


@bot.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Role.py - Error', colour=0xe74c3c)
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.now()
    bot.AppInfo = await bot.application_info()
    await bot.AppInfo.owner.send(embed=embed)


@bot.event
async def on_ready() -> None:
    global STUDENT_ROLE
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over ICP-BIT server"))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.tree.sync()
    bit_server = bot.get_guild(ICP_BIT_SERVER_ID)
    STUDENT_ROLE=bit_server.get_role(STUDENT_ROLE)


@bot.tree.command(name="enroll", description="Hour of Hack Registration")
@app_commands.describe(london_met_id="Your London Met ID", name="Your Name")
async def enroll(interaction: discord.Interaction, london_met_id: int, name: str):
    user_data=read_json('user')
    data = {
        "username": interaction.user.name,
        "lid": london_met_id,
        "name": name,
    }
    if str(interaction.user.id) in user_data:
        txt="Enrollment Updated Sucessfully!"
    else:
        txt="Enrolled Sucessfully!"
    user_data[str(interaction.user.id)]=data
    write_json('user', user_data)
    await interaction.response.send_message(txt, ephemeral=True)


@bot.event
async def on_member_update(before, after):
    after_roles=[r.id for r in after.roles]
    before_roles=[r.id for r in before.roles]
    if GRADUATE_ROLE_ID in after_roles and not GRADUATE_ROLE_ID in before_roles:
         await after.remove_roles(STUDENT_ROLE)
    elif not GRADUATE_ROLE_ID in after_roles and GRADUATE_ROLE_ID in before_roles:
         await after.add_roles(STUDENT_ROLE)


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id==1289057002311385118:
        now=datetime.now(tz_NP)
        if now.weekday() != 0 or now.hour != 15:
            await member.move_to(None)
            return

        attendance=read_json('attendance')
        date_now=now.strftime('%Y-%m-%d')
        if date_now not in attendance:
            attendance[date_now]=[]
        if not str(member.id) in attendance[date_now]:
            attendance[date_now].append(str(member.id))
            write_json('attendance', attendance)
            try:
                dm_channel = await member.create_dm()
                await dm_channel.send("You are marked as present in today's session.")
            except: pass
        await member.move_to(None)

        user_data=read_json('user')
        mem_id=str(member.id)
        if not mem_id in user_data: user_data[mem_id]={"username": member.name}
        else: user_data[mem_id]["username"]=member.name
        write_json('user', user_data)

bot.run(os.getenv("bot_token"))
