import os
import argparse
import yaml

fightExpressions = {
    "pw": 'fight_style="Patchwerk"',
    "lm": 'fight_style="LightMovement"',
    "hm": 'fight_style="HeavyMovement"',
    "ba": 'raid_events+=/adds,count=1,first=30,cooldown=60,duration=20',
    "sa": 'raid_events+=/adds,count=3,first=45,cooldown=45,duration=10,distance=5',
    "1": 'desired_targets="1"',
    "2": 'desired_targets="2"',
    "dungeons": 'fight_style="DungeonSlice"',
    "ptr": 'ptr=1\n'
}


def assure_path_exists(path):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def clear_out_folders(path):
    assure_path_exists(path)
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def build_settings(talent_string, profile_name):
    settings_string = '\n'
    settings_string += "talents={0}\n".format(talent_string)
    for expression in fightExpressions:
        if expression in profile_name:
            settings_string += fightExpressions[expression] + "\n"
    return settings_string


with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile)

parser = argparse.ArgumentParser(description='Generates sim profiles.')
parser.add_argument('dir', help='Directory to generate profiles for.')
parser.add_argument('--dungeons', help='Run a dungeonsimming batch of sims.', action='store_true')
parser.add_argument('--talents', help='indicate talent build for output.', choices=config["builds"].keys())
parser.add_argument('--ptr', help='indicate if the sim should use ptr data.', action='store_true')
args = parser.parse_args()

clear_out_folders('%sresults/' % args.dir)
clear_out_folders('%sprofiles/' % args.dir)

# build combination list e.g. pw_sa_1
fightStyles = ["pw", "lm", "hm"]
addTypes = ["sa", "ba", "na"]
targets = ["1", "2"]
combinations = [
    "{0}_{1}_{2}".format(fight, add, tar) for fight in fightStyles for add in addTypes for tar in targets
]

if __name__ == '__main__':
    for simFile in config["sims"][args.dir[:-1]]["files"]:
        baseFile = "{0}{1}".format(args.dir, simFile)
        with open(baseFile, 'r') as f:
            data = f.read()
            f.close()
        if args.dungeons:
            combinations = ["dungeons"]
        for profile in combinations:
            # prefix the profile name with the base file name
            profile_name = "{0}_{1}".format(simFile[:-5], profile)
            if args.dungeons:
                talents = config["builds"][args.talents]["dungeons"]
            else:
                talents = config["builds"][args.talents]["composite"]

            settings = build_settings(talents, profile)
            simcFile = "profiles/{0}.simc".format(profile_name)
            with open(args.dir + simcFile, "w+") as file:
                if args.ptr:
                    file.writelines(fightExpressions["ptr"])
                file.writelines(data)
                file.writelines(settings)
                file.close()
