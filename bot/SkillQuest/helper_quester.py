import glob
import os
import random
import json
import math


def load_json(game):
    with open(f'quests/{game}/quests.json', 'r') as f:
        data = json.load(f)
    data = dict((k.lower(), v) for k,v in data.items())
    return data

def get_quests(game):
    data = load_json(game)
    return data.keys()

def get_data_for_quest(quest, game):
    data = load_json(game)
    return data[quest]['price'] * 1000000
    
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])


def load_abbreviations(game):
    with open(f'quests/{game}/abbreviations.json', 'r') as f:
        data = json.load(f)
    data = dict((k, v.lower()) for k,v in data.items())
    return data

def format_content(data):
    rc = ''
    for values in data:
        rc += f"**Account Type: ** {values['type'].capitalize()} \n"
        rc += f"**Price: **{values['price']}\n"
        if values['notes'] != "":
            rc += f"**Notes: ** {values['notes'].capitalize()} \n\n"
        else:
            rc += "\n"
    print(rc)
    return rc