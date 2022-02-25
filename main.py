from replit import db
import discord
import pytz
from discord.ext import commands, tasks
from discord.utils import get
from online import online
from datetime import datetime
import threading
import asyncio
import random
import os
from discord.ext.commands import CommandNotFound

def get_prefix(client, message):
  return db[str(message.guild.id)]

intents = discord.Intents.all()
intents.members = True
intents.reactions = True
client = commands.Bot(command_prefix=get_prefix, intents=intents)
client.remove_command('help')

currentDayClasses = []
emptybl = [""]
current_date = None
current_time = None
currentDay = None
est = pytz.timezone('US/Eastern')

# MANUAL DATABASE ADJUSTMENTS
#db["startPeriodTmw"] = 1
#db["day"] = 1
#db["status"] = None
#db["holiday"] = False
#db["currentPeriods"] = ["Period 1: D", "Period 2: E", "Break", "Period 3: F", "Period 4: G", "Lunch/Plus", "Period 5: A"]
#db["sysCheck"] = "None"
#db["timeCheck"] = None
#db["pride"] = True
#db["bans"] = []
#db["bans"] = []

#  ----------------- SETUP OF BOT ----------------- #
@client.event
async def on_message(message):
  if message.content == ">CMDnullOverride" and message.author.id == 743999268167352651:
    db[str(message.guild.id)] = "."
    embed = discord.Embed(title = "", description = "Prfx error resolved.", colour = discord.Colour.green())
    await message.channel.send(embed = embed)
  elif str(message.author.id) in db["bans"]:
    return
  else:
    await client.process_commands(message)
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('>help'))
@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = ">"
@client.command(pass_context=True)
async def broadcast(ctx, *msg):
    for server in client.guilds:
        for channel in server.channels:
          try:
            args = ""
            for i in range(len(msg)):
              args += msg[i] + " "
            await channel.send(args)
          except Exception:
            continue
          else:
            break
@client.command()
async def prefix(ctx, cmd):
  embed = discord.Embed(title = "", description = "Current prefix: " + str(cmd), colour = discord.Colour.green())
  await ctx.channel.send(embed = embed, delete_after = 5)
@client.command()
async def changePrefix(ctx, cmd):
  try:
    if(len(cmd) == 1):
      db[str(ctx.message.guild.id)] = str(cmd)
      embed = discord.Embed(title = "", description = "New prefix has been set.", colour = discord.Colour.green())
      await ctx.channel.send(embed = embed)
    else:
      embed = discord.Embed(title = "", description = "Prefixes cannot be longer than 1 character.", colour = discord.Colour.red())
      await ctx.channel.send(embed = embed, delete_after = 5)
  except:
    embed = discord.Embed(title = "", description = "Failed to change command. Try later.", colour = discord.Colour.red())
    await ctx.channel.send(embed = embed, delete_after = 5)
@client.command()
async def rename(ctx, name):
  try:
    if(ctx.author.id == 743999268167352651):
      await client.user.edit(username=name)
      embed = discord.Embed(title = "", description = "Name Successfully Changed.", colour = discord.Colour.green())
    await ctx.channel.send(embed = embed)
  except:
    embed = discord.Embed(title = "", description = "Issues with changing name. Too many requests or the name is overused.", colour = discord.Colour.red())
    await ctx.channel.send(embed = embed, delete_after = 5)
#  ------------------------------------- #


#  ----------SCHEDULE HANDLER----------- #
def embeds(ctx, list_msg, msg, color, time):
  embed = discord.Embed(title=list_msg, description=msg, colour=color)
  client.loop.create_task(ctx.channel.send(embed=embed, delete_after = time))
  
def validator(message, uid):
  if str(uid) in db.keys():
    if len(db[str(uid)]) == 7:
      return True
    else:
      embeds(message, "", "Too few classes added. Use " + db[str(message.guild.id)] + "help", discord.Colour.red(), None)
      return False
  else:
    embeds(message, "", "User classes not stored. Use " + db[str(message.guild.id)] + "help", discord.Colour.red(), None)
    return False

