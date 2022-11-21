import discord
intents = discord.Intents.all()

intents.reactions= True
intents.messages= True
intents.message_content=True