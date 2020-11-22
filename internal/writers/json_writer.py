'JSON (.json) file writer'
import re
import json
import time
import operator
from datetime import datetime

import pandas

from internal.config import config
from internal.writers.common import (
    build_output_string, generate_report_name, lookup_id, convert_increase_to_double)


def build_json(sim_type, talent_string, results, base_path, directory, timestamp, covenant_string):
    # pylint: disable=too-many-arguments, disable=too-many-locals
    """build json from results"""
    output_file = build_output_string(base_path,
        sim_type, talent_string, covenant_string, "json")
    human_date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
    chart_data = {
        "name": generate_report_name(sim_type, talent_string, covenant_string),
        "data": {},
        "ids": {},
        "simulated_steps": [],
        "sorted_data_keys": [],
        "last_updated": human_date
    }
    # check steps in config
    # for each profile, try to find every step
    # if found put in unique dict
    steps = config["sims"][directory]["steps"]
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
        for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
            unique_key = '_'.join(key.split('_')[:-1])
            if unique_key not in unique_profiles and unique_key != "Base" and unique_key != "":
                unique_profiles.append(unique_key)
                chart_data["sorted_data_keys"].append(unique_key)
                chart_data["ids"][unique_key] = lookup_id(
                    unique_key, directory)
        for profile in unique_profiles:
            chart_data["data"][profile] = {}
            steps.sort(reverse=True)
            # Make sure that the steps in the json are from highest to lowest
            for step in steps:
                for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                    # split off the key to get the step
                    # key: Trinket_415 would turn into 415
                    key_step = key.split('_')[len(key.split('_')) - 1]
                    if profile in key and str(key_step) == str(step):
                        chart_data["data"][profile][step] = int(
                            round(value, 0))
        # Base isn't in unique_profiles so we handle that explicitly
        chart_data["data"]["Base"] = {}
        chart_data["data"]["Base"]["DPS"] = int(round(results.get("Base"), 0))
    json_data = json.dumps(chart_data)
    with open(output_file, 'w') as results_json:
        results_json.write(json_data)


def build_covenant_json():
    """build aggregated covenant json"""
    sim_types = ["Composite", "Dungeons", "Single"]
    talents = config["builds"].keys()
    results = {}
    # find the 3 JSON entries for each talent setup
    for sim_type in sim_types:
        covenants = {
            "kyrian": {"max": 0.00, "min": 0.00},
            "necrolord": {"max": 0.00, "min": 0.00},
            "night_fae": {"max": 0.00, "min": 0.00},
            "venthyr": {"max": 0.00, "min": 0.00}
        }
        # loop over config["builds"] to get each set of covenant{} data
        for talent in talents:
            input_file = "results/Results_Aggregate_{0}.json".format(talent)
            with open(input_file) as data:
                talent_data = json.load(data)
            covenant_data = talent_data['data'][sim_type.lower()]
            # for each set of covenant{} data populate new dict with min/max
            for covenant in covenants:
                if covenants[covenant]["max"]:
                    covenants[covenant]["max"] = max(
                        covenant_data[covenant]["max"], covenants[covenant]["max"])
                else:
                    covenants[covenant]["max"] = covenant_data[covenant]["max"]

                if covenants[covenant]["min"]:
                    covenants[covenant]["min"] = min(
                        covenant_data[covenant]["min"], covenants[covenant]["min"])
                else:
                    covenants[covenant]["min"] = covenant_data[covenant]["min"]
        # output 1 JSON file as Results_Aggregate.json
        results[sim_type.lower()] = covenants
    chart_data = {
        "name": "Aggregate",
        "data": results,
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }
    json_data = json.dumps(chart_data)
    output_file = "results/Results_Aggregate.json"
    with open(output_file, 'w') as results_json:
        results_json.write(json_data)


def build_talented_covenant_json(talents):
    """build aggregated talented covenant json file"""
    sim_types = ["Composite", "Dungeons", "Single"]
    results = {}
    # find the 3 CSV files for the given talent setup
    for sim_type in sim_types:
        csv = "results/Results_{0}_{1}.csv".format(sim_type, talents)
        data = pandas.read_csv(
            csv, usecols=['profile', 'actor', 'DPS', 'increase'])
        covenants = {
            "kyrian": {"max": 0.00, "min": 0.00},
            "necrolord": {"max": 0.00, "min": 0.00},
            "night_fae": {"max": 0.00, "min": 0.00},
            "venthyr": {"max": 0.00, "min": 0.00},
            "base": {"DPS": 0.00}
        }
        # for each file, iterate over results to get max/min per covenant
        for value in data.iterrows():
            covenant = re.sub(r"_\d+", "", value[1].actor).lower()
            covenant_dict = covenants.get(covenant)
            if covenant == "base":
                covenants["base"]["DPS"] = convert_increase_to_double(
                    value[1].increase)
            elif covenant_dict:
                if covenant_dict["max"]:
                    covenant_dict["max"] = max(
                        convert_increase_to_double(value[1].increase), covenant_dict.get("max"))
                else:
                    covenant_dict["max"] = convert_increase_to_double(
                        value[1].increase)

                if covenant_dict["min"]:
                    covenant_dict["min"] = min(
                        convert_increase_to_double(value[1].increase), covenant_dict.get("min"))
                else:
                    covenant_dict["min"] = convert_increase_to_double(
                        value[1].increase)
        # use that data to build out the sim_type data block by covenant
        results[sim_type.lower()] = covenants
    # output 1 JSON file per talent setup as Results_Aggregate_am-as.json
    chart_data = {
        "name": "Aggregate {0}".format(talents),
        "data": results,
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }
    json_data = json.dumps(chart_data)
    output_file = "results/Results_Aggregate_{0}.json".format(talents)
    with open(output_file, 'w') as results_json:
        results_json.write(json_data)