def schedules(ctx, uid, gen, stalk):
  name = ""
  if(gen == False):
    name = "[" + client.get_user(uid).name + "]"
  school = current_time >= '00:00:00' and current_time <= '13:55:00'
  afterSchool = not school
  msg = ""
  filler = ""
  list_msg = None
  normalTimes = [
        "07:19 - 08:19", "08:23 - 09:23", "09:27 - 09:35", "09:39 - 10:39",
        "10:43 - 11:43", "11:47 - 12:52", "12:56 - 01:51"
    ]
  prideTimes = [
        "07:19 - 08:09", "08:13 - 09:03", "09:07 - 09:55", "09:59 - 10:49",
        "10:53 - 11:43", "11:47 - 12:52", "12:56 - 01:51"
    ]
  currentTimes = []
  colors = [
        0xdbbe8a, 0xcae394, 0x82adc4, 0xc0a8f0, 0x8c2727, 0xe08743, 0xffc800, 0x6e7a58, 0x8affcc, 0x5a6e65
    ]
  if(db["pride"] == True):
    currentTimes = prideTimes
    filler = "Pride"
  if(db["pride"] == False):
    currentTimes = normalTimes
    filler = "Break"
  if (school and db["day"] < 5):
    list_msg = "**Today's Schedule:  " + name + "** \n"
  elif (afterSchool and (db["day"] != 4) and (db["day"] < 5) and db["holiday"]==False):
    list_msg = "**Tommorrow's Schedule:  " + name + "** \n"
  elif (afterSchool and (db["day"] >= 4) and db["holiday"]==False):
    list_msg = "**Monday's Schedule: " + name + "** \n"
  elif (db["holiday"]==True):
    list_msg = "**Schedule After Return: " + name + "** \n"
  k = 5
  for i in range(7):
    if not gen:
      if i == 2:
            msg = msg + ("*" + (currentTimes[i]) + "*" + " - **" + filler + "**\n")
      elif i == 5:
            msg = msg + ("*" + (currentTimes[i]) + "*" + " - **" + "Lunch/PLUS" + "**\n")
      elif i != 2 and i != 5:
            msg = msg + ("*" + (currentTimes[i]) + "*" + " - **" + db[str(uid)][db["startPeriodTmw"]-k] + "**\n")
            k = k - 1
    else:
      if i == 2:
          msg = msg + ("*" + (currentTimes[i]) + "*" + " - **" + filler + "**\n")
      else:
        msg = msg + ("*" + (currentTimes[i]) + "*" + " - **" + db["currentPeriods"][i] + "**\n")
  embed = discord.Embed(title=list_msg, description=msg, colour=random.choice(colors))
  if(stalk):
    embed.set_footer(text="Use >private to private schedule.")
  elif(gen):
    embed.set_footer(text="Use " + db[str(ctx.guild.id)] + "mySchedule for individual schedule. " + current_date + " at " + current_time + " EST")
  elif(not gen):
    embed.set_footer(text="As of " + current_date + " at " + current_time + " EST")
  client.loop.create_task(ctx.send(embed=embed))

def checkTime():
  global currentDay
  global currentPeriod
  global currentDayClasses
  global current_date
  global current_time
  schedule = ["A", "B", "C", "D", "E", "F", "G"]
  threading.Timer(1, checkTime).start()
  now1 = datetime.now()
  current_date = now1.astimezone(est).strftime("%m-%d")
  current_time = now1.astimezone(est).strftime("%H:%M:%S")
  if (current_time == db["timeCheck"]):
    db["sysCheck"] = "Checked " + str(current_date) + " " + str(current_time)
  # -------- Auto 7AM HIT --------#
  if (current_time == "06:30:00" and db["day"] < 5 and db["holiday"] == False):
    channel = client.get_channel(932858966638223390)
    schedules(channel, 765582891949883403, True, False)
  

  # ---------- 2PM HIT ----------#
  if (current_time == '13:52:03' and db["day"] < 5 and db["holiday"]==False): 
    currentDayClasses = []
    currentPeriod = db["startPeriodTmw"]
    if (db["day"] == 4 or db["day"] == 1 or db["day"] == 3):
      for i in range(7):
        if currentPeriod == 7:
          currentPeriod = 0
        if i !=2 and i != 5 and i != 6:
          currentDayClasses.append("Period " + str(i + 1) + ": " + schedule[currentPeriod])
          currentPeriod += 1
        if i == 5:
          currentDayClasses.append("Period " + str(i) + ": " + schedule[currentPeriod])
          currentPeriod += 1
        if i == 4:
          currentDayClasses.append("Lunch/Plus")
        if i == 2:
         currentDayClasses.append("filler")
        db["pride"] = False
        db['startPeriodTmw'] = currentPeriod
    else:
      for i in range(7):
        if currentPeriod == 7:
          currentPeriod = 0
        if i !=2 and i != 5 and i != 6:
          currentDayClasses.append("Period " + str(i + 1) + ": " + schedule[currentPeriod])
          currentPeriod += 1
        if i == 5:
          currentDayClasses.append("Period " + str(i) + ": " + schedule[currentPeriod])
          currentPeriod += 1
        if i == 4:
          currentDayClasses.append("Lunch/Plus")
        if i == 2:
          currentDayClasses.append("filler")
        db["pride"] = True
        db['startPeriodTmw'] = currentPeriod
    db["status"] = "schedule updated " + str(current_date) + " " + str(current_time)
    db["currentPeriods"] = currentDayClasses
  if (current_time == '23:59:59'):
    currentDay = db["day"]
    currentDay += 1
    if (currentDay == 7):
      currentDay = 0
    # store the current day
    db["day"] = currentDay

