"""
builds trinket strings
python build_combos.py
"""

from itertools import combinations
# pylint: disable=line-too-long

combos = {
    "Forbidden_Necromantic_Tome_259": "forbidden_necromantic_tome,id=186421,ilevel=259",
    "Titanic_Ocular_Gland_252": "titanic_ocular_gland,id=186423,ilevel=252",
    "Shadowed_Orb_of_Torment_252": "shadowed_orb_of_torment,id=186428,ilevel=252",
    "Empyreal_Ordnance_278": "empyreal_ordnance,id=180117,ilevel=278",
    "Empyreal_Ordnance_262": "empyreal_ordnance,id=180117,ilevel=262",
    "Inscrutable_Quantum_Device_278": "inscrutable_quantum_device,id=179350,ilevel=278",
    "Inscrutable_Quantum_Device_262": "inscrutable_quantum_device,id=179350,ilevel=262",
    "Soulletting_Ruby_278": "soulletting_ruby,id=178809,ilevel=278",
    "Soulletting_Ruby_262": "soulletting_ruby,id=178809,ilevel=262",
    "Unbound_Changeling_Mastery_278": "unbound_changeling,id=178708,ilevel=278",
    "Unbound_Changeling_Mastery_262": "unbound_changeling,id=178708,ilevel=262",
    "Unbound_Changeling_Haste_278": "unbound_changeling,id=178708,ilevel=278",
    "Unbound_Changeling_Haste_262": "unbound_changeling,id=178708,ilevel=262",
    "Resonant_Reservoir_265": "resonant_reservoir,id=188272,ilevel=265",
    "Resonant_Reservoir_278": "resonant_reservoir,id=188272,ilevel=278",
    "Elegy_of_the_Eternals_265": "elegy_of_the_eternals,id=188270,ilevel=265",
    "Elegy_of_the_Eternals_278": "elegy_of_the_eternals,id=188270,ilevel=278",
    "The_First_Sigil_265": "the_first_sigil,id=188271,ilevel=265",
    "The_First_Sigil_278": "the_first_sigil,id=188271,ilevel=278",
    "Architects_Ingenuity_Core_265": "architects_ingenuity_core,id=188268,ilevel=265",
    "Architects_Ingenuity_Core_278": "architects_ingenuity_core,id=188268,ilevel=278",
    "Grim_Eclipse_272": "grim_eclipse,id=188254,ilevel=272",
    "Grim_Eclipse_285": "grim_eclipse,id=188254,ilevel=285",
    "Scars_of_Fraternal_Strife_272": "scars_of_fraternal_strife,id=188253,ilevel=272",
    "Scars_of_Fraternal_Strife_285": "scars_of_fraternal_strife,id=188253,ilevel=285",
    "Moonlit_Prism_272": "moonlit_prism,id=137541,ilevel=272"
}


def item_id(trinket):
    """given a comma-separated definition for a trinket, returns just the id"""
    i = trinket.split(",")[1]
    return i[3:]


def build_combos():
    """generates the combination list with unique equipped trinkets only"""
    trinkets = combinations(combos.keys(), 2)
    unique_trinkets = []
    for pair in trinkets:
        # check if item id matches, trinkets are unique
        if item_id(combos[pair[0]]) != item_id(combos[pair[1]]):
            unique_trinkets.append(pair)
    print(f"Generated {len(unique_trinkets)} combinations.")
    return unique_trinkets


def build_simc_string(trinkets):
    """build profileset for each trinket combination"""
    result = ""
    for combo in trinkets:
        for trinket in combo:
            trinket_one = combo[0]
            trinket_two = combo[1]
            trinket_one_value = combos[trinket_one]
            trinket_two_value = combos[trinket_two]
            profileset_name = f"{trinket_one}-{trinket_two}"
            if "Cabalists_Hymnal_Allies" in trinket:
                allies_count = trinket[24]
                result += f"profileset.\"{profileset_name}\"+=shadowlands.crimson_choir_in_party={allies_count}\n"
            if "Unbound_Changeling" in trinket:
                stat_type = trinket.split("_")[2].lower()
                result += f"profileset.\"{profileset_name}\"+=shadowlands.unbound_changeling_stat_type={stat_type}\n"
        result += f"profileset.\"{profileset_name}\"+=trinket1={trinket_one_value}\n"
        result += f"profileset.\"{profileset_name}\"+=trinket2={trinket_two_value}\n\n"
    return result


def generate_sim_file(input_string):
    """reads in the base simc file and creates the generated.simc file"""
    with open("base.simc", 'r', encoding="utf8") as file:
        data = file.read()
        file.close()
    with open("generated.simc", 'w+', encoding="utf8") as file:
        file.writelines(data)
        file.writelines(input_string)


if __name__ == '__main__':
    trinket_combos = build_combos()
    SIMC_STRING = build_simc_string(trinket_combos)
    generate_sim_file(SIMC_STRING)
