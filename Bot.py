'''
Created on Apr 20, 2017

@author: Rocko
'''

import discord
import asyncio
import os
import itertools
import re
import pickle
import random
import time
import json
import string
import io
import datetime
from PIL import Image, ImageDraw, ImageSequence, ImageFont
from urllib.request import urlopen
from pathlib import Path
from typing import Union
from Trivia import Trivia
from TriviaHighScoreTable import TriviaHighScoreTable
from utilities import *
import json

class LabRatBot(discord.Client):
    def __init__(self, **options):
        discord.Client.__init__(self, **options)

        self.trigger = '.'

        self.nickname = 'Ketamouse'
        self.avatar = 'rat.jpg'
        self.status = 'with research chemicals' #Discord sets 'Playing {}' with game name. This variable is the game name

        self.trivia_instance = None
        self.in_trivia = False

        self.bot_spam_channel = '337311436327878656'
        self.mouse_discord_id = '91929884145766400'

        self.current_directory = os.path.dirname(os.path.realpath(__file__))

        self.commands = {'mute' : '(Mod) Text mute a member of the chat [ex. mute @User]',\
            'unmute' : "(Mod) Unmute a member [ex. unmute @User]",\
            'warn' : "(Mod) Warn a member [ex. warn @User]",\
            'unwarn' : "(Mod) Remove a warning from a member [ex. unwarn @User]",\
            'warnings': "View warnings for yourself or another (Mods only for viewing others) [ex. warnings OR warnings @User]",\
            'warningsall': "(Mod) View all warning counts",\
            'imgmute' : "(Mod) Mute a user from posting images in the chat [ex. imgmute @User]",\
            'imgunmute' : "(Mod) Unmute a user from posting images [ex. imgunmute @User]",\
            'addrole' : "(Mod) Give a user a role [ex. addrole @User role name here]",\
            'delrole' : "(Mod) Remove a role from a user [ex. delrole @User role name here]",\
            'selfie' : "Posts a selfie that you've posted in the #selfies channel [ex. selfie]",\
            'ping' : "Ping pong~",\
            'dosed' : "Are you high? Let the chat know! [ex. dosed MDMA 100mg]\n\tdosed start - Will get the time you issued the last dosed command",\
            'redose' : "Took another dose? Let us know! [ex. redose 200mg]",\
            'sober' : "Opposite of [dosed]. Removes the nickname and high status from your person [ex. sober]",\
            'drug' : "Get information about a drug [ex. drug MDMA]",\
            'slap' : "Slaps the f**k out of somebody [ex. slap @👿Imp👿#2125]",\
            'trivia': "Starts a trivia game! [ex. trivia @Subject @MaxScore]\n\ttrivia subjects - View possible topics\n\ttrivia join - Joins a starting game of trivia\n\ttrivia start - Starts a game with the current players (host only)\n\ttrivia end - Ends the game of trivia (only by host)\n\ttrivia highscores - View Highscore totals for trivia",\
            'whohas' : "Who has a role", \
            'custom1_kill_newcomer' : "Custom command to re-vamp the newcomer role system. You must be Mouse to use.",\

            'help' : "This message..."}

        self.imgmuted = []
        self.muted = []
        self.dosed = {}

        self.server_data_path = 'server.dat'

        if Path('dosed.pkl').exists():
            self.dosed = pickle.load(Path('dosed.pkl').open('rb'))
        if Path('imgmuted.pkl').exists():
            self.imgmuted = pickle.load(Path('imgmuted.pkl').open('rb'))
        if Path('muted.pkl').exists():
            self.muted = pickle.load(Path('imgmuted.pkl').open('rb'))

        self.imgmute_extensions = ['.jpg','.png','.bmp','.jpeg','.gif']

        self.max_warnings = 5

        

    @asyncio.coroutine
    def on_server_role_create(self,role : discord.Role):
        print('A new role, {}, has been created. Announcing to staff chat'.format(role.name))
        staff_channel = next([c for c in role.guild.channels if c.id == 232893052820258816])
        yield from staff_channel.send('A new role has been created named: {}'.format(role.name))

    @asyncio.coroutine
    def on_server_role_update(self,before : discord.Role, after : discord.Role):
        print('Role {} has been changed.'.format(before.name))
        if before.name != after.name:
            staff_channel = next([c for c in after.guild.channels if c.id == 232893052820258816])
            yield from staff_channel.send('Role with name {} has been changed to {}'.format(before.name, after.name))
        pass

    @asyncio.coroutine
    def on_ready(self):
        print('TheLabRat.py - Initialization Sequence')
        print('Logged in as \'{}\''.format(self.user.name))
        print('User ID: {}'.format(self.user.id))

        for serv in self.guilds:
            self.server = serv

        print(self.server)

        print('Setting status: "{}"'.format(self.status))
        try:
            yield from self.change_presence(activity=discord.Game(name=self.status))
        except Exception as e:
            print('Errors have occurred... ' + str(e))

        print('Setting avatar and nickname - {}'.format(self.avatar))
        try:
            yield from self.user.edit(username=self.nickname,avatar = open(self.current_directory+'\\{}'.format(self.avatar),'rb').read())
        except Exception as e:
            print('Errors have occured... ' + str(e))

        print('Initialization Complete')
        print('============================')
        print('Awaiting messages')

    @asyncio.coroutine
    def on_message(self, msg : discord.Message):
        print('[MESSAGE] [{}] [{}] ({}) - {}'.format(msg.channel.name,msg.author,msg.author.top_role,msg.content))

        message = str(msg.content).lower()

