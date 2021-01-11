"""stores utils that are shared between scripts"""
import argparse
import yaml

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def get_talents(args):
    """lookup talents based on current config"""
    if args.talents:
        talents = [args.talents]
    elif config["sims"][args.dir[:-1]]["builds"]:
        talents = config["builds"].keys()
    else:
        talents = []
    return talents


def get_covenant(args):
    """lookup covenant based on current config"""
    if args.covenant:
        covenants = [args.covenant]
    elif config["sims"][args.dir[:-1]]["covenant"]["lookup"]:
        covenants = config["covenants"]
    else:
        covenants = []
    return covenants


def get_simc_dir(talent, covenant, folder_name):
    """get proper directory based on talent and covenant options"""
    if covenant:
        if talent:
            return "{0}/{1}/{2}/".format(folder_name, talent, covenant)
        return "{0}/{1}/".format(folder_name, covenant)
    if talent:
        return "{0}/{1}/".format(folder_name, talent)
    return "{0}/".format(folder_name)


def generate_parser(description):
    """creates the shared argparser for sim.pu and profiles.py"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('dir', help='Directory to generate profiles for.')
    parser.add_argument(
        '--dungeons', help='Run a dungeonsimming batch of sims.', action='store_true')
    parser.add_argument(
        '--talents', help='indicate talent build for output.', choices=config["builds"].keys())
    parser.add_argument(
        '--covenant', help='indicate covenant build for output.', choices=config["covenants"])
    parser.add_argument(
        '--ptr', help='indicate if the sim should use ptr data.', action='store_true')
    return parser
