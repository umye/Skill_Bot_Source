#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
import os
import re
import asyncio
import datetime 
import helper_skillcalc as hsc
import helper_quester as h
import helper_minigames as hm
import difflib
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='!')
client.remove_command('help')


@client.command()
async def help(ctx, arg=None):
    if not arg:
        # GENERIC
        embed = discord.Embed(title="Available Help Commands", description="```diff\n!help minigame :: Shows the usage of minigames\n!help skills :: Shows the usage for skills\n!help quests - Shows the usage of quests \n```", color=0x800000)
        await ctx.send(embed=embed)
        return
    arg = arg.lower()
    if arg == "minigame":
        desc = ""
        minigames = hm.get_all_minigames()
        for mini in minigames:
            data = hm.load_minigame(mini)
            name = data['name']
            emoji = data['emoji']
            code = mini
            desc += f"{emoji} {name}: `{code}`\n"
        desc += ":information_source: **How to check prices?**\n ‎"
        desc += f"```diff\n Command :: !minigame minigamecode quantity\n Example :: !minigame ba 2 \n```"
        embed = discord.Embed(title="Available Minigames", description=desc, color=0x800000)
        strings = [f'Requested by ', f'{ctx.message.author.name}', f'#', f'{ctx.message.author.discriminator}']
        footer = '‎'.join(strings)
        embed.set_footer(text=footer, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
    elif arg == "skills":
        strings = [f'Requested by ', f'{ctx.message.author.name}', f'#', f'{ctx.message.author.discriminator}']
        footer = '‎'.join(strings)
        skills = hsc.get_tracked_skills("07")
        images = hsc.get_images_for_skills("07")
        embed = discord.Embed(color=0x800000)
        embed.set_author(name = "Skill Help", icon_url="https://i.imgur.com/IXUHdP2.png")
        embed.add_field(name=f'‎Command List \n‎', value=f'`!agility 1-99`\n`!construction 1-99`\n`!cooking 1-99`\n`!crafting 1-99`\n`!farming 1-99`\n`!firemaking 1-99`\n`!fishing 1-99`\n`!herblore 1-99`\n`!hunter 1-99`\n`!mining 1-99`\n`!melee 1-99`\n`!prayer 1-99`\n`!runecraft 1-99`\n`!slayer 1-99`\n`!smithing 1-99`\n`!thieving 1-99`\n`!woodcutting 1-99`\n ‎', inline=False)
        embed.set_footer(text=footer, icon_url=ctx.author.avatar_url)
        # for skill in skills:
            # embed.add_field(name=f'!{skill}', value=f'Calculate the cost of {skill} level', inline=True)
        await ctx.send(embed=embed)
    elif arg == "quests":
        embed = discord.Embed(description=f'Type multiple quests to receive an estimate. \n Quest spellings are based off of the [Official Wiki](https://oldschool.runescape.wiki/w/Quests/List).\n ‎', color=0x800000)
        embed.set_author(name = "Quest Help", icon_url="https://i.imgur.com/qwwvPa1.png")
        embed.add_field(name=f'Example Usage', value=f'`!quests dragon slayer 2, cooks assistant`\n`!quests ds2, mm2, bone voyage`\n ‎', inline=False)
        strings = [f'Requested by ', f'{ctx.message.author.name}', f'#', f'{ctx.message.author.discriminator}']
        footer = '‎'.join(strings)
        embed.set_footer(text=footer, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@client.event
async def on_ready():
    print(f'{client.user} is connected.')

@client.command()
async def minigame(ctx, mgame, kc = 1):
    minigames  = hm.get_all_minigames()
    print(minigames)
    mgame = mgame.lower()
    if mgame not in minigames:
        print(minigames)
        return
    data = hm.load_minigame(mgame)

    desc_item = ""
    desc_prices = ""
    for _item in data['prices']:
        item = _item['item']
        emoji = _item['emoji']
        price = _item['price']
        desc_item += f"{emoji} {item}\n"
        desc_prices += f"`{h.human_format(price * kc)}` <:gp:829007550359011378>\n"
    embed = discord.Embed(title=f'Minigame Calculator', description=f'Pricing for {data["name"]} for `{kc}` killcount', color=0x800000)
    embed.add_field(name="Item", value=desc_item, inline=True)
    embed.add_field(name="Pricing", value=desc_prices, inline=True)
    await ctx.send(embed=embed)


@client.command()
async def quests(ctx, *args):
    message = ' '.join(args)
    requested_quests = [m.lstrip().rstrip() for m in message.split(',')]
    all_quests = h.get_quests("07")
    abbv = h.load_abbreviations("07")
    not_found = []
    found = []
    total = 0
    desc_found = ""
    desc_not_found = ""
    for quest_name in requested_quests:
        quest = quest_name.lower()
        if quest_name in abbv:
            quest = f'{abbv[quest_name].lower()}'
        if quest in all_quests:
            total += h.get_data_for_quest(quest, "07")
            found.append(quest_name)
            desc_found += f"• {quest_name} | `{h.human_format(h.get_data_for_quest(quest, '07'))}` <:gp:829007550359011378>\n"
        else:
            not_found.append(quest_name)
    str_not_found = ''
    for nf in not_found:
        possbile_matches = difflib.get_close_matches(nf, all_quests)
        possbile_matches_str = f"**{nf}**: {','.join(possbile_matches)}\n"
        str_not_found += possbile_matches_str
    # str_found = f"**Total**: {hsc.human_format(total)}\n**For Quests:** {', '.join(found)}"
    str_found = desc_found
    if str_found == "":
        str_found = "Quests not found"
    embed = discord.Embed(title=f'Quest Calculator', description=f'Total: `{h.human_format(total)}` <:gp:829007550359011378>', color=0x800000)
    embed.add_field(name="Individual Prices", value=str_found, inline=False)
    strings = [f'Requested by ', f'{ctx.message.author.name}', f'#', f'{ctx.message.author.discriminator}']
    footer = '‎'.join(strings)
    embed.set_footer(text=footer, icon_url=ctx.author.avatar_url)
    if str_not_found != '':
        embed.add_field(name="Not Found - Did you mean?", value=str_not_found, inline=False)
        strings = [f'Requested by ', f'{ctx.message.author.name}', f'#', f'{ctx.message.author.discriminator}']
        footer = '‎'.join(strings)
        embed.set_footer(text=footer, icon_url=ctx.author.avatar_url)    
    await ctx.send(embed=embed)
@client.event
async def on_message(message):
    if message.author == client.user or message.content[0] not in ['!', '.']:
        return

    commands = [f'!{c.name}' for c in client.commands]
    cmd = message.content.split(' ')[0]
    if cmd in commands:
        await client.process_commands(message)
        return
    isSkill = hsc.is_message_skill(message.content.split(' ')[0][1:], "07")
    if isSkill:
        skills = hsc.get_tracked_skills("07")
        images = hsc.get_images_for_skills("07")
        for skill in skills:
            if f'!{skill}' == message.content.split(' ')[0]:
                try:
                    is_skill = True
                    header, rc, mintotal = hsc.parse(message.content, skill, "07") 
                    embed = discord.Embed(title=f"{skill.capitalize()} Calculator", description=f'{header}', color=0x800000)
                    desc = ''
                    for value in rc:
                        fromto = value.split("\n")[0]
                        other = "\n".join(value.split("\n")[1:])
                        desc += f"{fromto}{other}\n"
                    desc += "\n-------------------\n"
                    desc += mintotal

                    embed.add_field(name=f"Prices", value=f'{desc}', inline=False)
                    embed.set_author(name = skill.capitalize(), icon_url=images[skill])
                    # embed.set_footer(text=f"{mintotal}", icon_url=images[skill])
                    await message.channel.send(embed=embed)
                except ValueError as e:
                    embed = discord.Embed(title=f'Let me help you', description=f'**Example;** if you want a OSRS quote for 45-70 hunter.\n**!hunter 45-70**\n*mind the spaces! :)*', color=0x800000)
                    embed.set_author(name = "Help", icon_url=images['help'])
                    await message.channel.send(embed=embed)




client.run(TOKEN)
