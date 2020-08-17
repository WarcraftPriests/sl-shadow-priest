# Shadowlands Shadow Priest Sims

This repo includes scripts and sims for shadow priests.

## Important Links
- [Wiki](https://github.com/WarcraftPriests/sl-shadow-priest/wiki)
- [Dungeon sims courtesy of Hero Damage](https://www.herodamage.com)

## Discussion
- [Discord](https://discord.gg/WarcraftPriests)
- [Website](https://warcraftpriests.com/)

## How to Run
All scripts are run built with python3, but should be able to be run with python2, but results may vary.

1. Run `pip install -r requirements.txt` in order for the scripts to work.
2. Edit and confirm config in `config.yml`, this controls how profiles are built, sims are ran, and aggregated. See the [wiki](https://github.com/WarcraftPriests/sl-shadow-priest/wiki/Config-File) for more information.
3. Run `python profiles.py dir/ [--ptr, --dungeons, --weights, --talents [as, AM]]` for the directory you want to sim. Current talent options are indicated by the config keys under: `builds`.
4. To run the sim in Raidbots create `api_secrets.py` inside the root directory. Set `api_key = XXX`.
5. By default if a file already exists in `output/` or if the weight in `internal/weights.py` is 0, sim.py will skip it
6. To run the sims use `python sim.py dir/ [--iterations 10000, --dungeons, --weights, --talents [as, AM]]` where `dir/` is the sim directory you want to sim
7. Based on config keys in `analyze` markdown, csv, and json will be generated for the aggregated sims. These will output seperate files for Composite, Single Target, or Dungeon sims. You can find all output files in the `results/` folder in any sim folder.
