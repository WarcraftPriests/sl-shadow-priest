import os
import argparse
import yaml

from itertools import combinations_with_replacement

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


fightExpressions = {
    "pw": 'fight_style="Patchwerk"',
    "lm": 'fight_style="LightMovement"',
    "hm": 'fight_style="HeavyMovement"',
    "ba": 'raid_events+=/adds,count=1,first=30,cooldown=60,duration=20',
    "sa": 'raid_events+=/adds,count=3,first=45,cooldown=45,duration=10,distance=5',
    "1": 'desired_targets="1"',
    "2": 'desired_targets="2"',
    "dungeons": 'fight_style="DungeonSlice"',
    "ptr": 'ptr=1\n',
    "weights": 'calculate_scale_factors="1"\nscale_only="intellect,crit,mastery,vers,haste"'
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


def build_settings(talent_string, profile_name_string, weights, covenant_string):
    settings_string = '\n'
    if talent_string:
        settings_string += "talents={0}\n".format(talent_string)
    if covenant_string:
        settings_string += "covenant={0}\n".format(covenant_string)
    for expression in fightExpressions:
        if expression in profile_name_string:
            settings_string += fightExpressions[expression] + "\n"
    if weights:
        settings_string += fightExpressions['weights']
    return settings_string


def build_stats_files():
    simFile = 'stats.simc'
    baseFile = "{0}{1}".format(args.dir, simFile)
    stats = config["stats"]["include"]
    statsBase = config["stats"]["base"] / 4
    statsSteps = config["stats"]["steps"]
    numOfSteps = (config["stats"]["total"] - config["stats"]["base"]) / statsSteps
    distributions = combinations_with_replacement(stats, int(numOfSteps))
    ratingCombinations = []
    for dist in distributions:
        mastery = dist.count('mastery')
        versatility = dist.count('versatility')
        haste = dist.count('haste')
        crit = dist.count('crit')
        masteryString = "gear_mastery_rating={0}".format(int((mastery * statsSteps) + statsBase))
        versatilityString = "gear_versatility_rating={0}".format(int((versatility * statsSteps) + statsBase))
        hasteString = "gear_haste_rating={0}".format(int((haste * statsSteps) + statsBase))
        critString = "gear_crit_rating={0}".format(int((crit * statsSteps) + statsBase))
        ratingCombinations.append(
            {
                "name": "M{0}_V{1}_H{2}_C{3}".format(mastery, versatility, haste, crit),
                "mastery": masteryString,
                "vers": versatilityString,
                "haste": hasteString,
                "crit": critString
            }
        )
    numberOfCombos = len(ratingCombinations)
    outputFile = "{0}/generated.simc".format(args.dir)
    baseStats = "gear_crit_rating={0}\ngear_haste_rating={0}\ngear_mastery_rating={0}\ngear_versatility_rating={0}\n".format(int(statsBase))
    with open(baseFile, 'r') as f:
        data = f.read()
        f.close()
    with open(outputFile, 'w+') as file:
        file.writelines(data)
        file.writelines(baseStats)
        for combo in ratingCombinations:
            file.write('profileset."{0}"+={1}\nprofileset."{2}"+={3}\nprofileset."{4}"+={5}\nprofileset."{6}"+={7}\n\n'.format(
                combo.get('name'), combo.get('mastery'),
                combo.get('name'), combo.get('vers'),
                combo.get('name'), combo.get('haste'),
                combo.get('name'), combo.get('crit')
            ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates sim profiles.')
    parser.add_argument('dir', help='Directory to generate profiles for.')
    parser.add_argument('--weights', help='Run sims with weights', action='store_true')
    parser.add_argument('--dungeons', help='Run a dungeonsimming batch of sims.', action='store_true')
    parser.add_argument('--talents', help='indicate talent build for output.', choices=config["builds"].keys())
    parser.add_argument('--covenant', help='indicate covenant build for output.', choices=config["covenants"])
    parser.add_argument('--ptr', help='indicate if the sim should use ptr data.', action='store_true')
    args = parser.parse_args()

    # check if sim dir requires talents
    if not args.talents and config["sims"][args.dir[:-1]]["builds"]:
        print("ERROR: Must provide talents for {0}/ sims.".format(args.dir[:-1]))
        exit()

    # check if sim dir requires covenant
    if not args.covenant and config["sims"][args.dir[:-1]]["covenant"]:
        print("ERROR: Must provide covenant for {0}/ sims.".format(args.dir[:-1]))
        exit()

    clear_out_folders('%soutput/' % args.dir)
    clear_out_folders('%sprofiles/' % args.dir)

    if args.dir[:-1] == 'stats':
        build_stats_files()

    # build combination list e.g. pw_sa_1
    fightStyles = ["pw", "lm", "hm"]
    addTypes = ["sa", "ba", "na"]
    targets = ["1", "2"]
    combinations = [
        "{0}_{1}_{2}".format(fight, add, tar) for fight in fightStyles for add in addTypes for tar in targets
    ]
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
            if args.talents:
                if args.dungeons:
                    talents = config["builds"][args.talents]["dungeons"]
                else:
                    talents = config["builds"][args.talents]["composite"]
            else:
                talents = ''
            settings = build_settings(talents, profile, args.weights, args.covenant)
            simcFile = "profiles/{0}.simc".format(profile_name)
            with open(args.dir + simcFile, "w+") as file:
                if args.ptr:
                    file.writelines(fightExpressions["ptr"])
                file.writelines(data)
                file.writelines(settings)
                file.close()