checkTime()


# ---------------------------------------- #
# -------------- ALL COMMANDS ------------ #
# ---------------------------------------- #


# ------------ SCHEDULE COMMANDS --------- #
@client.command()
async def schedule(message):
  schedules(message, message.author.id, True, False)
@client.command()
async def mySchedule(message):
  if(validator(message, message.author.id)):
    schedules(message, message.author.id, False, False)

@client.command()
async def private(ctx):
  try: 
    db[str(ctx.author.id) + "priv"] = not db[str(ctx.author.id) + "priv"]
    var = db[str(ctx.author.id) + "priv"]
    embeds(ctx, "", "Schedule private status " + str(var), discord.Colour.green(), None)
  except:
    db[str(ctx.author.id) + "priv"] = True
    embeds(ctx, "", "Schedule private status set True", discord.Colour.green(), None)
@client.command()
async def stalk(ctx, user: discord.User):
  if str(user.id) not in db.keys():
    embeds(ctx, "", "User does not have classes stored.", discord.Colour.red(), 5)
    return
  elif len(db[str(user.id)]) != 7:
    embeds(ctx, "", "Too few classes added for this person. Use " + str(db[str(user.id)]) + "addClass or " + str(db[str(user.id)]) +"addClasses", discord.Colour.red(), 5)
    return
  try:
    if db[str(user.id) + "priv"] == True:
      embeds(ctx, "", "Unavailable: Users schedule is private.", discord.Colour.red(), 5)
    else:
      if(str(user.id) in db.keys()):
        schedules(ctx, user.id, False, True)
      else:
        embeds(ctx, "", "Unavailable: User was banned.", discord.Colour.red(), 5)
  except:
    if(str(user.id) in db.keys()):
      schedules(ctx, user.id, False, True)
    else:
      embeds(ctx, "", "Unavailable: Users schedule is private.", discord.Colour.red(), 5)
@client.command()
async def addClass(ctx,classes):
  if str(ctx.author.id) not in db.keys():
    db[str(ctx.author.id)] = []
  if str(ctx.author.id) in db.keys():
    if len(db[str(ctx.author.id)]) == 7:
      embeds(ctx, "", "7 classes already added. Use " + str(db[str(ctx.guild.id)]) + "reset to restart.", discord.Colour.red(), 5)
    elif len(db[str(ctx.author.id)]) < 7:
      db[str(ctx.author.id)].append(classes)
      embeds(ctx, "", str(classes) + " has been added.", discord.Colour.green(), 5)
@client.command()
async def addClasses(ctx,*classes):
  if str(ctx.author.id) not in db.keys():
    db[str(ctx.author.id)] = []
    if len(classes) == 7:
      for i in range(len(classes)):
        db[str(ctx.author.id)].append(classes[i])
      embeds(ctx, "", "Classes added!", discord.Colour.green(), None)
    elif len(classes) != 7:
      embeds("", "Too few or too many classes. Classes with multiple words should used quotations around them.", discord.Colour.red(), 5)
  elif str(ctx.author.id) in db.keys():
    if len(db[str(ctx.author.id)]) == 7:
      embeds(ctx, "", "7 classes already added. Use " + str(db[str(ctx.guild.id)]) + "reset to restart", discord.Colour.red(), 5)
    elif len(classes) == 7:
      for i in range(len(classes)):
        db[str(ctx.author.id)].append(classes[i])
      embeds(ctx, "", "Classes added!", discord.Colour.green(), None)
    elif len(classes) != 7:
      embeds("", "Too few or too many classes. Classes with multiple words should used quotations around them.", discord.Colour.red(), 5)
