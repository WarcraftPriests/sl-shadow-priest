weightsCastleNathria = {
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

weightsSingle = {
    'pw_na_1': 0.55555555556,
    'lm_na_1': 0.34343434343,
    'hm_na_1': 0.10101010101,
}


def find_weights(key):
    if key == 'weightsSingle':
        return weightsSingle
    elif key == 'weightsCastleNathria':
        return weightsCastleNathria