#WELCOME CHANNEL
#region
        if msg.channel.id == '505440537332023316': #Welcome channel ID
            if message.strip() == '-agree' or message.strip() == '.agree':
                newcomer_role = next(r for r in self.server.roles if r.name == 'Newcomer')
                joinee = msg.author
                yield from msg.author.remove_roles(newcomer_role)
                yield from msg.delete()
                wm = yield from msg.guild.get_channel(219867619103211520).send("{0} has joined the server".format(joinee.mention))
                yield from asyncio.sleep(5)
                yield from wm.delete()
                return
            else:
                if msg.pinned != True:
                    yield from msg.delete()
                    return
#endregion

#MUTES
#region
#IMAGE MUTE
        if msg.author.id in self.imgmuted:
            if len(msg.attachments) > 0:
                if '.'+msg.attachments[0]['url'].split('.')[-1] in self.imgmute_extensions:
                    yield from msg.delete()
                    yield from msg.channel.send( "You are image muted and cannot post image attachments {0}".format(msg.author.mention))
                    return
#TOTAL MUTE
        elif msg.author.id in self.muted:
            yield from msg.delete()
            return
#endregion 

        if msg.author.id == self.user.id:
            return
        elif message.startswith(self.trigger):
            #Commands
            command = message[1:].split(' ')[0]
            parameters = message[1:].split(' ')[1:]

            if command in self.commands.keys():
                yield from self.process_command(msg, command, parameters)
        elif self.in_trivia:
            if msg.author.id in self.trivia_instance.current_players:
                if message in self.trivia_instance.answers_given:
                    yield from msg.channel.send( "Answer {0} has already been given once".format(message))
                points = self.trivia_instance.giveAnswer(message)
                if points > 0:
                    self.trivia_instance.givePoints(msg.author.id, points)
                    
                    yield from msg.channel.send("{0} got it with '{1}'! He receives {2} points for a total of {3}.".format(msg.author.mention,message.capitalize(),points,self.trivia_instance.current_players[msg.author.id]))
                    if self.trivia_instance.current_players[msg.author.id] >= self.trivia_instance.max_score:
                        winner = msg.author
                        yield from msg.channel.send( "{0} wins the trivia game!".format(msg.author.mention))
                        self.trivia_instance.End()
                        self.trivia_instance = None
                        self.in_trivia = False
                    else:
                        self.trivia_instance.getNextQuestion()
                        yield from asyncio.sleep(5)
                        yield from msg.channel.send( "TRIVIA QUESTION ({0})\n\n{1}".format(self.trivia_instance.current_subject,self.trivia_instance.current_question.question.capitalize()))
