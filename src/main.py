'''
Author: Emily Inkrott
File: main.py
Description: the main driver for MonaBot
'''

import discord
from discord.ext import commands
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
    config.load_config()
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_guild_join(guild):    
    config.change_config(guild, "id", guild.id)
    print("new channel added")

#--- TRIGGERS ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #we don't care if mona is the person sending messages
    print(message.guild, message.author, message.content)
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
    Set the current channel for moderator-only outputs.
    This is specifically for the !callmods and !tempcheck commands.
    Make sure this is a channel that only moderators can see! Note that
    !callmods will not work unless the mod channel is set!
    '''
    print(ctx.message.channel)
    config.change_config(ctx.guild, "output_channel", ctx.message.channel.id)
    channel = bot.get_channel(config.config_vals[ctx.guild.name]["output_channel"])
    await channel.send("Output channel set!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setmodrole(ctx):
    '''
    Sets the role to ping for mod output.
    This is specifically for !callmods and !tempcheck. Note that
    !callmods will not work unless the modrole is set!
    '''
    print()
    if not ctx.message.role_mentions:
        await ctx.send("Please mention a role to set it as the moderator role.")
    elif len(ctx.message.role_mentions) != 1:
        await ctx.send("Please mention only one role to set as the moderator role.")
    else:
        print(ctx.message.role_mentions[0].id)
        config.change_config(ctx.guild, "mod_role", ctx.message.role_mentions[0].id)

        if "output_channel" not in config.config_vals[ctx.guild.name].keys():
            channel = ctx.channel
        else:
            channel = bot.get_channel(config.config_vals[ctx.guild.name]["output_channel"])
        await channel.send("Moderator role set!")

@bot.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    '''
    Pings MonaBot and outputs latency in the chat.
    '''
    latency = bot.latency 
    await ctx.send(latency) 

    if("output_channel" in config.config_vals[ctx.guild.name].keys()):
        await bot.get_channel(config.config_vals[ctx.guild.name]["output_channel"]).send(latency)
    else:
        await ctx.send(latency)

#--- FUN COMMANDS ---

@bot.command()
async def echo(ctx, *, content:str):
    '''
    Mona will echo back whatever you type after the command.
    ex) !echo hello :)
    '''
    await ctx.send(content)

@bot.command()
async def hello(ctx):
    '''
    Mona will say hello :)
    '''
    message = "Hello " + ctx.author.display_name + "!"
    await ctx.send(message)

@bot.command()
async def callmods(ctx):
    '''
    Silently alerts the mods when you need assistance.
    !callmods deletes the command message immediately, and pings the mods in a set output channel.
    If a mod role or an output channel has not been set, the command will not execute. See !setmodrole
    and !setchannel for how admins can set mode roles and output channels.
    '''
    await ctx.message.delete()

    if not "mod_role" in config.config_vals[ctx.guild.name].keys():
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send("No mod role has been specified. Your admin can do this with !setmodrole")
        else:
            await ctx.send("Your admin hasn't set up that command.")
    else:
        message = ctx.guild.get_role(config.config_vals[ctx.guild.name]["mod_role"]).mention + " " + ctx.author.mention + " is calling for assistance in " + ctx.channel.mention
        print(message)
        if not "output_channel" in config.config_vals[ctx.guild.name].keys() :
            await ctx.send("No mod channel has been specified. Your admin can do this with !setchannel")
        else:
            channel = bot.get_channel(config.config_vals[ctx.guild.name]["output_channel"])
            await channel.send(message)

@bot.command()
async def tempcheck(ctx):
    '''
    call a tempcheck to gauge people's comfort in the conversation.
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
    message = """> 💗✨SELF CARE TIME✨💗
    > **Have you drink recently?**
    > 🧃 Go get a drink! 🧃
    > **Have you eaten recently?**
    > 🍕 It is time to eat! 🍕
    > **Past 12am?**
    > 🛌 Siesta Time 🛌
    > **Sitting still all day?**
    > 🕺 Get up and move your body! 🕺
    > **Cold?**
    > 🧣 Bundle Up! 🧣
    > **Hot?**
    > 🧊 Have something cold! 🧊
    > **Forgot your meds?**
    > 💊 This is your reminder to take any needed medication! 💊
    > **Need to be clean?**
    > 🚿 Take a shower, wash your face, or at least splash some water on your face! 🚿
    > **Overwhelmed?**
    > 🚪 Take some time to get away. 🚪
    > **Need some help with self care?**
    > 💗 Check out https://youfeellikeshit.com/ for a helpful step by step walkthrough. 💗
    > **Most Importantly**
    > You are allowed to be unproductive. You are allowed to have a day off from everything. Rest is Important. Rest.
    """
    #most of this message taken from +selfcare in the BLASEBALL discord server, implemented with carlbot.
    await ctx.send(message)

#crimes
@bot.command()
async def crimes(ctx, user: discord.Member, *, accusation):
    '''
    Accuse a user of crimes and let the people vote on the verdict!
    ex) !crimes @user they eat kitkats like a heathen!
    Reactions will be used to determine a person's fate. Voting lasts for 60 seconds,
    and a guilty verdict adds the CRIMINAL role to a user for one hour, then removes it.
    '''
    if not ctx.message.mentions or not (user in ctx.guild.members):
        await ctx.send("At least ping the person you're accusing! (`!crimes @user [accusation])`")
        print(user)
        print(ctx.message.mentions)
        print(bot.users)
        for member in ctx.guild.members:
            print(member)
        return
    accuse_message = ctx.message.author.mention + " is accusing " + user.mention + """of crimes! The accusation is as follows:
     > """ + accusation
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
   


#go to sleep
#part trigger, part command
#command to tell mona to tell u to sleep
#TODO: Figure out scheduled events!

#--- helper functions ---
async def call_tempcheck(message : discord.Message):
    '''
    call a tempcheck to gauge people's comfort in the conversation.
    Mona will keep an eye out for the word "tempcheck" in messages, and 
    will add reactions whenever it appears. If the stope sign reaction
    is added, it's time to move on from this topic of conversation.
    '''
    print("calling tempcheck!")
    reactions = [ "✅", "⚠️", "🛑"]
    for emoji in reactions:
        await message.add_reaction(emoji)

    if "mod_role" in config.config_vals[message.guild.name].keys():
        msg = message.guild.get_role(config.config_vals[message.guild.name]["mod_role"]).mention + " " + message.author.mention + " is calling a tempcheck in " + message.channel.mention
        if not "output_channel" in config.config_vals[message.guild.name].keys() :
            channel = message.channel
        else:
            channel = bot.get_channel(config.config_vals[message.guild.name]["output_channel"])
        await channel.send(msg)
    return


#may need to take this out of main if the bot doesn't work
'''def main():
    config.load_config()
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN)
    
if __name__ == "__main__":
    main()
'''
config.load_config()
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)