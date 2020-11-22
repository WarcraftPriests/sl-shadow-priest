"""creates results files from sim results"""

import re
import os
import pandas

from internal import utils
from internal.config import config
from internal.writers.common import find_weight
from internal.writers.csv_writer import build_csv
from internal.writers.json_writer import (
    build_json, build_covenant_json, build_talented_covenant_json)
from internal.writers.markdown_writer import build_markdown


def build_results(data, weights, sim_type, directory):
    # pylint: disable=too-many-locals
    """create results dict from sim data"""
    results = {}
    for value in data.iterrows():
        actor = value[1].actor
        fight_style = re.search(
            '((hm|lm|pw).*|dungeons$)', value[1].profile).group()
        weight = find_weight(sim_type, fight_style)
        weighted_dps = value[1].DPS * weight
        if weights:
            intellect = value[1].int
            haste = value[1].haste / intellect * weight
            crit = value[1].crit / intellect * weight
            mastery = value[1].mastery / intellect * weight
            vers = value[1].vers / intellect * weight
            wdps = 1 / intellect * weight
            existing = results.get(actor, {})
            results[actor] = {
                'dps': existing.get('dps', 0) + weighted_dps,
                'intellect': existing.get('intellect', 0) + weight,
                'haste': existing.get('haste', 0) + haste,
                'crit': existing.get('crit', 0) + crit,
                'mastery': existing.get('mastery', 0) + mastery,
                'vers': existing.get('vers', 0) + vers,
                'wdps': existing.get('wdps', 0) + wdps
            }
        else:
            results[actor] = results.get(actor, 0) + weighted_dps
    # Each profile sims "Base" again so we need to divide that to get the real average
    number_of_profiles = len(config["sims"][directory]["files"])

    if config["sims"][directory]["covenant"]["files"]:
        number_of_profiles = 1
    base_actor = results.get('Base')
    if weights:
        base_dps = {}
        for key, value in base_actor.items():
            base_dps[key] = value / number_of_profiles
    else:
        base_dps = base_actor / number_of_profiles
    results['Base'] = base_dps
    return results


def analyze(talents, directory, dungeons, weights, timestamp, covenant):
    # pylint: disable=too-many-arguments, too-many-locals
    """main analyze function"""
    base_path =  os.path.join(directory, utils.get_simc_dir(talents, covenant, 'output'))
    csv_path = os.path.join(base_path, 'statweights.csv')

    headers = ['profile', 'actor', 'DD', 'DPS']
    if weights:
        headers += ['int', 'haste', 'crit', 'mastery', 'vers']
    data = pandas.read_csv(csv_path, usecols=headers)

    talent_string = "_{0}".format(talents) if talents else ""
    covenant_string = "_{0}".format(covenant) if covenant else ""
    sim_types = ["Dungeons"] if dungeons else ["Composite", "Single"]
    covenant_range = config["sims"][directory]["steps"][0] == "CovenantRange"

    for sim_type in sim_types:
        results = build_results(data, weights, sim_type, directory)
        base_dps = results.get('Base')
        if config["analyze"]["markdown"]:
            build_markdown(sim_type, talent_string, results, directory,
                           weights, base_dps, covenant_string)
        if config["analyze"]["csv"]:
            build_csv(sim_type, talent_string, results, directory,
                      weights, base_dps, covenant_string)
        # If covenant_range is true we skip building the json here to do it later
        if config["analyze"]["json"] and not covenant_range and not weights:
            build_json(sim_type, talent_string, results, directory,
                       directory, timestamp, covenant_string)

    # Check if we need to build extra JSON files
    if covenant_range:
        build_talented_covenant_json(talents)
        build_covenant_json()
