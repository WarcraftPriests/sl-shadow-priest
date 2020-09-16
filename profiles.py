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


def build_settings(profile_name_string, weights, covenant_string):
    settings_string = '\n'
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
    numOfSteps = (config["stats"]["total"] -
                  config["stats"]["base"]) / statsSteps
    distributions = combinations_with_replacement(stats, int(numOfSteps))
    ratingCombinations = []
    for dist in distributions:
        mastery = dist.count('mastery')
        versatility = dist.count('versatility')
        haste = dist.count('haste')
        crit = dist.count('crit')
        masteryString = "gear_mastery_rating={0}".format(
            int((mastery * statsSteps) + statsBase))
        versatilityString = "gear_versatility_rating={0}".format(
            int((versatility * statsSteps) + statsBase))
        hasteString = "gear_haste_rating={0}".format(
            int((haste * statsSteps) + statsBase))
        critString = "gear_crit_rating={0}".format(
            int((crit * statsSteps) + statsBase))
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
    print("Simming {0} number of combinations".format(numberOfCombos))
    outputFile = "{0}/generated.simc".format(args.dir)
    baseStats = "gear_crit_rating={0}\ngear_haste_rating={0}\ngear_mastery_rating={0}\ngear_versatility_rating={0}\n".format(
        int(statsBase))
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


def build_simc_file(talent, covenant, profile_name):
    if covenant:
        return "profiles/{0}/{1}/{2}.simc".format(talent, covenant, profile_name)
    elif talent:
        return "profiles/{0}/{1}.simc".format(talent, profile_name)
    else:
        return "profiles/{0}.simc".format(profile_name)


def build_profiles(talent, covenant, args):
    # build combination list e.g. pw_sa_1
    fightStyles = ["pw", "lm", "hm"]
    addTypes = ["sa", "ba", "na"]
    targets = ["1", "2"]
    combinations = [
        "{0}_{1}_{2}".format(fight, add, tar) for fight in fightStyles for add in addTypes for tar in targets
    ]
    simFiles = config["sims"][args.dir[:-1]]["files"]

    if config["sims"][args.dir[:-1]]["covenant"]["files"]:
        simFiles = ["{0}.simc".format(covenant)]

    for simFile in simFiles:
        baseFile = "{0}{1}".format(args.dir, simFile)
        with open(baseFile, 'r') as f:
            data = f.read()
            f.close()
        if args.dungeons:
            combinations = ["dungeons"]
        if talent:
            if args.dungeons:
                talents = config["builds"][talent]["dungeons"]
            else:
                talents = config["builds"][talent]["composite"]
        else:
            talents = ''
        # insert talents in here so copy= works correctly
        if talents:
            data = data.replace("spec=shadow", "spec=shadow\ntalents={0}".format(talents))

        for profile in combinations:
            # prefix the profile name with the base file name
            profile_name = "{0}_{1}".format(simFile[:-5], profile)
            settings = build_settings(profile, config["sims"][args.dir[:-1]]["weights"], covenant)

            simcFile = build_simc_file(talent, covenant, profile_name)
            with open(args.dir + simcFile, "w+") as file:
                if args.ptr:
                    file.writelines(fightExpressions["ptr"])
                file.writelines(data)
                file.writelines(settings)
                file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates sim profiles.')
    parser.add_argument('dir', help='Directory to generate profiles for.')
    parser.add_argument(
        '--dungeons', help='Run a dungeonsimming batch of sims.', action='store_true')
    parser.add_argument(
        '--talents', help='indicate talent build for output.', choices=config["builds"].keys())
    parser.add_argument(
        '--covenant', help='indicate covenant build for output.', choices=config["covenants"])
    parser.add_argument(
        '--ptr', help='indicate if the sim should use ptr data.', action='store_true')
    args = parser.parse_args()

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

    clear_out_folders('%soutput/' % args.dir)
    clear_out_folders('%sprofiles/' % args.dir)

    if args.dir[:-1] == 'stats':
        build_stats_files()

    if covenants:
        for talent, covenant in [(talent, covenant) for talent in talents for covenant in covenants]:
            clear_out_folders(
                '{0}output/{1}/{2}/'.format(args.dir, talent, covenant))
            clear_out_folders(
                '{0}profiles/{1}/{2}/'.format(args.dir, talent, covenant))
            print("Building {0}-{1} profiles...".format(talent, covenant))
            build_profiles(talent, covenant, args)
    elif talents:
        for talent in talents:
            clear_out_folders('{0}output/{1}/'.format(args.dir, talent))
            clear_out_folders('{0}profiles/{1}/'.format(args.dir, talent))
            print("Building {0} profiles...".format(talent))
            build_profiles(talent, None, args)
    else:
        print("Building default profiles...")
        build_profiles(None, None, args)
