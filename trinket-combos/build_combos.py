"""
builds trinket strings
python build_combos.py
"""

from itertools import combinations
# pylint: disable=line-too-long

combos = {
    "Forbidden_Necromantic_Tome_259": "forbidden_necromantic_tome,id=186421,ilevel=259",
    "Forbidden_Necromantic_Tome_246": "forbidden_necromantic_tome,id=186421,ilevel=246",
    "Tome_of_Monstrous_Constructions_252": "tome_of_monstrous_constructions,id=186422,ilevel=252",
    "Tome_of_Monstrous_Constructions_239": "tome_of_monstrous_constructions,id=186422,ilevel=239",
    "Titanic_Ocular_Gland_252": "titanic_ocular_gland,id=186423,ilevel=252",
    "Titanic_Ocular_Gland_239": "titanic_ocular_gland,id=186423,ilevel=239",
    "Shadowed_Orb_of_Torment_252": "shadowed_orb_of_torment,id=186428,ilevel=252",
    "Shadowed_Orb_of_Torment_239": "shadowed_orb_of_torment,id=186428,ilevel=239",
    "Ebonsoul_Vise_252": "ebonsoul_vise,id=186431,ilevel=252",
    "Ebonsoul_Vise_239": "ebonsoul_vise,id=186431,ilevel=239",
    "Empyreal_Ordnance_252": "empyreal_ordnance,id=180117,ilevel=252",
    "Empyreal_Ordnance_242": "empyreal_ordnance,id=180117,ilevel=242",
    "Inscrutable_Quantum_Device_252": "inscrutable_quantum_device,id=179350,ilevel=252",
    "Inscrutable_Quantum_Device_246": "inscrutable_quantum_device,id=179350,ilevel=246",
    "Soulletting_Ruby_252": "soulletting_ruby,id=178809,ilevel=252",
    "Soulletting_Ruby_246": "soulletting_ruby,id=178809,ilevel=246",
    "Unbound_Changeling_Mastery_252": "unbound_changeling,id=178708,ilevel=252",
    "Unbound_Changeling_Mastery_246": "unbound_changeling,id=178708,ilevel=246",
    "Unbound_Changeling_Haste_252": "unbound_changeling,id=178708,ilevel=252",
    "Unbound_Changeling_Haste_246": "unbound_changeling,id=178708,ilevel=246",
    "Moonlit_Prism_246": "moonlit_prism,id=137541,ilevel=246",
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
