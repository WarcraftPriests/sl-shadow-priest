'internal configuration - exposes config.yml as a dict'
import yaml

config = {}
with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)
