"""stores utils that are shared between scripts"""
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
