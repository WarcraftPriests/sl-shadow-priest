# Shadowlands Shadow Priest Sims

This repo includes scripts and sims for shadow priests.

## Important Links
- [Wiki](https://github.com/WarcraftPriests/sl-shadow-priest/wiki)
- [SimulationCraft Wiki](https://github.com/simulationcraft/simc/wiki/Priests)

## Discussion
- [Discord](https://discord.gg/WarcraftPriests)
- [Website](https://warcraftpriests.com/)

## How to Run
All scripts are run built with python3, but should be able to be run with python2 (results may vary).

### Prepare your environment
1. Run `pip install -r requirements.txt` in order for the scripts to work.
2. Edit and confirm config in `config.yml`, this controls how profiles are built, sims are ran, and aggregated. See the [wiki](https://github.com/WarcraftPriests/sl-shadow-priest/wiki/Config-File) for more information.

### Create profiles
1. Run `python profiles.py dir/ [--ptr, --dungeons, --talents [am, stm, hv], --covenant [kyrian, necrolord, night_fae, venthyr]]` for the directory you want to sim. Current talent options are indicated by the config keys under: `builds`. If you don't specify `talents` or `covenant` and that sim uses it based on config, all combinations will be automatically generated.

### Simulate
#### Use raidbots
1. To run the sim in Raidbots create `api_secrets.py` inside the root directory. Set `api_key = 'XXX'`.
2. By default if a file already exists in `output/` or if the weight in `internal/weights.py` is 0, sim.py will skip it.
3. To run the sims use `python sim.py dir/ [--iterations 10000, --dungeons, --talents [am, hv, stm]]` where `dir/` is the sim directory you want to sim. If you don't specify `talents` or `covenant` and that sim uses it based on config, all combinations will be automatically generated.
4. Based on config keys in `analyze` markdown, csv, and json will be generated for the aggregated sims. These will output separate files for Composite, Single Target, or Dungeon sims. You can find all output files in the `results/` folder in any sim folder.

#### Use local simc
1. To run with a local simc you have to options:
    1. use the simc you have on your Path ( nothing to setup here)
    2. use a simc located in a seperated folder, create a `local_secrets.py` inside the root directory and set `simc_path = '{"nightly": "path/to/exectuable", "rework": "another/path"}'`
- We use a dict here to support different `simcVersions` like raidbots, you can so define a different simc installation by every key you define.
- If you don't supply the `local_secrets.py` we will use the simc on the path for every different `simcVersion` defined in `config.yml`.

2. By default if a file already exists in `output/` or if the weight in `internal/weights.py` is 0, sim.py will skip it.
3. To run the sims use `python sim.py dir/ [--iterations 10000, --dungeons, --talents [am, hv, stm] --local]` where `dir/` is the sim directory you want to sim. If you don't specify `talents` or `covenant` and that sim uses it based on config, all combinations will be automatically generated.
4. Based on config keys in `analyze` markdown, csv, and json will be generated for the aggregated sims. These will output separate files for Composite, Single Target, or Dungeon sims. You can find all output files in the `results/` folder in any sim folder.

### General Order of sims to run
The following is a rough order to follow when running sims. Generally the things on the same row can be run at the same time since they do not influence each other.

1. Consumables, Enchants, Stats, Trinkets, and Racials
2. Conduits
3. Legendaries (update conduits as needed from #2)
4. Soulbinds & Soulbinds-Launch (update conduits and legendaries as needed from #2 and #3)
5. Covenants & Covenant-Choice (update conduits, legendaries, and soulbinds as needed from #2, #3, and #4)
6. Weights (add top covenant builds from #5)

## Output Formats
Based on `config.yml` sim results will output in up to 3 different formats: Markdown, CSV, and JSON. The files are all located in the `results/` folder of each sim type. The following sections go over how the data is listed here. Each output file is made up into various sections based on how the sim is configured. There are several layers of results.

### Layers
- Sim Type
    - Composite
    - Dungeons
    - Single
- Talents
- Covenant

These layers are used to create the file name. So if a sim is run with default setup without talent builds or covenants it will just be `Results_SIMTYPE` i.e. `Results_Composite.md`. If the sim is ran with talents this is augmented with that talent build (see config for current builds) i.e.`Results_Composite_am.md`. The last layer is Covenant ability, which sims for each individual covenant on top of this i.e. `Results_Composite_am_kyrian`.

### Markdown
The markdown files are broken up and contain easy layer name at the top as a header. Each file is just a simple table broken up by Actor, DPS, and the Increase of that actor against the `Base` actor.

### CSV
The CSV files are the simplest of the bunch, the only trick is that we parse the sim type profile as the start of the row. So a row is simply `profile,actor,DPS,increase,`.

### JSON
JSON files contain the most rich information about the results. The basic structure is as follows:

```json
{
    "name": "SIMTYPE - TALENT - COVENANT",
    "data": {
        "ACTOR": {
            "DPS": 1234
        },
    },
    "ids": {
        "ACTOR": null,
    },
    "simulated_steps": [
        "DPS"
    ],
    "sorted_data_keys": [
        "ACTOR",
    ],
    "last_updated": "YYYY-MM-DD"
}
```

- Name: simple name of the sim containing all relevant information about the data
- Data: this contains the sorted result list of each actor. The content of this will depend on the data itself as defined in `config`. For most sims this will just be a single entry for `DPS` as the step, but for things like trinkets this will be a step for each ilevel i.e. `420`, `425`.
- IDs: This will contain rich information for each actor to be used to generate tooltip data. There are several different ways to lookup this data, namely `spell`, `item`, or `none`. This `lookupType` is defined for each type of sim in `config`. Spell type will use [this file](https://github.com/WarcraftPriests/sl-shadow-priest/blob/master/internal/spell_ids.py) that links actor names to spell IDs to populate this. The item type searches in `.simc` files of the sim for the corresponding actor name and adds the ID it finds on that line.
- Simulated Steps: This just enumerates the steps used in `data`
- Sorted Data Keys: This list is sorted by maximum dps in order.
- Last Updated: simply contains the timestamp that the chart was generated