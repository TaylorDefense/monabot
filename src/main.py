'''
Author: Emily Inkrott
File: main.py
Description: the main driver for MonaBot
'''

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

import config
import intents_config


default_prefixes = ['!']

def get_prefix(bot, message):
    return (bot, message)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(*default_prefixes), intents=intents_config.intents)


@bot.event
async def on_ready():
    #config.load_config()
    config.initialize_table()
    config.load_config_from_db()
    print('We have logged in as {0.user}'.format(bot))
    print(config.config_vals)

@bot.event
async def on_guild_join(guild):    
    config.add_guild(guild)
    print("new server added")

#--- TRIGGERS ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #we don't care if mona is the person sending messages
    if("tempcheck" in message.content and not "!help" in message.content):
        await call_tempcheck(message)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    msg="Welcome! " + member.mention + " just joined. Come and say hello!"
    await member.guild.system_channel.send(msg)

#--- UTILITY COMMANDS ---

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx):
    '''
    Set your current channel for moderator-only outputs.
    This is specifically for the !callmods and !tempcheck commands.
    Make sure this is a channel that only moderators can see! Note that
    !callmods and pings on tempchecks will not work unless the mod channel is set.
    '''
    print(ctx.message.channel)
    config.set_mod_channel(ctx.guild, ctx.message.channel)
    channel = bot.get_channel(config.config_vals[ctx.guild.name]["output_channel"])
    await channel.send("Output channel set!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setmodrole(ctx):
    '''
    Sets the moderator role to ping for mod output.
    This is specifically for !callmods and !tempcheck. Note that
    !callmods will not work unless the modrole is set!
    ex) `!setmodrole @moderators`
    '''
    print()
    if not ctx.message.role_mentions:
        await ctx.send("Please mention a role to set it as the moderator role.")
    elif len(ctx.message.role_mentions) != 1:
        await ctx.send("Please mention only one role to set as the moderator role.")
    else:
        print(ctx.message.role_mentions[0].id)
        config.set_mod_role(ctx.guild, ctx.message.role_mentions[0])

        if "output_channel" not in config.config_vals[ctx.guild.name].keys():
            channel = ctx.channel
        else:
            channel = bot.get_channel(config.config_vals[ctx.guild.name]["output_channel"])
        await channel.send("Moderator role set!")

@bot.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    '''
    Pings MonaBot and outputs latency in the mod channel.
    If the mod channel has not been set, latency is output in the channel
    that the command was sent in. 
    '''
    latency = bot.latency 

    if("output_channel" in config.config_vals[ctx.guild.name].keys()):
        await bot.get_channel(int(config.config_vals[ctx.guild.name]["output_channel"])).send(latency)
    else:
        await ctx.send(latency)

#--- FUN COMMANDS ---

@bot.command()
async def echo(ctx, *, content:str):
    '''
    Mona will echo back whatever you type after the command.
    ex) `!echo hello :)`
    '''
    await ctx.send(content)
    print("echo")

@bot.command()
async def hello(ctx):
    '''
    Mona will say hello :)
    '''
    message = "Hello " + ctx.author.display_name + "!"
    await ctx.send(message)
    print("hello")

@bot.command()
async def callmods(ctx):
    '''
    Silently alerts the mods when you need assistance.
    !callmods deletes the command message immediately, and pings the mods in a set output channel.
    If a mod role or an output channel has not been set, the command will not execute. See !setmodrole
    and !setchannel for how admins can set mode roles and output channels.
    '''
    print("calling mods")
    await ctx.message.delete()
    try:
        message = ctx.guild.get_role(int(config.config_vals[ctx.guild.name]["mod_role"])).mention + " " + ctx.author.mention + " is calling for assistance in " + ctx.channel.mention
        print(message)
        channel = bot.get_channel(int(config.config_vals[ctx.guild.name]["output_channel"]))
        await channel.send(message)
    except AttributeError as err:
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send("You haven't set up that command. You can do this with !setmodrole and !setchannel. If you're still having issues, make sure that the MonaBot role is at the top of your roles list, and that MonaBot has permission to see your output channel!")
        else:
            await ctx.send("Your admin hasn't set up that command.")
        print(err)
    except KeyError as err:
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send("You haven't set up that command. You can do this with !setmodrole and !setchannel. If you're still having issues, make sure that the MonaBot role is at the top of your roles list, and that MonaBot has permission to see your output channel!")
        else:
            await ctx.send("Your admin hasn't set up that command.")
        print(err)
    print("called the mods")

@bot.command()
async def tempcheck(ctx):
    '''
    Call a tempcheck to gauge people's comfort in the conversation.
    Mona will keep an eye out for the word "tempcheck" in messages, and 
    will add reactions whenever it appears even if not used in a command. 
    If the stop sign reaction is added, it's time to move on from this topic of conversation.
    '''
    await asyncio.sleep(1) 
    #note: tempcheck is a trigger, so the command doesn't actually need to do work.
    #we simply await while on_message() takes care of the call.

@bot.command()
async def selfcare(ctx):
    '''
    get a useful set of self care tips!
    This list came from the BLASEBALL server. It has been amended with the walkthrough link.
    '''
    message = """
    **Have you drank anything recently?**
    🧃 Go get a drink! 🧃
    **Have you eaten recently?**
    🍕 It is time to eat! 🍕
    **Is it past 12am?**
    🛌 Siesta Time 🛌
    **Sitting still all day?**
    🕺 Get up and move your body! 🕺
    **Cold?**
    🧣 Bundle Up! 🧣
    **Hot?**
    🧊 Have something cold! 🧊
    **Forgot your meds?**
    💊 This is your reminder to take any needed medication! 💊
    **Need to be clean?**
    🚿 Take a shower, wash your face, or at least splash some water on your face! 🚿
    **Overwhelmed?**
    🚪 Take some time to get away. 🚪
    **Need some help with self care?**
    💗 Check out https://youfeellikeshit.com/ for a helpful step by step walkthrough. 💗
    **Most Importantly**
    You are allowed to be unproductive. You are allowed to take time for yourself. Rest is important, and *you* are important! Take care of yourself!
    """
    #most of this message taken from +selfcare in the BLASEBALL discord server, implemented with carlbot.

    embed=discord.Embed(title="💗✨SELF CARE TIME✨💗", description=message, color=0xBDFDFF)
    
    try:
        await ctx.send(embed=embed)
    except:
        await ctx.send(message)

#crimes
@bot.command()
async def crimes(ctx, user: discord.Member, *, accusation = ""):
    '''
    Accuse a user of crimes and let the people vote on the verdict!
    ex) !crimes @user they eat kitkats like a heathen!
    Reactions will be used to determine a person's fate. Voting lasts for 60 seconds.
    A guilty verdict adds the CRIMINAL role to a user for one hour, then removes it.
    NOTE: Make sure that the MonaBot and Criminal roles are at the top of your roles list!
    '''
    if not ctx.message.mentions or not (user in ctx.guild.members):
        await ctx.send("At least ping the person you're accusing! (`!crimes @user [accusation])`")
        print(user)
        print(ctx.message.mentions)
        print(bot.users)
        for member in ctx.guild.members:
            print(member)
        return

    if (accusation != ""):
        accuse_message = ctx.message.author.mention + " is accusing " + user.mention + """ of crimes! The accusation is as follows:
        > """ + accusation
    else:
        accuse_message = ctx.message.author.mention + " is accusing " + user.mention + " of crimes!"
    
    
    await ctx.send(accuse_message)
    vote_message = """⚖️ **Place Your Vote** ⚖️
    > 😇 INNOCENT! 
    > 👿 GUILTY!
    > 🤷 ...abstain."""
    vote = await ctx.send(vote_message)
    await vote.add_reaction("😇")
    await vote.add_reaction("👿")
    await vote.add_reaction("🤷")

    await asyncio.sleep(60)
    reactions = [ "😇", "👿", "🤷"]
    vote_counts = [0,0,0]
    vote = await vote.channel.fetch_message(vote.id)  # Can be None if msg was deleted
    print(vote.content)
    print(vote.reactions)
    print(type(vote.reactions))
    for reaction in vote.reactions:
        print(reaction.emoji)
        print(vote_counts)
        if reaction.emoji == reactions[0]:
            vote_counts[0] = reaction.count
        elif reaction.emoji == reactions[1]:
            vote_counts[1] = reaction.count
        elif reaction.emoji == reactions[2]:
            vote_counts[2] = reaction.count
        print(vote_counts)
        
    await asyncio.sleep(3)    
    print("counts when moving on: ", vote_counts)

    if (max(vote_counts) == vote_counts[2] or (vote_counts[0] == vote_counts[1])):
        await ctx.send("The jury could not come to a conclusion. You're free to go... but we're watching you.")
    elif(max(vote_counts) == vote_counts[0]):
        await ctx.send(user.mention + " has been declared innocent of their crimes. They are free to go.")
    elif(max(vote_counts) == vote_counts[1]):
        await ctx.send(user.mention + " has been found GUILTY. Jail for the criminal! Jail for the criminal for 100 years! (Or the next hour)")          
        role = discord.utils.get(ctx.guild.roles, name="CRIMINAL")
        if role is None:
            # Doesn't exist, create the role here
            role = await ctx.guild.create_role(name="CRIMINAL", color=discord.Colour.red(), hoist=True)
        role = discord.utils.get(ctx.guild.roles, name="CRIMINAL")
        if role == None:
            print("role not found")
            return
        else:
            await user.add_roles(role)
            await asyncio.sleep(3600)
            print(user.roles)
            print(role.id)
            print(role in user.roles)
            await user.remove_roles(role)
   
#bot.command()


#go to sleep
#part trigger, part command
#command to tell mona to tell u to sleep
#TODO: Figure out scheduled events!

#--- helper functions ---
async def call_tempcheck(message : discord.Message):
    '''
    Call a tempcheck to gauge people's comfort in the conversation.
    Mona will keep an eye out for the word "tempcheck" in messages, and 
    will add reactions whenever it appears. If the stope sign reaction
    is added, it's time to move on from this topic of conversation.
    '''
    print("calling tempcheck!")
    reactions = [ "✅", "⚠️", "🛑"]
    for emoji in reactions:
        await message.add_reaction(emoji)

    try:
        msg = message.guild.get_role(int(config.config_vals[message.guild.name]["mod_role"])).mention + " " + message.author.mention + " is calling a tempcheck in " + message.channel.mention
        channel = bot.get_channel(int(config.config_vals[message.guild.name]["output_channel"]))
        await channel.send(msg)
    except AttributeError:
        if message.author.guild_permissions.administrator:
            await message.reply("You haven't set up your moderation settings. You can do this with !setmodrole and !setchannel. If you're still having issues, make sure that the MonaBot role is at the top of your roles list, and that MonaBot has permission to see your output channel!")
    except KeyError:
        if message.author.guild_permissions.administrator:
            await message.reply("You haven't set up your moderation settings. You can do this with !setmodrole and !setchannel. If you're still having issues, make sure that the MonaBot role is at the top of your roles list, and that MonaBot has permission to see your output channel!")

    return

#the below commands are for amending the database from discord if the console is not accessible
'''
@bot.command()
@commands.has_permissions(administrator=True)
async def showdb(ctx):
    config.show_db_instances()
    await asyncio.sleep(2)

@bot.command()
@commands.has_permissions(administrator=True)
async def cleardb(ctx):
    config.clear_db()
    await asyncio.sleep(2)

'''

load_dotenv()
#--- DATABASE STUFF ---
config.initialize_table()
config.load_config_from_db()
TOKEN = str(os.getenv('TOKEN'))
bot.run(TOKEN)