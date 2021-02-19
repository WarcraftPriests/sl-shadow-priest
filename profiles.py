"""Generates profiles used to sim based on the base profiles"""
import os
from itertools import combinations_with_replacement
import re
import yaml
import internal.utils as utils

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


fightExpressions = {
    "pw": 'fight_style="Patchwerk"',
    "lm": 'fight_style="LightMovement"',
    "hm": 'fight_style="HeavyMovement"',
    "ba": 'raid_events+=/adds,count=1,first=30,cooldown=60,duration=20',
    "sa": 'raid_events+=/adds,count=3,first=45,cooldown=45,duration=10,distance=5',
    "1": 'desired_targets=1',
    "2": 'desired_targets=2',
    "dungeons": 'fight_style="DungeonSlice"',
    "ptr": 'ptr=1\n',
    "weights": 'calculate_scale_factors="1"\nscale_only="intellect,crit,mastery,vers,haste"'
}


def assure_path_exists(path):
    """Make sure the path exists and contains a folder"""
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def clear_out_folders(path):
    """Clear out any existing files in the given path"""
    assure_path_exists(path)
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except OSError as error:
            print(error)


def build_settings(profile_name_string, weights, covenant_string):
    """Add any and all expressions to the bottom of the profile"""
    settings_string = '\n'
    if covenant_string:
        settings_string += "covenant={0}\n".format(covenant_string)
    for expression in fightExpressions:
        if expression in profile_name_string:
            settings_string += fightExpressions[expression] + "\n"
    if weights:
        settings_string += fightExpressions['weights']
    return settings_string


def generate_combination_name(stat_distribution):
    """generates a profile name based on the counts of each stat"""
    mastery = stat_distribution.count('mastery')
    versatility = stat_distribution.count('versatility')
    haste = stat_distribution.count('haste')
    crit = stat_distribution.count('crit')
    return "M{0}_V{1}_H{2}_C{3}".format(mastery, versatility, haste, crit)


def generate_stat_string(stat_distribution, name):
    """generates the gear rating string based on the count of the stat"""
    count = stat_distribution.count(name)
    stats_base = config["stats"]["base"] / 4
    extra_line = "\n" if name == "versatility" else ""
    stat_amount = (count * config["stats"]["steps"]) + int(stats_base)
    return "gear_{0}_rating={1}{2}".format(name, stat_amount, extra_line)


def build_stats_files():
    """Build generated.simc stats file from stats.simc"""
    sim_file = 'stats.simc'
    base_file = "{0}{1}".format(args.dir, sim_file)
    stats = config["stats"]["include"]
    stats_base = config["stats"]["base"] / 4
    num_of_steps = (config["stats"]["total"] -
                    config["stats"]["base"]) / config["stats"]["steps"]
    distributions = combinations_with_replacement(stats, int(num_of_steps))
    rating_combinations = []
    for dist in distributions:
        combination = {
            "name": generate_combination_name(dist),
            "mastery": generate_stat_string(dist, "mastery"),
            "versatility": generate_stat_string(dist, "versatility"),
            "haste": generate_stat_string(dist, "haste"),
            "crit": generate_stat_string(dist, "crit")
        }
        rating_combinations.append(combination)
    print("Simming {0} number of combinations".format(
        len(rating_combinations)))
    output_file = "{0}/generated.simc".format(args.dir)
    base_stats = """gear_crit_rating={0}
gear_haste_rating={0}
gear_mastery_rating={0}
gear_versatility_rating={0}\n\n""".format(
        int(stats_base))
    with open(base_file, 'r') as file:
        data = file.read()
        file.close()
    with open(output_file, 'w+') as file:
        file.writelines(data)
        file.writelines(base_stats)
        for combo in rating_combinations:
            for stat in stats:
                file.write(
                    'profileset."{0}"+={1}\n'.format(combo.get('name'), combo.get(stat)))


def build_simc_file(talent_string, covenant_string, profile_name):
    """Returns output file name based on talent and covenant strings"""
    if covenant_string:
        if talent_string:
            return "profiles/{0}/{1}/{2}.simc".format(talent_string, covenant_string, profile_name)
        return "profiles/{0}/{1}.simc".format(covenant_string, profile_name)
    if talent_string:
        return "profiles/{0}/{1}.simc".format(talent_string, profile_name)
    return "profiles/{0}.simc".format(profile_name)


def replace_talents(talent_string, data):
    """Replaces the talents variable with the talent string given"""
    if "talents=" in data:
        data = re.sub(
            r'talents=.*', "talents={}".format(talent_string), data, 1)
    else:
        data.replace(
            "spec=shadow", "spec=shadow\ntalents={0}".format(talent_string))
    return data


def replace_conduits(talent_string, data):
    """replace conduits with config values"""
    positions = ["first", "second"]
    items = ["id", "name"]

    # replace first.id, second.id, first.name, second.name
    for position in positions:
        for item in items:
            data = data.replace("${{conduits.{0}.{1}}}".format(
                position, item), config["builds"][talent_string]["conduits"][position][item])
    return data


def update_talents(talent_string, replacement):
    """replaces talent in string with given replacement"""
    new_talents = ""
    talent_string = str(talent_string)
    if replacement == "mindbender":
        new_talents = talent_string[:5] + "2" + talent_string[6:]
    return new_talents


