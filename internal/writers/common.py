'Common helpers for writers'
import os

from internal.config import config
from internal.weights import find_weights
from internal.spell_ids import find_ids


def generate_report_name(sim_type, talent=None, covenant=None):
    """create report name based on talents and covenant"""
    talents = f" - {talent.strip('_')}" if talent else ""
    covenant = f" - {covenant.strip('_')}" if covenant else ""
    return f"{sim_type}{talents}{covenant}"


def assure_path_exists(path):
    """Make sure the path exists and contains a folder"""
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def build_output_string(base_path, sim_type, talent, covenant, file_ext):
    """creates output string for the results file"""
    output_dir = os.path.join(base_path, "results")
    assure_path_exists(output_dir)
    return os.path.join(output_dir, f"Results_{sim_type}{talent}{covenant}.{file_ext}")


def lookup_id(name, directory):
    """lookup the spell or item id of an item name"""
    lookup_type = config["sims"][directory]["lookupType"]
    if lookup_type == "spell":
        return lookup_spell_id(name, directory)
    if lookup_type == "item":
        return lookup_item_id(name, directory)
    if lookup_type == "none":
        return None
    print(f"Could not find id for {name}")
    return None


def lookup_spell_id(spell_name, directory):
    """lookup a spell name from the ids dict"""
    ids = find_ids(directory)
    if ids:
        return ids.get(spell_name)
    print(f"Could not find spell id for {spell_name}")
    return None


def lookup_item_id(item_name, directory):
    """
    get the list of sim files from config
    loop over them and search for the item name line by line
    """
    for sim_file in config["sims"][directory]["files"]:
        with open(sim_file, 'r') as file:
            for line in file:
                if item_name in line:
                    # find ,id= -> take 2nd half ->
                    # find , -> take 1st half
                    return int(line.split(',id=')[1].split(',')[0])
    return None


def convert_increase_to_double(increase):
    """convert string increase to double"""
    increase = increase.strip('%')
    increase = round(float(increase), 4)
    if increase:
        increase = round(increase / 100, 4)
    return increase


def get_change(current, previous):
    """gets the percent change between two numbers"""
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
    """looks up the weight based on the sim type"""
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
    return weight
