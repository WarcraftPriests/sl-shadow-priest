"""weight dict definitions"""

weightsSepulcherOfTheFirstOnes = {
    'pw_ba_1': 0.009,
    'pw_sa_1': 0.127,
    'pw_na_1': 0.377,
    'lm_ba_1': 0.003,
    'lm_sa_1': 0.048,
    'lm_na_1': 0.138,
    'hm_ba_1': 0.000,
    'hm_sa_1': 0.000,
    'hm_na_1': 0.027,
    'pw_ba_2': 0.027,
    'pw_sa_2': 0.043,
    'pw_na_2': 0.150,
    'lm_ba_2': 0.005,
    'lm_sa_2': 0.000,
    'lm_na_2': 0.036,
    'hm_ba_2': 0.000,
    'hm_sa_2': 0.000,
    'hm_na_2': 0.009,
}

weights_sanctum_of_domination = {
    'pw_ba_1': 0.000,
    'pw_sa_1': 0.055,
    'pw_na_1': 0.570,
    'lm_ba_1': 0.000,
    'lm_sa_1': 0.050,
    'lm_na_1': 0.205,
    'hm_ba_1': 0.000,
    'hm_sa_1': 0.000,
    'hm_na_1': 0.000,
    'pw_ba_2': 0.020,
    'pw_sa_2': 0.020,
    'pw_na_2': 0.050,
    'lm_ba_2': 0.020,
    'lm_sa_2': 0.000,
    'lm_na_2': 0.010,
    'hm_ba_2': 0.000,
    'hm_sa_2': 0.000,
    'hm_na_2': 0.000,
}

weights_castle_nathria = {
    'pw_ba_1': 0.0200000,
    'pw_sa_1': 0.0600000,
    'pw_na_1': 0.2750000,
    'lm_ba_1': 0.0000000,
    'lm_sa_1': 0.0050000,
    'lm_na_1': 0.1700000,
    'hm_ba_1': 0.0000000,
    'hm_sa_1': 0.0000000,
    'hm_na_1': 0.0500000,
    'pw_ba_2': 0.0400000,
    'pw_sa_2': 0.0400000,
    'pw_na_2': 0.1200000,
    'lm_ba_2': 0.0500000,
    'lm_sa_2': 0.0800000,
    'lm_na_2': 0.0800000,
    'hm_ba_2': 0.0000000,
    'hm_sa_2': 0.0000000,
    'hm_na_2': 0.0100000,
}

weights_single = {
    'pw_na_1': 0.69514237856,
    'lm_na_1': 0.25460636516,
    'hm_na_1': 0.05025125628,
}


def find_weights(key):
    """return the matching dict"""
    if key == 'weightsSingle':
        return weights_single
    if key == 'weightsCastleNathria':
        return weights_castle_nathria
    if key == 'weightsSanctumOfDomination':
        return weights_sanctum_of_domination
    if key == 'weightsSepulcherOfTheFirstOnes':
        return weightsSepulcherOfTheFirstOnes
    return None
