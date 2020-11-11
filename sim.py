import argparse
import yaml
import sys
import platform
import re
import os

from os import listdir
from internal.weights import find_weights
from internal.sim_parser import parse_json
from internal.sim_parser import get_timestamp
from internal.analyze import analyze

# Check if Mac or PC
if platform.system() == 'Darwin':
    pyVar = 'python3'
else:
    pyVar = 'python'

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def get_simc_dir(talent, covenant, folder_name):
    if covenant:
        return "{0}/{1}/{2}/".format(folder_name, talent, covenant)
    elif talent:
        return "{0}/{1}/".format(folder_name, talent)
    else:
        return "{0}/".format(folder_name)


def get_path(simcBuildVersion):
    try:
        import local_secrets
        pathDict = local_secrets.simc_path
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            return handle_path_darwin(pathDict[simcBuildVersion])
        else:
            return handle_path_win(pathDict[simcBuildVersion])
    except:
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            return "simc"
        else:
            return "simc.exe"


def handle_path_darwin(path):
    if path.endswith("/"):
        return "{0}simc".format(path)
    else:
        return "{0}/simc".format(path)


def handle_path_win(path):
    if(path.endswith("\\")):
        return "{0}simc.exe".format(path)
    else:
        return "{0}\\simc.exe".format(path)


def get_api_key(args, simcBuildVersion):
    if args.local:
        executable = get_path(simcBuildVersion)
        
        if is_executable(executable):
            return executable
        else:
            print("{0} not a valid executable please check your local_secrets.py or your path".format(executable))
            sys.exit()
    else :
        try:
            import api_secrets
            return api_secrets.api_key
        except ModuleNotFoundError:
            print('Please create api_secrets.py file like mentioned in the Readme')
            sys.exit()

def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)

def run_sims(args, iterations, talent, covenant):
    if args.local:
        from internal.simc import raidbots
    else:
        from internal.api import raidbots

    api_key = get_api_key(args, config["simcBuild"])
    
    print("Running sims on {0} in {1}".format(config["simcBuild"], args.dir))
    existing = listdir(args.dir + get_simc_dir(talent, covenant, 'output'))
    profiles = listdir(args.dir + get_simc_dir(talent, covenant, 'profiles'))
    count = 0

    for profile in profiles:
        profile_name = re.search(
            '((hm|lm|pw).+?(?=.simc)|dungeons.simc)', profile).group()
        count = count + 1
        if not args.dungeons:
            weight = find_weights(config["compositeWeights"]).get(profile_name)
        else:
            weight = 1
        print("Simming {0} out of {1}.".format(count, len(profiles)))
        output_name = profile.replace('simc', 'json')
        if output_name not in existing and weight > 0:
            output_location = args.dir + \
                get_simc_dir(talent, covenant, 'output') + output_name
            profile_location = args.dir + \
                get_simc_dir(talent, covenant, 'profiles') + profile
            # prefix the profile name with the base file name
            profile_name_with_dir = "{0}{1}".format(args.dir, profile_name)
            raidbots(api_key, profile_location,
                     config["simcBuild"], output_location, profile_name_with_dir, iterations)
        elif weight == 0:
            print("-- {0} has a weight of 0. Skipping file.".format(output_name))
        else:
            print("-- {0} already exists. Skipping file.".format(output_name))


def convert_to_csv(args, weights, talent, covenant):
    # creates results/statweights.txt
    results_dir = args.dir + get_simc_dir(talent, covenant, 'output')
    parse_json(results_dir, weights)


def analyze_data(args, talent, covenant, weights):
    analyze(talent, args.dir, args.dungeons,
            weights, get_timestamp(), covenant)


def main():
    parser = argparse.ArgumentParser(
        description='Parses a list of reports from Raidbots.')
    parser.add_argument('dir', help='Directory you wish to sim.')
    parser.add_argument(
        '--iterations', help='Pass through specific iterations to run on. Default is 10000')
    parser.add_argument(
        '--dungeons', help='Run a dungeonsimming batch of sims.', action='store_true')
    parser.add_argument(
        '--talents', help='indicate talent build for output.', choices=config["builds"].keys())
    parser.add_argument(
        '--covenant', help='indicate covenant build for output.', choices=config["covenants"])
    parser.add_argument(
        '--local', help='indicate if the simulation should run local.', action='store_true')
    parser.add_argument(
        '--auto_download', help='indicate if we should automatically download latest simc.', action='store_true')
    args = parser.parse_args()

    sys.path.insert(0, args.dir)


    # Download simc if needed
    if (args.local and args.auto_download):
        from internal.auto_download import download_latest
        from local_secrets import simc_path
        simc_path['latest'] = download_latest()
        config['simcBuild'] = 'latest' # Additional temp swap to using the latest build

    weights = config["sims"][args.dir[:-1]]["weights"]
    if args.iterations:
        iterations = args.iterations
    else:
        iterations = str(config["defaultIterations"])

    if args.talents:
        talents = [args.talents]
    elif config["sims"][args.dir[:-1]]["builds"]:
        talents = config["builds"].keys()
    else:
        talents = []

    if args.covenant:
        covenants = [args.covenant]
    elif config["sims"][args.dir[:-1]]["covenant"]["lookup"]:
        covenants = config["covenants"]
    else:
        covenants = []

    if covenants:
        for talent, covenant in [(talent, covenant) for talent in talents for covenant in covenants]:
            print("Simming {0}-{1} profiles...".format(talent, covenant))
            run_sims(args, iterations, talent, covenant)
            convert_to_csv(args, weights, talent, covenant)
            analyze_data(args, talent, covenant, weights)
    elif talents:
        for talent in talents:
            print("Simming {0} profiles...".format(talent))
            run_sims(args, iterations, talent, None)
            convert_to_csv(args, weights, talent, None)
            analyze_data(args, talent, None, weights)
    else:
        print("Simming default profiles...")
        run_sims(args, iterations, None, None)
        convert_to_csv(args, weights, None, None)
        analyze_data(args, None, None, weights)


if __name__ == "__main__":
    main()