@client.command()
async def swapClasses(ctx, class1, class2):
  if str(ctx.author.id) not in db.keys():
    embeds(ctx, "", "Classes for user not stored yet. Use " + str(db[str(ctx.guild.id)]) + "addClasses or " + str(db[str(ctx.guild.id)]) + "addClass to set classes.", discord.Colour.red(), 5)
  elif(str(ctx.author.id) in db.keys()):
    msg = "Class not found!"
    for i in range(len(db[str(ctx.author.id)])):
      if str(db[str(ctx.author.id)][i]) == str(class1):
        db[str(ctx.author.id)][i] = class2
        msg = "Classes swapped!"
    if("not found" in msg):
      colorSel = discord.Colour.red()
    else:
      colorSel = discord.Colour.green()
    embeds(ctx, "", msg, colorSel, None)
@client.command()
async def reset(ctx):
  if str(ctx.author.id) not in db.keys():
    embeds(ctx, "",  "There are no classes to reset.", discord.Colour.red(), 5)
  if str(ctx.author.id) in db.keys():
    del db[str(ctx.author.id)]
    embeds(ctx, "",  "Classes reset!", discord.Colour.green(), None)


# ---------- OWNER COMMANDS ---------- #
@client.command()
async def ban(ctx, user: discord.User, *args):
  banmsg = ""
  if(ctx.author.id == 743999268167352651):
    banlist = db["bans"]
    if(str(user.id) in banlist):
      embeds(ctx, "", str(user.name) + " was already banned.", discord.Colour.red(), None)
    else:
      if(str(user.id) in db.keys()):
        del db[str(user.id)]
      banlist.append(str(user.id))
      db["bans"] = banlist
      channel = await user.create_dm()
      for i in range(len(args)):
        banmsg += (args[i] + " ")
      await channel.send("You have been banned. Reason: " + banmsg)
      embeds(ctx, "", str(user.name) + " is now banned.", discord.Colour.green(), None)
  else:
    embeds(ctx, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def unban(ctx, user: discord.User):
  if(ctx.author.id == 743999268167352651):
    banlist = db["bans"]
    if str(user.id) in db["bans"]:
      banlist.remove(str(user.id))
      db["bans"] = banlist
      channel = await user.create_dm()
      await channel.send("You have been unbanned.")
      embeds(ctx, "", str(user.name) + " is now unbanned.", discord.Colour.green(), None)
    elif user.id not in db["bans"]:
      embeds(ctx, "", str(user.name) + " is not on ban list.", discord.Colour.red(), None)
  else:
    embeds(ctx, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def day(message):
  days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  if(message.author.id == 743999268167352651):
    embeds(message, "", str(days[db["day"]]) + ", " + str(current_date), discord.Colour.green(), None)
  else:
    print("here")
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def SDAT(message):
  if(message.author.id == 743999268167352651):
    embeds(message, "", "The start day after tomorrow is: " + str(schedule[db["startPeriodTmw"]]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def status(message):
  if(message.author.id == 743999268167352651):
    embeds(message, "", str(db["status"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def holidayTrue(message):
  if(message.author.id == 743999268167352651 or message.author.id == 235148962103951360):
    db["holiday"] = True
    embeds(message, "", "Holiday status set: " + str(db["holiday"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def holidayFalse(message):
  if(message.author.id == 743999268167352651 or message.author.id == 235148962103951360):
    db["holiday"] = False
    embeds(message, "", "Holiday status set: " + str(db["holiday"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def sysCheck(message):
  if(message.author.id == 743999268167352651):
    embeds(message, "", str(db["sysCheck"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()  
async def prideStatus(message):
  if(message.author.id == 743999268167352651):
    embeds(message, "", "Pride status is currently " + str(db["pride"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def prideChange(message):
  if(message.author.id == 743999268167352651):
    db["pride"] = not db["pride"]
    embeds(message, "", "Pride change to: " + str(db["pride"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def sysCheckTime(message):
  if(message.author.id == 743999268167352651):
    embeds(message, "", "System will be checked at: " + str(db["timeCheck"]), discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def sysCheckTimeIn(message, args):
  if(message.author.id != 743999268167352651):
    db["timeCheck"] = str(args)
    embeds(message, "", str(args) + " is the set time.", discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def keys(message):
  if(message.author.id == 743999268167352651):
    keys = db.keys()
    embeds(message, "", keys, discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)
@client.command()
async def blocks(message):
  if(message.author.id == 743999268167352651):
    embeds(message, "", db["currentPeriods"], discord.Colour.green(), None)
  else:
    embeds(message, "", "Owner only command", discord.Colour.red(), 5)

# --- HELP COMMANDS --- #
@client.command()
async def help(message):
    result = "\n"
    cmd = db[str(message.guild.id)]
    list_msg ="__**EducationalThings Help Menu**__ \n"
    embed = discord.Embed(title =  list_msg, description = ''.join(result), colour = 0xFFFFFF)        
    embed.add_field(name="\n**Purpose:**", value="School utilities.", inline = False)    
    embed.add_field(name="\n**Summoning The Bot:**", value=f"> Use the command " + db[str(message.guild.id)] + " to summon the bot\n> default prefix is > \n> use " + db[str(message.guild.id)] + "changePrefix to change the prefx", inline = False)    
    if(message.author.id != 743999268167352651):
      embed.add_field(name="**Commands:**", value="Commands for schedules: \n\n> " + cmd + "schedule \n> >addClass [class name] - add your own classes 1 at a time from period A to G \n> " + cmd + "addClasses [list of class names] - add classes with spaces from periods A to G, any classes with multiple words in them should use quotation marks \n> " + cmd + "swapClasses [class in list] [new class] - swaps out an existing stored class for a new one \n> " + cmd + "reset - reset your class list \n> " + cmd + "mySchedule - display your classes specifically\n> >private - make your schedule privated(others can't view it) \n> " + cmd + "stalk [@user] - find someone else's schedule", inline = False)
      embed.add_field(name="Open Source Code", value="[Here](https://replit.com/@TarunEswar2/SchoolSchedule?__cf_chl_jschl_tk__=cz0kvjdELQELMwXoKVuOyC0IBQCwXW6uLeXU2azq3fU-1640883188-0-gaNycGzNC6U#main.py)")
    else:
      embed.add_field(name="**Link to code**", value="[Here](https://replit.com/@TarunEswar2/SchoolSchedule?__cf_chl_jschl_tk__=cz0kvjdELQELMwXoKVuOyC0IBQCwXW6uLeXU2azq3fU-1640883188-0-gaNycGzNC6U#main.py)")
      embed.add_field(name="**Commands:**", value="Commands for maintance(owner only): \n\n> " + cmd + "day \n> " + cmd + "SDAT \n> " + cmd + "holidayTrue \n> " + cmd + "holidayFalse \n> " + cmd + "status \n> " + cmd + "prideStatus \n> " + cmd + "prideChange \n> " + cmd + "sysCheck \n> " + cmd + "sysCheckTimeIn [input time] \n> " + cmd + "sysCheckTime \n> " + cmd + "keys \n> >CMDnullOverride \n> \n \n Commands for schedules: \n\n> " + cmd + "schedule - displays the general schedule \n> " + cmd + "mySchedule - display your classes specifically \n> " + cmd + "addClass [class name] - add your own classes individually from periods A to G \n> " + cmd + "addClasses [list of class names] - add classes with spaces from periods A to G, any classes with multiple words in them should use quotation marks \n> " + cmd + "swapClasses [class stored] [new class] - swaps out an existing stored class for a new one \n> " + cmd + "reset - reset your class list \n", inline = False)
    await message.channel.send(embed = embed)

# --- COMMAND ERROR --- #
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        embed = discord.Embed(title = "", description = "Command not found! Use " + str(db[str(ctx.guild.id)]) + "help for possible commands.", colour = discord.Colour.red())
        await ctx.channel.send(embed = embed, delete_after = 5)
        return
    raise error


online()
client.run(os.environ.get("TOKEN"))