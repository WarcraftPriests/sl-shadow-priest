"""
builds trinket strings
python build_combos.py
"""

from itertools import combinations
# pylint: disable=line-too-long

combos = {
    # dungeons
    "Moonlit_Prism_298": "moonlit_prism,id=137541,ilevel=298",
    "Soleahs_Secret_Technique_Haste_298": "soleahs_secret_technique_haste,id=190958,ilevel=298",
    "Soleahs_Secret_Technique_Mastery_298": "soleahs_secret_technique_mastery,id=190958,ilevel=298",
    "Soleahs_Secret_Technique_Haste_304": "soleahs_secret_technique_haste,id=190958,ilevel=304",
    "Soleahs_Secret_Technique_Mastery_304": "soleahs_secret_technique_mastery,id=190958,ilevel=304",
    "Tovras_Lightning_Repository_298": "tovras_lightning_repository,id=110001,ilevel=298",
    "Tovras_Lightning_Repository_304": "tovras_lightning_repository,id=110001,ilevel=304",
    # castle nathria
    "Cabalists_Hymnal_Allies_0_298": "cabalists_hymnal,id=184028,ilevel=298",
    "Cabalists_Hymnal_Allies_4_298": "cabalists_hymnal,id=184028,ilevel=298",
    "Cabalists_Hymnal_Allies_0_311": "cabalists_hymnal,id=184028,ilevel=311",
    "Cabalists_Hymnal_Allies_4_311": "cabalists_hymnal,id=184028,ilevel=311",
    # sanctum of domination
    "Titanic_Ocular_Gland_291": "titanic_ocular_gland,id=186423,ilevel=291",
    "Titanic_Ocular_Gland_304": "titanic_ocular_gland,id=186423,ilevel=304",
    "Forbidden_Necromantic_Tome_298": "forbidden_necromantic_tome,id=186421,ilevel=298",
    "Forbidden_Necromantic_Tome_311": "forbidden_necromantic_tome,id=186421,ilevel=311",
    "Shadowed_Orb_of_Torment_291": "shadowed_orb_of_torment,id=186428,ilevel=291",
    "Shadowed_Orb_of_Torment_304": "shadowed_orb_of_torment,id=186428,ilevel=304",
    # sepulcher of the first ones
    "Elegy_of_the_Eternals_291": "elegy_of_the_eternals,id=188270,ilevel=291",
    "Elegy_of_the_Eternals_304": "elegy_of_the_eternals,id=188270,ilevel=304",
    "The_First_Sigil_291": "the_first_sigil,id=188271,ilevel=291",
    "The_First_Sigil_304": "the_first_sigil,id=188271,ilevel=304",
    "Scars_of_Fraternal_Strife_298": "scars_of_fraternal_strife,id=188253,ilevel=298",
    "Scars_of_Fraternal_Strife_311": "scars_of_fraternal_strife,id=188253,ilevel=311",
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
            if "Soleahs_Secret_Technique" in trinket:
                stat_type = trinket.split("_")[3].lower()
                result += f"profileset.\"{profileset_name}\"+=shadowlands.soleahs_secret_technique_type={stat_type}\n"
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