#endregion
    @asyncio.coroutine
    async def process_command(self, msg : discord.Message, command, params):
        issuer = msg.author
        if command == 'custom1_kill_newcomer':
            if not issuer.id == 91929884145766400: #Mouse only command for debugging
                await msg.channel.send( "You are not Mouse.")
                return

            newcomer_role = next(r for r in self.server.roles if r.name == 'Newcomer')
            everyone_role = msg.channel.server.default_role
            people = msg.channel.server.members
            channels = msg.channel.server.channels

            for channel in channels:
               poveride = channel.overwrites_for(newcomer_role) or discord.PermissionOverwrite()
               poveride.send_messages = False
               poveride.read_messages = False

               peoveride = channel.overwrites_for(everyone_role) or discord.PermissionOverwrite()
               peoveride.read_messages = True
               peoveride.send_messages = True

               await channel.set_permissions(newcomer_role, poveride)
               await channel.set_permissions(everyone_role, peoveride)

        elif command == 'soberall':
            if not issuer.id == 91929884145766400: #Mouse only command for debugging
                await msg.channel.send( "You are not Mouse.")
                return
            for d in self.dosed.keys():
                us = await self.FindUser(d,msg)
                await us.edit(nick=self.dosed[d]['dname'])
            self.dosed = {}
            pickle.dump(self.dosed,Path('dosed.pkl').open('wb'))

        elif command == 'warn':
            if not msg.channel.permissions_for(issuer).kick_members:
                await msg.channel.send("You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(' '.join(params),msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            if user == issuer:
                await msg.channel.send( "Yo-...you can't warn yourself... Why would you **want** to?")
                return

            warns = {}
            if not Path('warns.pkl').exists():
                warns[user.id] = 1
            else:
                warns = pickle.load(Path('warns.pkl').open('rb'))
                if user.id in warns:
                    warns[user.id] += 1
                    await msg.channel.send("{} has been warned. He currently has {}/{} warnings".format(user.mention,warns[user.id],self.max_warnings))
                else:
                    warns[user.id] = 1
            pickle.dump(warns,Path('warns.pkl').open('wb'))
        
        elif command == 'unwarn':
            if not msg.channel.permissions_for(issuer).kick_members:
                await msg.channel.send("You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0],msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            if user == issuer:
                await msg.channel.send( "Yo-...you can't warn yourself... Why would you **want** to?")
                return

            warns = {}
            if not Path('warns.pkl').exists():
                await msg.channel.send("There are no warnings.")
                return
            else:
                warns = pickle.load(Path('warns.pkl').open('rb'))
                if user.id in warns and warns[user.id] > 0:
                    warns[user.id] -= 1
                    await msg.channel.send("1 warning has been removed for {}. He currently has {}/{} warnings".format(user.mention,warns[user.id],self.max_warnings))
                else:
                    await msg.channel.send("{} did not have any warnings".format(user.mention))

            pickle.dump(warns,Path('warns.pkl').open('wb'))

        elif command == 'warnings':
            user = None
            if len(params) > 0:
                user = await self.FindUser(' '.join(params),msg)
                if not msg.channel.permissions_for(issuer).kick_members and user != issuer:
                    await msg.channel.send("You don't have the proper permissions {}".format(issuer.mention))
                    return
            
            warns = {}
            if not Path('warns.pkl').exists():
                await msg.channel.send("There aren't any warnings on file.")
            else:
                warns = pickle.load(Path('warns.pkl').open('rb'))
                if user != None:
                    if user.id in warns:
                        await msg.channel.send("{} has {}/{} warnings".format(user.mention,warns[user.id],self.max_warnings))
                    else:
                        await msg.channel.send("{} has 0/{} warnings".format(user.mention,self.max_warnings))
                else:
                    if issuer.id in warns:
                        await msg.channel.send("{} has {}/{} warnings".format(issuer.mention,warns[issuer.id],self.max_warnings))
                    else:
                        await msg.channel.send("{} has 0/{} warnings".format(issuer.mention,self.max_warnings))

        elif command == 'warningsall':
            if not msg.channel.permissions_for(issuer).kick_members:
                await msg.channel.send("You don't have the proper permissions {}".format(issuer.mention))
                return
            
            warns = {}
            if not Path('warns.pkl').exists():
                await msg.channel.send("There aren't any warnings on file.")
            else:
                warns = pickle.load(Path('warns.pkl').open('rb'))

            await msg.channel.send("\n".join([f"{self.get_user(key)}.display_name | {value} warnings" for (key,value) in warns.items()]))

        elif command == 'mute':
            if not msg.channel.permissions_for(issuer).manage_messages:
                await msg.channel.send( "You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0],msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            if user == issuer:
                await msg.channel.send( "Yo-...you can't mute yourself...")
                return

            mute_role = discord.utils.get(user.guild.roles, name="Muted")

            path = Path('muted.pkl')
            
            if path.exists():
                temp = pickle.load(path.open('rb'))
                if user.id in temp:
                    await msg.channel.send("{0} is already muted".format(user.display_name))
                else:
                    self.muted.append(user.id)
                    pickle.dump(self.muted,path.open('wb'))
                    await msg.channel.send( "{0} was muted by {1}".format(user.mention, issuer.mention))
            else:
                self.muted.append(user.id)
                pickle.dump(self.muted,path.open('wb'))
                await msg.channel.send( "{0} was muted by {1}".format(user.mention, issuer.mention))

            await user.add_roles(mute_role)

        elif command == 'unmute':
            if not msg.channel.permissions_for(issuer).manage_messages:
                await msg.channel.send( "You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0],msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            if user == issuer:
                await msg.channel.send( "You shouldn't be muted...")
                return

            mute_role = discord.utils.get(user.guild.roles, name="Muted")

            if user.id in self.muted:
                self.muted.remove(user.id)
                pickle.dump(self.muted,Path('muted.pkl').open('wb'))
                await msg.channel.send( "{0} was re-granted posting privileges by {1}".format(user.mention, issuer.mention))
            else:
                await msg.channel.send( "{0} was never muted.".format(user.mention))

            await user.remove_roles(mute_role)

        elif command == 'imgmute':
            if not msg.channel.permissions_for(issuer).manage_messages:
                await msg.channel.send( "You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0],msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            if user == issuer:
                await msg.channel.send( "You can't image mute yourself... No matter how much you probably should.")
                return

            path = Path('imgmuted.pkl')
            
            if path.exists():
                temp = pickle.load(path.open('rb'))
                if user.id in temp:
                    await msg.channel.send("{0} is already image muted".format(user.display_name))
                else:
                    self.imgmuted.append(user.id)
                    pickle.dump(self.imgmuted,path.open('wb'))
                    await msg.channel.send( "{0} was image muted by {1}".format(user.mention, issuer.mention))
            else:
                self.imgmuted.append(user.id)
                pickle.dump(self.imgmuted,path.open('wb'))
                await msg.channel.send( "{0} was image muted by {1}".format(user.mention, issuer.mention))

        elif command == 'imgunmute':
            if not msg.channel.permissions_for(issuer).manage_messages:
                await msg.channel.send( "You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0], msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            if user == issuer:
                await msg.channel.send( "You shouldn't be image muted...")
                return

            if user.id in self.imgmuted:
                self.imgmuted.remove(user.id)
                pickle.dump(self.imgmuted,Path('imgmuted.pkl').open('wb'))
                await msg.channel.send( "{0} was re-granted image posting privileges by {1}".format(user.mention, issuer.mention))
            else:
                await msg.channel.send( "{0} was never image muted.".format(user.mention))
            
        elif command == 'addrole':
            if not msg.channel.permissions_for(issuer).manage_roles:
                await msg.channel.send( "You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0], msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            role = next(r for r in self.server.roles if ' '.join(params[1:]).lower() == r.name.lower())

            if role is None:
                await msg.channel.send( "No role called {0}".format(params[1]))
            else:
                await user.add_roles(role)
                await msg.channel.send( "{0} was given the role {1} by {2}!".format(user.mention,role.name,issuer.mention))

        elif command == 'delrole':
            if not msg.channel.permissions_for(issuer).manage_roles:
                await msg.channel.send( "You don't have the proper permissions {}".format(issuer.mention))
                return

            user = await self.FindUser(params[0], msg)
            if user is None:
                await msg.channel.send( "No user with that name")
                return

            role = next(r for r in self.server.roles if ' '.join(params[1:]).lower() == r.name.lower())

            if role is None:
                await msg.channel.send( "No role called {0}".format(params[1]))
            else:
                await user.remove_roles(role)
                await msg.channel.send( "{0} was stripped of the role {1} by {2}.".format(user.mention,role.name,issuer.mention))

        elif command == 'selfie':
            selfie_channel = next(c for c in self.server.channels if 'selfies' in c.name.lower())
            logs = await selfie_channel.history(limit=2000).flatten()

            #async for m in selfie_channel.history(limit=2000):
            #    if len(m.attachments) > 0 and m.author == issuer:
            #        logs.append(m)

            pics = [m.attachments[0] for m in logs]
            if pics is None or len(pics) == 0:
                await msg.channel.send( "You don't have any selfies posted in {0}".format(selfie_channel.mention))

            pic = random.choice(pics)

            embed = discord.Embed(title="{0}'s selfie".format(issuer.display_name), description="Selfie Image")
            embed.set_image(url=pic['url'])
            embed.set_author(name=issuer.display_name)
            await msg.channel.send( embed=embed)

        elif command == 'ping':
            await msg.channel.send( "p-...pong?")

        elif command == 'dosed':
            if params[0] == 'start':
                if issuer.id in self.dosed.keys():
                    tm = self.dosed[issuer.id]['start_time']

                    tm = (datetime.datetime.fromtimestamp(tm) - datetime.timedelta(hours=5, minutes=0)).strftime('%I:%M:%S %p')
                    
                    await msg.channel.send( "You first dosed (issued this command) at {0}".format(tm))
                else:
                    await msg.channel.send( "You first dosed at... no, wait you didn't.")
                return
            elif params[0] == 'last':
                if issuer.id in self.dosed.keys():
                    if 'last_redose' not in self.dosed[issuer.id]:
                        await msg.channel.send( "You haven't told me you redosed")
                        return

                    tm = self.dosed[issuer.id]['last_redose']

                    tm = (datetime.datetime.fromtimestamp(tm) - datetime.timedelta(hours=5, minutes=0)).strftime('%I:%M:%S %p')
                    
                    await msg.channel.send( "You last re-dosed (issued the redose command) at {0}".format(tm))
                else:
                    await msg.channel.send( "You last re-dosed at... no, wait you didn't.")
                return
            drug = params[0].lower()
            dosage = ''.join(params[1:])

            if re.match('\d+([umk]?g)',dosage) is None:
                await msg.channel.send( "That dosage doesn't make sense to me...")
                return

            jsn = json.load(open('tripsit_drugs.json','r', encoding="utf8"))

            drugs = list(jsn['data'][0].keys())
            chosen_drug = None

            if drug not in drugs:
                #look through aliases
                for d in drugs:
                    if 'aliases' in jsn['data'][0][d]:
                        if drug in jsn['data'][0][d]['aliases']:
                            chosen_drug = d
            else:
                chosen_drug = next(d for d in drugs if d == drug)

            if chosen_drug == None:
                await msg.channel.send( "Couldn't find a drug by that name.")
                return

            if issuer.id in self.dosed:
                await msg.channel.send( "You're already listed as on something")
                return

            ch_nn = issuer.display_name + '/' + chosen_drug.capitalize() + '/' + dosage
            if len(ch_nn) > 32:
                to_rem = len(ch_nn)-32+1
                chosen_drug = chosen_drug[:-to_rem]+'.'

            self.dosed[issuer.id] = {'name': issuer.display_name, 'dname': ch_nn, 'dosage': dosage, 'start_time': time.time() }
            pickle.dump(self.dosed,Path('dosed.pkl').open('wb'))

            await issuer.edit(nick=self.dosed[issuer.id]['dname'])
            await msg.channel.send( "{0} is high on {1} ({2}). Be nice, and good vibes!".format(issuer.mention,drug.capitalize(),dosage))

        elif command == 'sober':
            if issuer.id not in self.dosed:
                await msg.channel.send( "You're not listed as a currently dosed user")
                return

            await issuer.edit(nick=self.dosed[issuer.id]['name'])
            await msg.channel.send( "{0} is now sober. Hope you had fun!".format(issuer.mention))
            del self.dosed[issuer.id]
            pickle.dump(self.dosed,Path('dosed.pkl').open('wb'))
        
        elif command == 'redose':
            if len(re.findall('\d+?([umk])?g', ''.join(params[0:]))) == 0:
                await msg.channel.send( "That dosage doesn't make sense to me...")
                return

            if issuer.id not in self.dosed:
                await msg.channel.send( "You never let me know you dosed anything... Try .help")
                return

            amount = int(re.findall(r'\d+', ''.join(params[0:]))[0])
            last_dosage = int(re.findall(r'\d+', self.dosed[issuer.id]['dosage'])[0])
            last_unit = re.findall(r'[^\d]+', self.dosed[issuer.id]['dosage'])[0]

            self.dosed[issuer.id]['last_redose'] = time.time()
            self.dosed[issuer.id]['dosage'] = str(last_dosage + amount) + last_unit
            self.dosed[issuer.id]['dname'] = self.dosed[issuer.id]['dname'].replace(str(last_dosage) + last_unit, self.dosed[issuer.id]['dosage'])
            
            await issuer.edit(nick=self.dosed[issuer.id]['dname'])
            await msg.channel.send( "{0} redosed for {1} for a total of {2}".format(issuer.display_name, ''.join(params[0:]), self.dosed[issuer.id]['dosage']))
            pickle.dump(self.dosed,Path('dosed.pkl').open('wb'))

        elif command == 'drug':
            drug = ''.join(params)

            res = urlopen('http://tripbot.tripsit.me/api/tripsit/getDrug?name={0}'.format(drug)).read()
            res = json.loads(res)

            if res['err'] == True:
                await msg.channel.send( "No drug found by that name")
            else:
                data = res['data'][0]
                embed = None
                if 'links' in data:
                    embed = discord.Embed(title=data['pretty_name'], description='[Drug information](http://drugs.tripsit.me/{0})\n[Experiences]({1})'.format(data['name'],data['links']['experiences']))
                else:
                    embed = discord.Embed(title=data['pretty_name'], description='[Drug information](http://drugs.tripsit.me/{0})\n[Experiences]({1})'.format(data['name'],"None Reported"))
                embed.add_field(name='Summary', value=data['properties']['summary'])
                if 'effects' in data['properties']:
                    embed.add_field(name='Effects', value=data['properties']['effects'], inline = False)
                embed.add_field(name='Onset', value=data['properties']['onset'], inline = False)
                embed.add_field(name='Duration', value=data['properties']['duration'], inline = False)
                embed.add_field(name='After Effects', value=data['properties']['after-effects'], inline = False)

                for roa in data['formatted_dose']:
                    value = ""
                    dos_cats = list(data['formatted_dose'][roa])
                    dos_vals = list(data['formatted_dose'][roa].values())

                    for i in range(len(dos_cats)):
                        value += "**{0}** - {1}\n".format(dos_cats[i], dos_vals[i])

                    embed.add_field(name='Dosage ({0})'.format(roa), value=value)
                
                embed.add_field(name='Categories', value="\n".join([string.capwords(c.replace('-',' ')) for c in data['properties']['categories']]), inline = False)

                await msg.channel.send( embed=embed)

        elif command == 'slap':
            slapee = await self.FindUser(' '.join(params[0:]),msg)

            im = Image.open('slap.gif')
            frames = []
            for frame in ImageSequence.Iterator(im):
                d = ImageDraw.Draw(frame)
                f = ImageFont.truetype('CODE2000.ttf',16)
                d.text((120,50), slapee.display_name, font=f)
                del d

                b = io.BytesIO()
                frame.save(b, format="GIF")
                frame = Image.open(b)
                frames.append(frame)

            frames[0].save('slap_out.gif', save_all=True, append_images=frames[1:])
            f = open('slap_out.gif','rb')
            await msg.channel.send("*slaps {0}*".format(slapee.mention),file=discord.File(f))
            f.close()
            im.close()
            os.remove('slap_out.gif')

        elif command == 'trivia':
            if self.in_trivia:
                if params[0].lower() == 'join':
                    if self.trivia_instance.initialized == True and self.trivia_instance.started == False:
                        if msg.author.id in self.trivia_instance.current_players:
                            await msg.channel.send( "You are already in this game, {0}".format(msg.author.mention))
                        else:
                            self.trivia_instance.addPlayer(msg.author.id) 
                            await msg.channel.send( "{0} added to the player list".format(msg.author.mention))
                        return
                elif params[0].lower() == 'end':
                    if msg.author == self.trivia_instance.host or msg.author.id == self.mouse_discord_id:
                        self.in_trivia = False
                        self.trivia_instance.End()
                        self.trivia_instance = None
                elif params[0].lower() == 'start':
                    if self.trivia_instance.initialized == True and self.trivia_instance.started == False:
                        if msg.author == self.trivia_instance.host:
                            self.trivia_instance.started = True
                            await msg.channel.send( "Starting {0} trivia game with {1} players! First one to {2} points wins!".format(self.trivia_instance.current_subject.capitalize(), len(self.trivia_instance.current_players),self.trivia_instance.max_score))
                            await asyncio.sleep(2)
                            await msg.channel.send( "TRIVIA QUESTION ({0})\n\n{1}".format(self.trivia_instance.current_subject,self.trivia_instance.current_question.question.capitalize()))
                        else:
                            await msg.channel.send( "You are not the host of this game, {0}. {1} is".format(msg.author.mention,self.trivia_instance.host.mention))

                    else:
                        await msg.channel.send( "Game of trivia already started and in progress...")

                    return

                else:
                    await msg.channel.send( "Trivia game is already in progress")
                return

            if params[0].lower() == 'subjects':
                subjects = [x.stem.capitalize() for x in Path('./trivia_questions/').iterdir() if x.is_file()]
                await msg.channel.send( "Trivia subjects\n============\n{0}".format("\n".join(subjects)))
                return
            elif params[0].lower() == 'highscores':
                ths = TriviaHighScoreTable()
                limit = 5
                ths.readFromFile()

                if len(params) == 2 and is_number(params[1]):
                    limit = int(params[1])

                top_5_msg = "TRIVIA HIGHSCORES (TOP {0})\n===================\n".format(str(limit))
                i = 1
                for entry, points in ths.players.items():
                    p = next(m for m in self.server.members if m.id == entry)
                    top_5_msg += "{0}.) {1} - {2}\n".format(str(i), p.display_name, p.mention)

                await msg.channel.send( top_5_msg)


            if len(params) == 2 and is_number(params[1]):
                self.trivia_instance = Trivia(params[0].lower(),int(params[1]))
                if len(self.trivia_instance.current_questions) == 0:
                    await msg.channel.send( "No trivia topic: {0}".format(params[0]))
                    self.trivia_instance = None
                else:
                    await msg.channel.send( "Trivia game with subject {0} initialized. Type '{1}trivia join' to enter! {1}trivia start to start (host only)".format(params[0], self.trigger))
                    self.in_trivia = True
                    self.trivia_instance.host = msg.author
                    self.trivia_instance.addPlayer(msg.author.id)

        elif command == 'whohas':
            role = next(r for r in self.server.roles if ' '.join(params[0:]).lower() == r.name.lower())

            people = filter(lambda m: role in m.roles, self.server.members)
            people = list(people)
            await msg.channel.send( ', '.join([m.display_name for m in people]))
            pass

        elif command == 'help':
            help_message = ""
            for k in self.commands.keys():
                help_message += k + " - " + self.commands[k] + "\n"
            await msg.channel.send( help_message)

#Helper Methods
#region
    @asyncio.coroutine
    def get_user_from_list(self,users : list, msg : discord.Message) -> discord.User:
        ask_list = "Which one?\n"
        i = 1
        for user in users:
            ask_list += "{0}.) {1}\n".format(i, user.display_name)
            i+=1
        
        yield from msg.channel.send( ask_list)
        resp = yield from self.wait_for('message',check=lambda m : m.author == msg.author and m.channel == msg.channel and m.content.isdigit() and 0 <= int(m.content)-1 <= (len(users)-1), timeout=5)

        chosen_ind = int(resp.content)-1
        
        return users[chosen_ind]

    @asyncio.coroutine
    def FindUser(self,name,msg : discord.Message,id = False) -> discord.User:
        if not id:
            if name.startswith('<@'):
                return next(m for m in self.server.members if name == m.mention)
            else:
                users = [m for m in self.server.members if (str.lower(name) in str.lower(m.display_name) or str.lower(name) in str.lower(m.name)) and m.display_name != 'Ketamouse']
                if len(users) == 0:
                    return None
                elif len(users) == 1:
                    return users[0]
                
                u = yield from self.get_user_from_list(users,msg)
                return u
        else:
            return self.fetch_user(name)

    @asyncio.coroutine
    def check_yes_no(self, message: discord.Message):
        if re.search('y[e|a]?s?', message.content.lower()) is not None \
                or re.search('n(o|ah)?', message.content.lower()):
            return True
        return False
#endregion

client = LabRatBot()
client.run('MzgxMjMzMDQzNjM1MDQ0MzUy.DPELiw.wpRRJul1-5dSo9DYWiya8lTUPvo')
