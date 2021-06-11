#!/usr/bin/env python3
import glob
import os
import random
import json
import math
import itertools
import datetime 

def get_all_minigames():
    skills = []
    for file in glob.glob(f"minigames/*.json"):
        skills.append(os.path.basename(file).replace('.json',''))
    return skills

def load_minigame(mini):
    with open(f'minigames/{mini}.json', 'r') as f:
        data = json.load(f)
    return data

