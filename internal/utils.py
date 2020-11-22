"""stores utils that are shared between scripts"""
import os
import argparse

from internal.config import config


def get_talents(args):
    """lookup talents based on current config"""
    if args.talents:
        talents = [args.talents]
    elif config["sims"][args.dir]["builds"]:
        talents = config["builds"].keys()
    else:
        talents = []
    return talents


def get_covenant(args):
    """lookup covenant based on current config"""
    if args.covenant:
        covenants = [args.covenant]
    elif config["sims"][args.dir]["covenant"]["lookup"]:
        covenants = config["covenants"]
    else:
        covenants = []
    return covenants


def get_simc_dir(talent, covenant, folder_name):
    """get proper directory based on talent and covenant options"""
    if covenant:
        return os.path.join(folder_name, talent, covenant)
    if talent:
        return os.path.join(folder_name, talent)
    return folder_name


def generate_parser(description):
    """creates the shared argparser for sim.py and profiles.py"""
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
