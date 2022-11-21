# MonaBot: Multipurpose Discord Bot

Monabot began as a project for a one day Hackathon, and has since become a little passion project for me. Commands are implemented according to requests and my own abilities with the discord API.

## Setup
MonaBot's setup is fairly simple! Once it joins a server, make sure that the MonaBot role is higher on the roles list than any member roles (other bot roles are fine though!). This is so that 
MonaBot can "see" all of the roles to execute commands involving moderator roles and the `!crimes` command.

## Triggers
Triggers activate whenever a certain event occurs, without users entering a command. Below is a list of triggers I have implemented thusfar.
* __`tempcheck`__
  * Activation: when the word "tempcheck" is included in a message.
  * Adds reactions ("✅", "⚠️", "🛑") to the message that called the command so that users can express their comfort level with the conversation. Mods are alerted when a tempcheck occurs if !setmodrole and !setchannel have been called successfully.
  * If any users react with the "🛑" reaction, it's probably time to move on from that topic!
  * _Note: this is functionally identicall to the `!tempcheck` command._
  * Example: The message `I'm calling a tempcheck` will trigger MonaBot to add the three reactions to the message. The mods (or role specified with `!setmodrole` will get a ping in the channel set with `!setchannel` with the channel it was sent in and the name of the person who called the tempcheck.
* __New server member__
  * Activation: when a new member joins the server
  * Sends a personalized greating in the server's system messages channel.

## Commands
Below is a list of commands that I have implemented thusfar.
#### Admin Only Commands
* __`!setmodrole`__
  * Sets the role that MonaBot will ping when dealing with moderation commands.
  * Example: `!setmodrole @moderators` will set the `moderators` role as the one MonaBot will ping.
* __`!setchannel`__
  * Sets the channel the command is called in as the output channel for moderation commands.
  * _Note: it is recommended that this be a channel only visible to moderators (or the role chosen with !setmodrole) since it will contain information from moderation commands that might be best kept hidden._
  * Example: calling `!setchannel` in `#mod-pings` will direct all moderation command output to the `#mod-pings` channel.
* __`!ping`__
  * Outputs MonaBot's latency in the designated output channel (if configured) or the channel the command was entered (if not configured).
 
#### Moderation Commands
* __`!callmods`__
  * Calls the mods silently to the channel where the command was entered.
  * This command immediately deletes the message that called it, so no one can see who called the mods. This aims to ease users' worries about being a "snitch" for calling the mods when uncomfortable
  * _Note: this command requires `!setmodrole` and `!setchannel` to have been successfully called by an admin so MonaBot knows who to ping and where to ping them!_
* __`!tempcheck`__
  * Adds reactions ("✅", "⚠️", "🛑") to the message that called the command so that users can express their comfort level with the conversation.
  * If any users react with the "🛑" reaction, it's probably time to move on from that topic!

#### Sily Commands
* __`!echo`__
  * MonaBot will echo back any message content that comes after the command.
  * Example: `!echo hello there (GENERAL KENOBI!)` will lead MonaBot to send the message `hello there (GENERAL KENOBI!)`
* __`!hello`__
  * MonaBot will say hello to the caller!
* __`!selfcare`__
  * MonaBot will send a list of helpful self care reminders to help users take better care of themselves.
* __`!crimes`__
  * Allows server members to accuse each other of crimes, and lets the public vote on whether the accused is guilty or innocent.
  * If found guilty, the accused will be given the `CRIMINAL` role, which changes the color of their name to red for 1 hour- after which point MonaBot will remove the role.
  * MonaBot creates the `CRIMINAL` role the first time someone is found guilty- if you notice that their name isn't changing color, make sure the `CRIMINAL` role is above any other roles that change nickname colors! 
  * Example: `!crimes @Ace he eats KitKats like a heathen` will trigger MonaBot's accusation and "trial" process. 
    * Users will have one minute to vote using reactions on MonaBot's messages- the majority reaction determines the ruling.
    * The verdict will be announced after the minute passes. The `CRIMINAL` role will be assigned in the event of a guilty verdict, then removed after one hour.
  

## Future Plans
Most important of my next steps is getting MonaBot online 24/7. Currently, the bot is hosted only from my computer, which isn't feasible in the long term. The next thing on my to-do list is to find a free way to host MonaBot so it can operate without me needing to run files on my computer at all times.
In addition to this, there are some additional commands and triggers I want to implement! They are listed below with their respective functions and holdups. This list will be updated as I receive suggestions and implement new features.
#### Commands and Triggers
* __Go to sleep!__
  * Users can ask MonaBot to remind them to log off and go to sleep at a certain time each day.
  * Ideally, MonaBot will check if a user is online before pinging them.
  * __Holdups:__ Figuring out how to schedule messages for a certain time each day.
* __Chat Censor__
  * A moderation tool that lets moderators automatically censor words of their choice with an emoji.
  * Moderators should be able to choose a custom emoji for each word, but a default one will be used if one is not specified. Moderators should also be able to change the default if they would like.
  * __Holdups:__ Lack of time and concerns about how this could be misused.
* __Annonymous Messages__
  * Allow users to submit messages, which MonaBot will post in a specified channel without the user's name associated
  * This would require a few different commands to implement:
    * A command to set the output channel. For obvious reasons, this should be different than the moderation channel, and to keep things user-friendly, the `!setchannel` command might need to be renamed to something more specific.
    * A command to submit annonymous messages. This won't be difficult to implement, and will probably be similar to some existing commands.
    * A command to report annonymous messages. Reporting a message would alert the moderators in the moderation channel about which message was reported, who reported it, and who sent the annonymous message. __Annonymity would only ever be compromised to moderators, and only in a reporting situation.__
 
  
  
  
  
  
  
  
