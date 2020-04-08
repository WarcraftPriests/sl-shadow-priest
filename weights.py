weightsCastleNathria = {
    'pw_ba_1': 0.0641667,
    'pw_sa_1': 0.0416667,
    'pw_na_1': 0.1508333,
    'lm_ba_1': 0.1558333,
    'lm_sa_1': 0.0291667,
    'lm_na_1': 0.2050000,
    'hm_ba_1': 0.0175000,
    'hm_sa_1': 0.0000000,
    'hm_na_1': 0.0275000,
    'pw_ba_2': 0.0166667,
    'pw_sa_2': 0.0416667,
    'pw_na_2': 0.0083333,
    'lm_ba_2': 0.0333333,
    'lm_sa_2': 0.1833333,
    'lm_na_2': 0.0166667,
    'hm_ba_2': 0.0041667,
    'hm_sa_2': 0.0041667,
    'hm_na_2': 0.0000000,
}

weightsSingle = {
    'pw_na_1': 0.39347826087,
    'lm_na_1': 0.53478260870,
    'hm_na_1': 0.07173913043,
}


def find_weights(key):
    if key == 'weightsSingle':
        return weightsSingle
    elif key == 'weightsCastleNathria':
        return weightsCastleNathria