def build_profiles(talent_string, covenant_string):
    # pylint: disable=R0912, too-many-locals, too-many-statements, line-too-long
    """build combination list e.g. pw_sa_1"""
    fight_styles = ["pw", "lm", "hm"]
    add_types = ["sa", "ba", "na"]
    targets = ["1", "2"]
    combinations = [
        "{0}_{1}_{2}".format(
            fight, add, tar
        ) for fight in fight_styles for add in add_types for tar in targets
    ]
    sim_files = config["sims"][args.dir[:-1]]["files"]

    if config["sims"][args.dir[:-1]]["covenant"]["files"]:
        sim_files = ["{0}.simc".format(covenant_string)]

    for sim_file in sim_files:
        with open("{0}{1}".format(args.dir, sim_file), 'r') as file:
            data = file.read()
            file.close()
        if args.dungeons:
            combinations = ["dungeons"]
        if talent_string:
            if args.dungeons:
                talents_expr = config["builds"][talent_string]["dungeons"]
            else:
                talents_expr = config["builds"][talent_string]["composite"]
        else:
            talents_expr = ''
        # insert soulbinds before we replace conduits
        if covenant_string:
            if args.dungeons:
                data = data.replace(
                    "${soulbind}", config["covenants"][covenant_string]["soulbind"]["dungeons"])
            else:
                data = data.replace(
                    "${soulbind}", config["covenants"][covenant_string]["soulbind"]["composite"])
        # insert talents in here so copy= works correctly
        if talents_expr:
            data = data.replace("${talents}", str(talents_expr))
            data = data.replace("${talents.mindbender}", update_talents(
                str(talents_expr), "mindbender"))
            data = replace_conduits(talent_string, data)
        if covenant_string:
            data = data.replace("${covenant}", covenant_string)

        for profile in combinations:
            sim_data = data
            # prefix the profile name with the base file name
            profile_name = "{0}_{1}".format(sim_file[:-5], profile)
            settings = build_settings(
                profile, config["sims"][args.dir[:-1]]["weights"], covenant_string)

            # insert talents based on profile
            if talents_expr:
                if profile in config["singleTargetProfiles"]:
                    new_talents = config["builds"][talent_string]["single"]
                    # Only replace Mindbender talent if using Shadowflame Prism, and it is not a legendary sim
                    if config["legendary"]["single"] == "6982" and args.dir[:-1] != 'legendaries' and args.dir[:-1] != 'legendary-items':
                        sim_data = replace_talents(update_talents(
                            talents_expr, "mindbender"), sim_data)
                    else:
                        sim_data = replace_talents(new_talents, sim_data)
                    sim_data = sim_data.replace(
                        "${legendary.id}", config["legendary"]["single"])
                else:
                    if args.dungeons:
                        # Only replace Mindbender talent if using Shadowflame Prism, and it is not a legendary sim
                        if config["legendary"]["dungeons"] == "6982" and args.dir[:-1] != 'legendaries' and args.dir[:-1] != 'legendary-items':
                            sim_data = replace_talents(update_talents(
                                talents_expr, "mindbender"), sim_data)
                        else:
                            sim_data = replace_talents(talents_expr, sim_data)
                        sim_data = sim_data.replace(
                            "${legendary.id}", config["legendary"]["dungeons"])
                    else:
                        # Only replace Mindbender talent if using Shadowflame Prism, and it is not a legendary sim
                        if config["legendary"]["composite"] == "6982" and args.dir[:-1] != 'legendaries' and args.dir[:-1] != 'legendary-items':
                            sim_data = replace_talents(update_talents(
                                talents_expr, "mindbender"), sim_data)
                        else:
                            sim_data = replace_talents(talents_expr, sim_data)
                        sim_data = sim_data.replace(
                            "${legendary.id}", config["legendary"]["composite"])

            simc_file = build_simc_file(
                talent_string, covenant_string, profile_name)
            with open(args.dir + simc_file, "w+") as file:
                if args.ptr:
                    file.writelines(fightExpressions["ptr"])
                file.writelines(sim_data)
                file.writelines(settings)
                file.close()


if __name__ == '__main__':
    parser = utils.generate_parser('Generates sim profiles.')
    args = parser.parse_args()

    talents = utils.get_talents(args)
    covenants = utils.get_covenant(args)

    clear_out_folders('%soutput/' % args.dir)
    clear_out_folders('%sprofiles/' % args.dir)

    if args.dir[:-1] == 'stats':
        build_stats_files()

    if covenants:
        if talents:
            for talent, covenant in [
                (talent, covenant) for talent in talents for covenant in covenants
            ]:
                clear_out_folders(
                    '{0}output/{1}/{2}/'.format(args.dir, talent, covenant))
                clear_out_folders(
                    '{0}profiles/{1}/{2}/'.format(args.dir, talent, covenant))
                print("Building {0}-{1} profiles...".format(talent, covenant))
                build_profiles(talent, covenant)
        else:
            for covenant in covenants:
                clear_out_folders('{0}output/{1}/'.format(args.dir, covenant))
                clear_out_folders(
                    '{0}profiles/{1}/'.format(args.dir, covenant))
                print("Building {0} profiles...".format(covenant))
                build_profiles(None, covenant)
    elif talents:
        for talent in talents:
            clear_out_folders('{0}output/{1}/'.format(args.dir, talent))
            clear_out_folders('{0}profiles/{1}/'.format(args.dir, talent))
            print("Building {0} profiles...".format(talent))
            build_profiles(talent, None)
    else:
        print("Building default profiles...")
        build_profiles(None, None)
