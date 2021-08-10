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
    "Cabalists_Hymnal_Allies_0_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_1_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_2_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_3_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_4_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Shadowed_Orb_of_Torment_252": "shadowed_orb_of_torment,id=186428,ilevel=252",
    "Shadowed_Orb_of_Torment_239": "shadowed_orb_of_torment,id=186428,ilevel=239",
    "Ebonsoul_Vise_252": "ebonsoul_vise,id=186431,ilevel=252",
    "Ebonsoul_Vise_239": "ebonsoul_vise,id=186431,ilevel=239",
    "Empyreal_Ordnance_252": "empyreal_ordnance,id=180117,ilevel=252",
    "Empyreal_Ordnance_236": "empyreal_ordnance,id=180117,ilevel=236",
    "Inscrutable_Quantum_Device_252": "inscrutable_quantum_device,id=179350,ilevel=252",
    "Inscrutable_Quantum_Device_236": "inscrutable_quantum_device,id=179350,ilevel=236",
    "Soulletting_Ruby_252": "soulletting_ruby,id=178809,ilevel=252",
    "Soulletting_Ruby_236": "soulletting_ruby,id=178809,ilevel=236",
    "Unbound_Changeling_Mastery_252": "unbound_changeling,id=178708,ilevel=252",
    "Unbound_Changeling_Mastery_236": "unbound_changeling,id=178708,ilevel=236",
    "Unbound_Changeling_Haste_252": "unbound_changeling,id=178708,ilevel=252",
    "Unbound_Changeling_Haste_236": "unbound_changeling,id=178708,ilevel=236",
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
    print("Generated {0} combinations.".format(len(unique_trinkets)))
    return unique_trinkets


def build_simc_string(trinkets):
    """build profileset for each trinket combination"""
    result = ""
    for combo in trinkets:
        for trinket in combo:
            if "Cabalists_Hymnal_Allies" in trinket:
                allies_count = trinket[24]
                result += "profileset.\"{0}-{1}\"+=shadowlands.crimson_choir_in_party={2}\n".format(
                    combo[0], combo[1], allies_count)
            if "Unbound_Changeling" in trinket:
                stat_type = trinket.split("_")[2].lower()
                result += "profileset.\"{0}-{1}\"+=shadowlands.unbound_changeling_stat_type={2}\n".format(
                    combo[0], combo[1], stat_type)
        result += "profileset.\"{0}-{1}\"+=trinket1={2}\n".format(
            combo[0], combo[1], combos[combo[0]])
        result += "profileset.\"{0}-{1}\"+=trinket2={2}\n\n".format(
            combo[0], combo[1], combos[combo[1]])
    return result


def generate_sim_file(input_string):
    """reads in the base simc file and creates the generated.simc file"""
    with open("base.simc", 'r') as file:
        data = file.read()
        file.close()
    with open("generated.simc", 'w+') as file:
        file.writelines(data)
        file.writelines(input_string)


if __name__ == '__main__':
    trinket_combos = build_combos()
    SIMC_STRING = build_simc_string(trinket_combos)
    generate_sim_file(SIMC_STRING)
