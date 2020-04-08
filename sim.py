import argparse
import yaml
import apiSecrets
import subprocess
import sys
import platform
from weights import find_weights
from api import raidbots
from os import listdir

# Check if Mac or PC
if platform.system() == 'Darwin':
    pyVar = 'python3'
else:
    pyVar = 'python'

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile)


def run_sims(args, iterations):
    api_key = apiSecrets.api_key
    print("Running sims on {0} in {1}".format(config["simcBuild"], args.dir))

    # determine existing jsons
    existing = listdir(args.dir + 'results/')
    profiles = listdir(args.dir + 'profiles/')
    count = 0

    for profile in profiles:
        profile_name = profile[:-5]
        count = count + 1
        if not args.dungeons:
            weight = find_weights(config["compositeWeights"]).get(profile_name)
        else:
            weight = 1
        print("Simming {0} out of {1}.".format(count, len(profiles)))
        output_name = profile.replace('simc', 'json')
        if output_name not in existing and weight > 0:
            output_location = args.dir + 'results/' + output_name
            profile_location = args.dir + 'profiles/' + profile
            # prefix the profile name with the base file name
            profile_name_with_dir = "{0}{1}".format(args.dir, profile_name)
            raidbots(api_key, profile_location, config["simcBuild"], output_location, profile_name_with_dir, iterations)
        elif weight == 0:
            print("{0} has a weight of 0. Skipping file.".format(output_name))
        else:
            print("{0} already exists. Skipping file.".format(output_name))


def convert_to_csv(args, weights):
    # creates results/statweights.txt
    results_dir = args.dir + "results/"
    # TODO: should bring this into a function call instead of a subprocess
    subprocess.call([pyVar, 'simParser.py', '-c', weights, '-r', '-d', results_dir], shell=False)


def analyze(args):
    if args.dungeons:
        script = "analyzeDS.py"
    else:
        script = "analyze.py"

    cmd = "{0} {1} {2}".format(pyVar, script, args.dir)

    if args.weights:
        cmd += " --weights"
    if args.talents:
        cmd += " --talents {0}".format(args.talents)
    # TODO: should bring this into a function call instead of a subprocess
    subprocess.call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser(description='Parses a list of reports from Raidbots.')
    parser.add_argument('dir', help='Directory you wish to sim.')
    parser.add_argument('--weights', help='For sims ran with weights this flag will change how simParser is ran.',
                        action='store_true')
    parser.add_argument('--iterations', help='Pass through specific iterations to run on. Default is 10000')
    parser.add_argument('--dungeons', help='Run a dungeonsimming batch of sims.', action='store_true')
    parser.add_argument('--talents', help='indicate talent build for output.', choices=config["builds"].keys())
    args = parser.parse_args()

    sys.path.insert(0, args.dir)

    if args.weights:
        weights = ''
    else:
        weights = '-s'
    if args.iterations:
        iterations = args.iterations
    else:
        iterations = str(config["defaultIterations"])

    run_sims(args, iterations)
    convert_to_csv(args, weights)
    # analyze(args)


if __name__ == "__main__":
    main()
