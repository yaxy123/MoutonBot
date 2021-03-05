# bot.py
import os

import discord
import requests
import random
import re
from html import unescape
from dotenv import load_dotenv
from sys import exit

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

players = {}
questions = {}
answers = {}
leaderboard = {}
with open('leaderboard.txt', 'r') as sf:
    lines = sf.readlines()
    for line in lines:
        info = line.split()
        leaderboard[int(info[0])] = int(info[1])

scoreboard = [0,100,200,300,500,1000,2000,4000,8000,16000,32000,64000,125000,250000,500000,1000000]

async def save(dic):
    with open('leaderboard.txt', 'r+') as f:
        f.truncate(0)
        f.close()
    with open('leaderboard.txt', 'w') as f:
        for key in dic:
            f.write(f'{key} {dic[key]}\n')

async def next_question(message, player):
    if players[player] == 5:
        await message.channel.send(f'<@{player}> Congratulations you secured $1,000')
        leaderboard[player] += 1000
        await save(leaderboard)
    if players[player] == 10:
        await message.channel.send(f'<@{player}> Congratulations you secured $32,000')
        leaderboard[player] += 32000
        await save(leaderboard)
    if players[player] == 15:
        await message.channel.send(f'<@{player}> Congratulations you won $1,000,000')
        leaderboard[player] += 1000000
        await save(leaderboard)

    print(questions[player][players[player]])
    question_data = questions[player][players[player]]
    pos = random.randint(0, 3)
    print(pos)
    question = question_data[0]
    answer = question_data[1]
    options = question_data[2]
    options.insert(pos, answer)
    answers[player] = pos
    await message.channel.send(f'<@{player}> {unescape(question)}\nA:{unescape(options[0])}\nB:{unescape(options[1])}\nC:{unescape(options[2])}\nD:{unescape(options[3])}')

async def generate_questions(player):
    print("Generating new trivia")
    players[player] = 1
    questions[player] = []
    url = "https://opentdb.com/api.php?amount=5&difficulty=easy&type=multiple"

    r = requests.get(url)

    data = r.json()
    for i in range(5):
        questions[player].append([data['results'][i]['question'], data['results'][i]['correct_answer'],
                             data['results'][i]['incorrect_answers']])

    url = "https://opentdb.com/api.php?amount=5&difficulty=medium&type=multiple"

    r = requests.get(url)

    data = r.json()
    for i in range(5):
        questions[player].append([data['results'][i]['question'], data['results'][i]['correct_answer'],
                             data['results'][i]['incorrect_answers']])

    url = "https://opentdb.com/api.php?amount=5&difficulty=hard&type=multiple"

    r = requests.get(url)

    data = r.json()
    for i in range(5):
        questions[player].append([data['results'][i]['question'], data['results'][i]['correct_answer'],
                             data['results'][i]['incorrect_answers']])

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.content == "!trivia":
        player = message.author.id
        if player not in players:
            await generate_questions(player)
            if player not in leaderboard:
                leaderboard[player] = 0

        print("starting trivia")
        await next_question(message, player)

    if message.content == '!A' or message.content == '!B' or message.content == '!C' or message.content == '!D':
        player = message.author.id
        answer = answers[player]
        if message.content == '!A' and answer == 0:
            await message.channel.send(f"Gratz you choose the right answer! Current pot: ${scoreboard[players[player]]}")
            players[player] += 1
            await next_question(message, player)
        elif message.content == '!B' and answer == 1:
            await message.channel.send(f"Gratz you choose the right answer! Current pot: ${scoreboard[players[player]]}")
            players[player] += 1
            await next_question(message, player)
        elif message.content == '!C' and answer == 2:
            await message.channel.send(f"Gratz you choose the right answer! Current pot: ${scoreboard[players[player]]}")
            players[player] += 1
            await next_question(message, player)
        elif message.content == '!D' and answer == 3:
            await message.channel.send(f"Gratz you choose the right answer! Current pot: ${scoreboard[players[player]]}")
            players[player] += 1
            await next_question(message, player)
        else:
            await message.channel.send(f"Wrong answer dumbfuck <:OOO:817450777379209217>")
            if answer == 0:
                await message.channel.send("The answer was A")
            elif answer == 1:
                await message.channel.send("The answer was B")
            elif answer == 2:
                await message.channel.send("The answer was C")
            elif answer == 3:
                await message.channel.send("The answer was D")
            await generate_questions(player)
            await next_question(message, player)

    if message.content == '!leaderboard':
        lb = ""
        dict(sorted(leaderboard.items(), key=lambda item: item[1])) 
        for player in leaderboard:
            lb += f"{await client.fetch_user(player)}: ${leaderboard[player]}" + '\n'
            #await message.channel.send(f"{await client.fetch_user(player)}: ${leaderboard[player]}")
        await message.channel.send(lb)

        

    if message.content == '!stop':
        player = message.author.id
        await message.channel.send(f'<@{player}> Congratulations you won ${scoreboard[players[player]-1]}')
        winnings = scoreboard[players[player]-1]
        if players[player] >= 5:
            winnings -= 1000
        if players[player] >= 10:
            winnings -= 32000
        leaderboard[player] += winnings
        await save(leaderboard)
        await generate_questions(player)

    if message.content == '!help':
        player = message.author.id
        await message.channel.send(f'<@{player}> Type !trivia to start playing, and type !A,!B,!C or !D to answer, type !stop to stop at any point and take back your winnings. You can type !leaderboard to see the current leaderboard')

    if message.author.id == 789915873250377728:
        if message.channel.id == 311605450724474880:
            pattern = re.compile("[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
            if pattern.match(message.content):
                await client.channels.get(733367403378901023).send(f"<@{message.author.id}> Did you know that there is a channel for memes called #meme, you should check that out instead of posting it in the pasture <PogO~1:774024977098997821>")


client.run(TOKEN)
