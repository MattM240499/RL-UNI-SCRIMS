from discord.ext.commands import Bot
from discord import Game
import discord
import asyncio
import random
import google_io
from bot_token import TOKEN

BOT_PREFIX = ("!")
global gameReady
games = []
gameQueue = []
gameReady = False
client = Bot(command_prefix=BOT_PREFIX)


@client.command(name="hello",
                description="says hello",
                brief="says hello",
                aliases=["hi", "hey", "howdy", "bonjour", "hola"],
                pass_context=True)
async def hello(context):
    msg = 'Hello '+context.message.author.mention
    await client.say(msg)


@client.command(name="queue",
                description="adds you to the queue",
                brief="adds you to the queue",
                aliases=["q", "Q"],
                pass_context=True)
async def queue(context):
    if context.message.author not in gameQueue:
        if len(gameQueue) != 6:
            gameQueue.append(context.message.author)
            await client.say("You have been added to the queue "+context.message.author.mention)
            await client.say("There are currently "+str(len(gameQueue))+" players in the queue")
        else:
            await client.say("Queue is full"+context.message.author.mention)
    else:
        await client.say("Already in queue "+context.message.author.mention)


@client.command(name="leave",
                description="removes you from the queue",
                brief="removes you from the queue",
                aliases=["l"],
                pass_context=True)
async def leave(context):
    if context.message.author in gameQueue:
        gameQueue.remove(context.message.author)
        await client.say("You have been removed from the queue "+context.message.author.mention)
        await client.say("There are currently "+str(len(gameQueue))+" players in the queue")
    else:
        await client.say("You are not in the queue "+context.message.author.mention)


@client.command(name="status",
                description="gets status of queue",
                brief="gets status of queue",
                aliases=["s", "S"],
                pass_context=True)
async def status(context):
    msg = "Current players in the queue "
    for i in gameQueue:
        msg += (str(i)[0:-5]+", ")  # discord names
    await client.say(msg)


@client.command(name="report score",
                description="!report <win/loss> <your score> <opponents score>",
                brief="report score of current match",
                aliases=["report", ],
                pass_context=True)
async def report_score(context, result, score1, score2):
    print(games)
    gamefound = False
    if result in ["win", "loss"]:
        if result == "loss":
            x = score1
            score1 = score2
            score2 = x
        if games:  # if list not empty
            for game in range(len(games)):
                print(games[game])
                if context.message.author in games[game][0]:
                    print("Found player on Blue team")
                    record = [str(games[game][0][0])[0:-5], str(games[game][0][1])[0:-5], str(games[game][0][2])[0:-5], str(
                        score1), str(score2), str(games[game][1][0])[0:-5], str(games[game][1][1])[0:-5], str(games[game][1][2])[0:-5]]
                    print(record)
                    gameFound = True
                    del games[game]
                    break

                elif context.message.author in games[game][1]:
                    record = [str(games[game][0][0])[0:-5], str(games[game][0][1])[0:-5], str(games[game][0][2])[0:-5], str(
                        score2), str(score1), str(games[game][1][0])[0:-5], str(games[game][1][1])[0:-5], str(games[game][1][2])[0:-5]]
                    print("Found player on Orange team")
                    print(record)
                    gameFound = True
                    del games[game]
                    break

                else:
                    print("player not found")
            if gameFound:
                google_io.addRecord(record)
                msg = context.message.author.mention+" reported the score as: " + \
                    record[0]+", "+record[1]+", "+record[2]+" "+record[3] + \
                    " - "+record[4]+" "+record[5]+", "+record[6]+", "+record[7]
            else:
                msg = "You are not currently in any games "+context.message.author.mention
            await client.say(msg)
        else:
            await client.say("There are currently no active games"+context.message.author.mention)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Rocket League"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


async def backgroundTasks():
    global gameReady
    global game
    await client.wait_until_ready()
    while not client.is_closed:
        if isQueueFull():
            gameReady = True
        if gameReady:
            newGame = createGame()
            Blue = newGame[0]
            Orange = newGame[1]
            games.append(newGame)
            channel = discord.Object(id='512004628942946306')
            # channel = discord.Object(id='491408697168494630') #test channel
            msg = "Team A: "+str(Blue[0])+", " + \
                str(Blue[1]) + ", " + str(Blue[2])
            await client.send_message(channel, msg)
            msg = "Team B: "+str(Orange[0])+", " + \
                str(Orange[1]) + ", " + str(Orange[2])
            await client.send_message(channel, msg)
        await asyncio.sleep(1)


def isQueueFull():
    if len(gameQueue) == 6:
        return True


def createGame():
    Blue = []
    Orange = []
    global gameReady
    if gameReady == True:
        for i in range(5, 2, -1):
            x = random.randint(0, i)
            player = gameQueue[x]
            Blue.append(player)
            gameQueue.remove(player)
        for i in range(2, -1, -1):
            player = gameQueue[i]
            Orange.append(player)
            gameQueue.remove(player)

        gameReady = False
    return [Blue, Orange]


client.loop.create_task(backgroundTasks())
client.run(TOKEN)
