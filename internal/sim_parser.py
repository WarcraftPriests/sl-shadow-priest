"""parses a simc output file into a single csv file"""
import os
import json
from os import path

from internal import utils


def parse(filename, weights):
    """parse the given sim file"""
    separator = ','
    ret = ''
    with open(filename, "r") as file:
        data = file.read()
        sim = json.loads(data)
        print("Parsing: " + filename)
        if 'error' in sim:
            print("ERROR: {0} contains a sim error - cannot parse.\n{1}".format(
                filename, sim['error']))
            raise RuntimeError from OSError
        results = sim['sim']['players']
        for player in sorted(results, key=lambda k: k['name']):
            if not weights or 'Int' in player['scale_factors']:
                ret += path.splitext(os.path.basename(filename))[0] + separator
                ret += player['name'] + separator
                ret += '{0:.{1}f}'.format(player['collected_data']
                                          ['dmg']['mean'], 0) + separator
                ret += '{0:.{1}f}'.format(player['collected_data']
                                          ['dps']['mean'], 0) + separator
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
    """parse the given file if it contains profilesets"""
    if weights:
        print("ERROR: Cannot sim weights with profilesets.")
    separator = ','
    ret = ''
    with open(filename, "r") as file:
        data = file.read()
        sim = json.loads(data)
        results = sim['sim']['profilesets']['results']
        for profile in sorted(results, key=lambda k: k['name']):
            ret += path.splitext(os.path.basename(filename))[0] + separator
            ret += profile['name'] + separator
            ret += '{0:.{1}f}'.format(0, 0) + separator
            ret += '{0:.{1}f}'.format(profile['mean'], 0) + separator
            ret += '\n'
    return ret


def parse_json(directory, weights):
    """parse json files"""
    headers = ['profile','actor','DD','DPS']
    if weights:
        headers += ['int','haste','crit','mastery','vers']
    parses = ','.join(headers) + '\n'

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            parses += parse(os.path.join(directory, filename), weights)

    with open(os.path.join(directory, "statweights.csv"), "w") as ofile:
        ofile.write(parses)


def get_timestamp(directory, talent, covenant):
    """get timestamp the sim was run"""
    full_path = os.path.join(directory, utils.get_simc_dir(talent, covenant, 'output'))
    for filename in os.listdir(full_path):
        if filename.endswith('.json'):
            with open(os.path.join(full_path, filename), "r") as file:
                data = file.read()
                sim = json.loads(data)
                timestamp = sim['timestamp']
                return timestamp
    return "unknown"
