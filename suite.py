"""run full suite of sims"""
import argparse
import csv
import os
import subprocess
import sys
import yaml


with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def call_process(process_args):
    """runs a process and constantly monitors for output"""
    subprocess.check_call(process_args, stdout=sys.stdout,
                          stderr=subprocess.STDOUT)


def update_state(directory, sim_type, output_file):
    """updates state text file"""
    with open(output_file, 'a+') as file:
        file.write("{0},{1},\n".format(directory, sim_type))
        file.close()


def check_state(sim_dir, sim_type, output_file):
    """opens state file to see if the sim has been ran yet"""
    with open(output_file, 'r') as file:
        sims = csv.reader(file, delimiter=',')
        for row in sims:
            if len(row) == 0:
                continue
            if row[0] == sim_dir and row[1] == sim_type:
                return False
    return True


def main():
    """main function, runs sim suite"""
    output_file = "internal/suite.csv"

    parser = argparse.ArgumentParser(description="Sims full sim suite")
    parser.add_argument(
        '--exclude', help='Exclude certain sim folders from the suite run',
        choices=config["sims"].keys(), default=["apl", "gear", "talent-builds"],
        nargs='+', required=False)
    parser.add_argument(
        '--fresh', help='restart suite from start', action='store_true')
    args = parser.parse_args()

    if args.fresh or not os.path.exists(output_file):
        with open(output_file, 'w') as file:
            file.write('dir,type,\n')
            file.close()

    for sim in config["sims"].keys():
        if sim in args.exclude:
            continue
        sim_dir = ("{0}/").format(sim)
        if check_state(sim_dir, "composite", output_file):
            print("Running sim suite for {0} - Composite".format(sim))
            call_process(["python", "profiles.py", sim_dir])
            call_process(["python", "sim.py", sim_dir])
            update_state(sim_dir, 'composite', output_file)
        if check_state(sim_dir, "dungeons", output_file):
            print("Running sim suite for {0} - Dungeons".format(sim))
            call_process(["python", "profiles.py", sim_dir, "--dungeons"])
            call_process(["python", "sim.py", sim_dir, "--dungeons"])
            update_state(sim_dir, 'dungeons', output_file)


if __name__ == "__main__":
    main()
