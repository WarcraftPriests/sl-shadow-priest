"""
builds trinket strings
python build_combos.py
"""

from itertools import combinations

combos = {
    "Soul_Igniter_213": "soul_igniter,id=184019,ilevel=213",
    "Soul_Igniter_226": "soul_igniter,id=184019,ilevel=226",
    "Glyph_of_Assimilation_213": "glyph_of_assimilation,id=184021,ilevel=213",
    "Glyph_of_Assimilation_226": "glyph_of_assimilation,id=184021,ilevel=226",
    "Macabre_Sheet_Music_213": "macabre_sheet_music,id=184024,ilevel=213",
    "Macabre_Sheet_Music_226": "macabre_sheet_music,id=184024,ilevel=226",
    "Cabalists_Hymnal_Allies_0_220": "cabalists_hymnal,id=184028,ilevel=220",
    "Cabalists_Hymnal_Allies_0_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_1_220": "cabalists_hymnal,id=184028,ilevel=220",
    "Cabalists_Hymnal_Allies_1_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_2_220": "cabalists_hymnal,id=184028,ilevel=220",
    "Cabalists_Hymnal_Allies_2_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_3_220": "cabalists_hymnal,id=184028,ilevel=220",
    "Cabalists_Hymnal_Allies_3_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Cabalists_Hymnal_Allies_4_220": "cabalists_hymnal,id=184028,ilevel=220",
    "Cabalists_Hymnal_Allies_4_233": "cabalists_hymnal,id=184028,ilevel=233",
    "Dreadfire_Vessel_220": "dreadfire_vessel,id=184030,ilevel=220",
    "Dreadfire_Vessel_233": "dreadfire_vessel,id=184030,ilevel=233",
    "Empyreal_Ordnance_210": "empyreal_ordnance,id=180117,ilevel=210",
    "Empyreal_Ordnance_226": "empyreal_ordnance,id=180117,ilevel=226",
    "Inscrutable_Quantum_Device_210": "inscrutable_quantum_device,id=179350,ilevel=210",
    "Inscrutable_Quantum_Device_226": "inscrutable_quantum_device,id=179350,ilevel=226",
    "Soulletting_Ruby_226": "soulletting_ruby,id=178809,ilevel=226",
    "Soulletting_Ruby_210": "soulletting_ruby,id=178809,ilevel=210",
    "Sinful_Gladiators_Insignia_of_Alacrity_226": "sinful_gladiators_insignia_of_alacrity,id=178386,ilevel=226"
}


def build_combos():
    """generates the combination list with unique equipped trinkets only"""
    trinkets = combinations(combos.keys(), 2)
    unique_trinkets = []
    for pair in trinkets:
        # check if name matches, trinkets are unique
        if pair[0][:-5] != pair[1][:-5]:
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
    simc_string = build_simc_string(trinket_combos)
    generate_sim_file(simc_string)
