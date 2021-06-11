#!/usr/bin/env python3
import glob
import os
import random
import json
import math
import itertools
import networkx as nx
import logging
import logging.handlers
import datetime 

# log_file = datetime.datetime.now().strftime('AgileSkillCalc_%Y_%m_%d_%H_%M.log')
# logger = logging.getLogger(__name__)
# handler = logging.handlers.WatchedFileHandler(
#     os.environ.get("LOGFILE", f'logs/{log_file}'))
# formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# handler.setFormatter(formatter)
# root = logging.getLogger()
# root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
# root.addHandler(handler)

def is_message_skill(message, game):
    if message in get_tracked_skills(game):
        return True
    return False

def get_tracked_skills(game):
    skills = []
    for file in glob.glob(f"skills/{game}/*.json"):
        skills.append(os.path.basename(file).replace('.json',''))
    return skills

def load_skills(skill, game):
    with open(f'skills/{game}/{skill}.json', 'r') as f:
        data = json.load(f)
    return data

def get_images_for_skills(game):
    images = {}
    images['help'] = "https://i.imgur.com/EWcW0kW.png"

    tracked_skills = get_tracked_skills(game)
    for sk in tracked_skills:
        data = load_skills(sk, game)
        images[sk] = data['image']
    
    return images

def get_xp_for_target_level(target):
    points = 0
    for level in range(1,120):
        diff = int(level + 300 * math.pow(2, float(level)/7) )
        points += diff
        if target == level+1:
            return int(points/4)
    return 0

def is_request_skill(message):
    if len(message) != 2:
        return False
    return True

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

def breakout(checkpoints, start_level, end_level):
    res = []
    prev = 0
    for c in checkpoints:
        if c > start_level and c < end_level:
            res.append(f'{start_level}-{c}')
            res.append(f'{c}-{end_level}')
            if prev != 0:
                res.append(f'{prev}-{c}')
            prev = c
    return res if len(res) > 0 else [f'{start_level}-{end_level}']

def get_price_breakdown(data, start_level, end_level):
    prices = data['prices']
    quote = []
    for p in prices:
        sl = int(p['start_level'])
        el = int(p['end_level'])
        method = p['notes']
        gp_xp = int(p['gp/xp'])
        if sl >= end_level or el <= start_level:
            continue
        if end_level < el:
            el = end_level
        start_xp = get_xp_for_target_level(max(sl, start_level))
        end_xp = get_xp_for_target_level(min(el, end_level))
        xp_diff = end_xp - start_xp
        cost = human_format(xp_diff * gp_xp)
        temp = f"<:skill:829007583276171367> [`{sl}-{el}`] {method} - <:gp:829007550359011378> `{human_format(xp_diff * gp_xp)}`"
        # temp = f"**{max(sl, start_level)} - {min(el, end_level)}**\n**Cost: **{cost}\n**Method: **{method}"
        quote.append(temp)
    return quote

def parse(content, skill, game):
    if game == "07":
        levels = content.strip('!' + skill).lstrip().split('-')
        if len(levels) > 2 or any([len(txt)>2 for txt in levels]) or all([isinstance(txt, int) and int(txt)>0 and int(txt) <=99 for txt in levels]):
            return "","Invalid input"
        start_level = int(levels[0])
        end_level = int(levels[1])
        if start_level >= end_level or start_level <= 0 or end_level > 99:
            return "","Start level cannot be: \n1. greater than or equal to end level.\n2. less than or equal to 0"
    if game == "rs3":
        levels = content.strip('+' + skill).lstrip().split('-')
        if len(levels) > 2 or any([len(txt)>3 for txt in levels]) or all([isinstance(txt, int) and int(txt)>0 and int(txt) <=120 for txt in levels]):
            return "","Invalid input"
        start_level = int(levels[0])
        end_level = int(levels[1])
        if start_level >= end_level or start_level <= 0 or end_level > 120:
            return "","Start level cannot be: \n1. greater than or equal to end level.\n2. less than or equal to 0"  
    
    data = load_skills(skill, game)
    # header = f"**Start Level:** {start_level} \n**End Level:** {end_level}"
    quote = get_price_breakdown(data, start_level, end_level)
    mintotal = f"\nMinimum Total-  <:gp:829007550359011378> `{get_min_price(data, start_level, end_level)}`"
    # mintotal = 0
    header = f"Training from `{start_level}` to `{end_level}` requires `{human_format(get_xp_for_target_level(end_level) - get_xp_for_target_level(start_level))}` experience. \n"

    # print(f"{header}\n{quote}\n{mintotal}")
    return header, quote, mintotal


def get_results(data, start, end):
    # print(data)
    G = nx.DiGraph()
    for key, weight in data.items():
        src_str, dest_str = key.split('-')
        src_idx, dest_idx = int(src_str), int(dest_str)
        G.add_edge(src_idx, dest_idx, weight=weight)

    all_paths = list(nx.all_simple_paths(G, 
                                        source=start, 
                                        target=end))
    distances = [sum(G.get_edge_data(s,d)['weight'] for s,d in zip(p,p[1:])) 
                for p in all_paths]


    results = {tuple(p):d for p,d in zip(all_paths,distances)}
    return results

def get_min_price(data, start_level, end_level):
    price_dict = {}
    prices = data['prices']
    checkpoints = data['checkpoints']
    sub_levels = breakout(checkpoints, start_level, end_level)
    for c in sub_levels:
        lvl = c.split('-')
        sl = int(lvl[0])
        el = int(lvl[1])
        xp_diff = get_xp_for_target_level(el) - get_xp_for_target_level(sl)
        for price in prices:
            json_start_level = int(price['start_level'])
            json_end_level = int(price['end_level'])
            if json_start_level > el or json_start_level > sl:
                continue
            if sl < json_end_level:
                json_gp_xp = int(price['gp/xp'])
                key = f'{sl}-{el}'
                if key in price_dict:
                    price_dict[key] = min(price_dict[key] ,xp_diff * json_gp_xp)
                else:
                    price_dict[key] = xp_diff * json_gp_xp 
    value = get_results(price_dict, start_level, end_level)
    min_price = human_format(int(min(value.values())))
    return min_price