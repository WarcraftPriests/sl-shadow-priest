import pandas
import operator
import yaml
import os
import json
import time

from internal.weights import find_weights
from internal.spell_ids import find_ids

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def assure_path_exists(path):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def build_output_string(sim_type, talent_string, file_type):
    output_dir = "results/"
    assure_path_exists(output_dir)
    return "{0}Results_{1}{2}.{3}".format(output_dir, sim_type, talent_string, file_type)


def get_change(current, previous):
    negative = 0
    if current < previous:
        negative = True
    try:
        value = (abs(current - previous) / previous) * 100.0
        value = float('%.2f' % value)
        if value >= 0.01 and negative:
            value = value * -1
        return value
    except ZeroDivisionError:
        return 0


def find_weight(sim_type, profile_name):
    weight_type = ""
    if sim_type == "Composite":
        weight_type = "compositeWeights"
    elif sim_type == "Single":
        weight_type = "singleTargetWeights"
    elif sim_type == "Dungeons":
        # Dungeon sim is just 1 sim, so we return 1 here
        return 1
    weight = find_weights(config[weight_type]).get(profile_name)
    if not weight:
        return 0
    else:
        return weight


def build_results(data, weights, sim_type, directory):
    results = {}
    for value in data.iterrows():
        profile = value[1].profile
        actor = value[1].actor
        fight_style = profile[profile.index('_') + 1:]
        weight = find_weight(sim_type, fight_style)
        weighted_dps = value[1].DPS * weight
        if weights:
            intellect = value[1].int * weight
            haste = value[1].haste / intellect * weight
            crit = value[1].crit / intellect * weight
            mastery = value[1].mastery / intellect * weight
            vers = value[1].vers / intellect * weight
            wdps = 1 / intellect * weight
            weight = 1 * weight
            if actor in results:
                existing = results[actor]
                results[actor] = [existing[0] + weighted_dps, existing[1] + weight, existing[2] + haste,
                                  existing[3] + crit, existing[4] + mastery, existing[5] + vers,
                                  existing[6] + wdps]
            else:
                results[actor] = [weighted_dps, weight, haste, crit, mastery, vers, wdps]
        else:
            if actor in results:
                results[actor] = results[actor] + weighted_dps
            else:
                results[actor] = weighted_dps
    # Each profile sims "Base" again so we need to divide that to get the real average
    number_of_profiles = len(config["sims"][directory[:-1]]["files"])
    base_dps = results.get('Base') / number_of_profiles
    results['Base'] = base_dps
    return results


def build_markdown(sim_type, talent_string, results, weights, base_dps):
    output_file = build_output_string(sim_type, talent_string, "md")
    with open(output_file, 'w+') as results_md:
        if weights:
            results_md.write(
                '# {0}\n| Actor | DPS | Int | Haste | Crit | Mastery | Vers | DPS Weight '
                '|\n|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n'.format(sim_type))
            for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                results_md.write("|%s|%.0f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|\n" % (
                    key, value[0], value[1], value[2], value[3], value[4], value[5], value[6]))
        else:
            results_md.write('# {0}\n| Actor | DPS | Increase |\n|---|:---:|:---:|\n'.format(sim_type))
            for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                results_md.write("|%s|%.0f|%.2f%%|\n" % (key, value, get_change(value, base_dps)))


def build_csv(sim_type, talent_string, results, weights, base_dps):
    output_file = build_output_string(sim_type, talent_string, "csv")
    with open(output_file, 'w') as results_csv:
        if weights:
            results_csv.write('profile,actor,DPS,int,haste,crit,mastery,vers,dpsW,\n')
            for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                results_csv.write("%s,%s,%.0f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,\n" % (
                    sim_type, key, value[0], value[1], value[2], value[3], value[4], value[5], value[6]))
        else:
            results_csv.write('profile,actor,DPS,increase,\n')
            for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                results_csv.write("%s,%s,%.0f,%.2f%%,\n" % (sim_type, key, value, get_change(value, base_dps)))


def lookup_id(name, directory):
    lookup_type = config["sims"][directory[:-1]]["lookupType"]
    if lookup_type == "spell":
        return lookup_spell_id(name, directory)
    elif lookup_type == "item":
        return lookup_item_id(name, directory)
    else:
        return None


def lookup_spell_id(spell_name, directory):
    ids = find_ids(directory[:-1])
    if ids:
        return ids[spell_name]
    else:
        return None


def lookup_item_id(item_name, directory):
    # get the list of sim files from config
    # loop over them and search for the item name line by line
    for sim_file in config["sims"][directory[:-1]]["files"]:
        with open(sim_file, 'r') as file:
            for line in file:
                if item_name in line:
                    # find ,id= -> take 2nd half ->
                    # find , -> take 1st half
                    return int(line.split(',id=')[1].split(',')[0])


def build_json(sim_type, talent_string, results, directory, timestamp):
    output_file = build_output_string(sim_type, talent_string, "json")
    human_date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
    chart_data = {
        "data": {},
        "ids": {},
        "simulated_steps": [],
        "sorted_data_keys": [],
        "last_updated": human_date
    }
    # check steps in config
    # for each profile, try to find every step
    # if found put in unique dict
    steps = config["sims"][directory[:-1]]["steps"]
    number_of_steps = len(steps)

    # if there is only 1 step, we can just go right to iterating
    if number_of_steps == 1:
        chart_data["simulated_steps"] = ["DPS"]
        for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
            chart_data["data"][key] = {
                "DPS": int(round(value, 0))
            }
            if key != "Base":
                chart_data["sorted_data_keys"].append(key)
                chart_data["ids"][key] = lookup_id(key, directory)
    else:
        unique_profiles = []
        chart_data["simulated_steps"] = steps
        # iterate over results and build a list of unique profiles
        # trim off everything after last _
        for key, value in results.items():
            unique_key = '_'.join(key.split('_')[:-1])
            if unique_key not in unique_profiles and unique_key != "Base" and unique_key != "":
                unique_profiles.append(unique_key)
                chart_data["sorted_data_keys"].append(unique_key)
                chart_data["ids"][unique_key] = lookup_id(unique_key, directory)
        for profile in unique_profiles:
            chart_data["data"][profile] = {}
            for step in steps:
                for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                    # split off the key to get the step
                    # key: Trinket_415 would turn into 415
                    key_step = key.split('_')[len(key.split('_')) - 1]
                    if profile in key and str(key_step) == str(step):
                        chart_data["data"][profile][step] = int(round(value, 0))
    json_data = json.dumps(chart_data)
    with open(output_file, 'w') as results_json:
        results_json.write(json_data)


def analyze(talents, directory, dungeons, weights, timestamp):
    os.chdir("..")
    csv = "output/statweights.csv".format(directory)
    if weights:
        data = pandas.read_csv(csv,
                               usecols=['profile', 'actor', 'DD', 'DPS', 'int', 'haste', 'crit', 'mastery', 'vers'])
    else:
        data = pandas.read_csv(csv, usecols=['profile', 'actor', 'DD', 'DPS'])

    talent_string = "_{0}".format(talents) if talents else ""
    sim_types = ["Dungeons"] if dungeons else ["Composite", "Single"]

    for sim_type in sim_types:
        results = build_results(data, weights, sim_type, directory)
        base_dps = results.get('Base')
        if config["analyze"]["markdown"]:
            build_markdown(sim_type, talent_string, results, weights, base_dps)
        if config["analyze"]["csv"]:
            build_csv(sim_type, talent_string, results, weights, base_dps)
        if config["analyze"]["json"]:
            build_json(sim_type, talent_string, results, directory, timestamp)
