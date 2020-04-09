import pandas


def build_output_string(directory, sim_type, talent_string, file_type):
    return "{0}Results_{1}{2}.{3}".format(directory, sim_type, talent_string, file_type)


def get_change(current, previous):
    negative = 0
    if current < previous:
        negative = True
    try:
        value = (abs(current - previous) / previous) * 100.0
        value = float('%.2f' % value)
        if value >= 0.01 and negative:
            value = value * -1
        return value
    except ZeroDivisionError:
        return 0


def build_results(data, weights):
    results = {}
    for value in data.iterrows():
        profile = value[1].profile
        weighted_dps = value[1].DPS
        intellect = value[1].int
        if weights:
            haste = value[1].haste / intellect
            crit = value[1].crit / intellect
            mastery = value[1].mastery / intellect
            vers = value[1].vers / intellect
            wdps = 1 / intellect
            weight = 1
            results[value[1].actor] = [weighted_dps, weight, haste, crit, mastery, vers, wdps]
        else:
            results[value[1].actor] = weighted_dps
    return results


def build_markdown(directory, sim_type, talent_string, results, weights):
    output_file = build_output_string(directory, sim_type, talent_string, "md")
    # with open(output_file, 'w') as results_md:
    #     if weights:
    #         results_md.write()


def analyze(talents, directory, dungeons, weights):
    csv = "{0}results/statweights.csv".format(directory)
    if weights:
        data = pandas.read_csv(csv,
                               usecols=['profile', 'actor', 'DD', 'DPS', 'int', 'haste', 'crit', 'mastery', 'vers'])
    else:
        data = pandas.read_csv(csv, usecols=['profile', 'actor', 'DD', 'DPS'])
    results = build_results(data, weights)
    base_dps = results.get('Base')

    if talents:
        talent_string = "_{0}".format(talents)
    else:
        talent_string = ""

    if dungeons:
        sim_types = ["Dungeons"]
    else:
        sim_types = ["Composite", "Single"]

    for sim_type in sim_types:
        build_markdown(directory, sim_type, talent_string, results, weights)
        # build_csv(directory, sim_type, talent_string, results, weights)
        # build_json(directory, sim_type, talent_string, results, weights)
