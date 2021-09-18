"""main sim script to run sims"""

import sys
import platform
import re
import os
from os import listdir
import importlib
import yaml

from internal.weights import find_weights
from internal.sim_parser import parse_json
from internal.sim_parser import get_timestamp
from internal.analyze import analyze
from internal import utils

api_secrets_spec = importlib.util.find_spec("api_secrets")
local_secrets_spec = importlib.util.find_spec("local_secrets")

if api_secrets_spec:
    api_secrets = api_secrets_spec.loader.load_module()

if local_secrets_spec:
    local_secrets = local_secrets_spec.loader.load_module()

with open("config.yml", "r", encoding="utf8") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def get_path(simc_build_version):
    """get path depending on local OS"""
    path_dict = local_secrets.simc_path
    if not path_dict:
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            return "simc"
        return "simc.exe"

    if platform.system() == 'Darwin' or platform.system() == 'Linux':
        return handle_path_darwin(path_dict[simc_build_version])
    return handle_path_win(path_dict[simc_build_version])


def handle_path_darwin(path):
    """find the proper path if using darwin based OS"""
    if path.endswith("/"):
        return f"{path}simc"
    return f"{path}/simc"


def handle_path_win(path):
    """find the proper path if using windows based OS"""
    if path.endswith("\\"):
        return f"{path}simc.exe"
    return f"{path}\\simc.exe"


def get_api_key(args, simc_build_version):
    """get api key from secret"""
    if args.local:
        executable = get_path(simc_build_version)

        if is_executable(executable):
            return executable
        print(
            f"{executable} not a valid executable please check your local_secrets.py or your path")
        sys.exit()
    else:
        return api_secrets.api_key


def is_executable(path):
    """check if given path is an executable"""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def run_sims(args, iterations, talent, covenant):
    # pylint: disable=import-outside-toplevel
    """run sims with the given config"""
    if args.local:
        from internal.simc import raidbots
    else:
        from internal.api import raidbots
    simc_build = config["simcBuild"]
    print(f"Running sims on {simc_build} in {args.dir}")
    existing = listdir(
        args.dir + utils.get_simc_dir(talent, covenant, 'output'))
    profiles = listdir(
        args.dir + utils.get_simc_dir(talent, covenant, 'profiles'))
    count = 0

    for profile in profiles:
        profile_name = re.search(
            '((hm|lm|pw).+?(?=.simc)|dungeons.simc)', profile).group()
        count = count + 1
        if not args.dungeons:
            weight = find_weights(config["compositeWeights"]).get(profile_name)
        else:
            weight = 1
        print(f"Simming {count} out of {len(profiles)}.")
        output_name = profile.replace('simc', 'json')
        if output_name not in existing and weight > 0:
            output_location = args.dir + \
                utils.get_simc_dir(talent, covenant, 'output') + output_name
            profile_location = args.dir + \
                utils.get_simc_dir(talent, covenant, 'profiles') + profile
            # prefix the profile name with the base file name
            profile_name_with_dir = f"{args.dir}{profile_name}"
            raidbots(get_api_key(args, config["simcBuild"]), profile_location,
                     config["simcBuild"], output_location, profile_name_with_dir, iterations)
        elif weight == 0:
            print(f"-- {output_name} has a weight of 0. Skipping file.")
        else:
            print(f"-- {output_name} already exists. Skipping file.")


def convert_to_csv(args, weights, talent, covenant):
    """creates results/statweights.txt"""
    results_dir = args.dir + utils.get_simc_dir(talent, covenant, 'output')
    parse_json(results_dir, weights)


def analyze_data(args, talent, covenant, weights):
    """create results"""
    analyze(talent, args.dir, args.dungeons,
            weights, get_timestamp(), covenant)


def main():
    # pylint: disable=import-outside-toplevel,too-many-branches,unsupported-assignment-operation,duplicate-code
    """main function, runs and parses sims"""
    parser = utils.generate_parser("Parses a list of reports from Raidbots.")
    parser.add_argument(
        '--iterations', help='Pass through specific iterations to run on. Default is 10000')
    parser.add_argument(
        '--local', help='indicate if the simulation should run local.', action='store_true')
    parser.add_argument(
        '--auto_download', help='indicate if we should automatically download latest simc.',
        action='store_true'
    )
    args = parser.parse_args()

    sys.path.insert(0, args.dir)

    # Download simc if needed
    if local_secrets and args.local and args.auto_download:
        from internal.auto_download import download_latest
        local_secrets.simc_path['latest'] = download_latest()
        # Additional temp swap to using the latest build
        config['simcBuild'] = 'latest'

    weights = config["sims"][args.dir[:-1]]["weights"]
    if args.iterations:
        iterations = args.iterations
    else:
        iterations = str(config["defaultIterations"])

    talents = utils.get_talents(args)
    covenants = utils.get_covenant(args)

    if covenants:
        if talents:
            for talent, covenant in [
                (talent, covenant) for talent in talents for covenant in covenants
            ]:
                print(f"Simming {talent}-{covenant} profiles...")
                run_sims(args, iterations, talent, covenant)
                convert_to_csv(args, weights, talent, covenant)
                analyze_data(args, talent, covenant, weights)
        else:
            for covenant in covenants:
                print(f"Simming {covenant} profiles...")
                run_sims(args, iterations, None, covenant)
                convert_to_csv(args, weights, None, covenant)
                analyze_data(args, None, covenant, weights)
    elif talents:
        for talent in talents:
            print(f"Simming {talent} profiles...")
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
