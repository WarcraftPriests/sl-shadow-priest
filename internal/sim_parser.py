import os
import json
from os import path

def parse(filename, weights):
    separator = ','
    ret = ''
    with open(filename, "r") as f:
        s = f.read()
        sim = json.loads(s)
        results = sim['sim']['players']
        for player in sorted(results, key=lambda k: k['name']):
            if not weights or 'Int' in player['scale_factors']:
                ret += path.splitext(filename)[0] + separator
                ret += player['name'] + separator
                ret += '{0:.{1}f}'.format(player['collected_data']['dmg']['mean'], 0) + separator
                ret += '{0:.{1}f}'.format(player['collected_data']['dps']['mean'], 0) + separator
                if weights:
                    weight = player['scale_factors']
                    stats = ['Int', 'Haste', 'Crit', 'Mastery', 'Vers']
                    for stat in stats:
                        ret += '{0:.{1}f}'.format(weight[stat], 2) + separator
                ret += '\n'
    if 'profilesets' in sim['sim']:
        ret += parse_profile_sets(filename, weights)
    return ret


def parse_profile_sets(filename, weights):
    if weights:
        print("ERROR: you selected to sim with weights, but you cannot sim weights with profilesets.")
    separator = ','
    ret = ''
    with open(filename, "r") as f:
        s = f.read()
        sim = json.loads(s)
        results = sim['sim']['profilesets']['results']
        for profile in sorted(results, key=lambda k: k['name']):
            ret += path.splitext(filename)[0] + separator
            ret += profile['name'] + separator
            ret += '{0:.{1}f}'.format(0, 0) + separator
            ret += '{0:.{1}f}'.format(profile['mean'], 0) + separator
            ret += '\n'
    return ret


def parse_json(directory, weights):
    os.chdir(directory)
    parses = 'profile,actor,DD,DPS'
    if weights:
        parses += 'int,haste,crit,mastery,vers'
    parses += '\n'
    for filename in os.listdir(os.getcwd()):
        if filename.endswith('.json'):
            parses += parse(filename, weights)
    with open("statweights.csv", "w") as ofile:
        print(parses, file=ofile)


def get_timestamp():
    for filename in os.listdir(os.getcwd()):
        if filename.endswith('.json'):
            with open(filename, "r") as f:
                s = f.read()
                sim = json.loads(s)
                timestamp = sim['timestamp']
                return timestamp
