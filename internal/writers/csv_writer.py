'CSV (.csv) file writer'
import csv
import operator

from internal.writers.common import build_output_string, get_change


def build_csv(sim_type, talent_string, results, base_path, weights, base_dps, covenant_string):
    # pylint: disable=too-many-arguments
    """build csv from results dict"""

    output_file = build_output_string(base_path,
        sim_type, talent_string, covenant_string, "csv")

    # Explicitly removing the newline here, since its applied via the [csv] module
    with open(output_file, 'w', newline='') as csv_fh:

        if weights:
            headers = ['profile', 'actor', 'DPS', 'int',
                       'haste', 'crit', 'mastery', 'vers', 'dpsW']
            writer = csv.DictWriter(csv_fh, fieldnames=headers)
            writer.writeheader()

            # Take the dict of dicts and created a new dict to be able to sort our keys
            actor_dps = {}
            for key, value in results.items():
                actor_dps[key] = value.get('dps')
            # sort the keys in the actor_dps dict by the dps value
            # use that key to lookup the actual dict of values
            for key, value in sorted(actor_dps.items(), key=operator.itemgetter(1), reverse=True):
                data = results[key]
                writer.writerow({
                    "profile": sim_type,
                    "actor": key,
                    "DPS": int(data.get('dps')),
                    "int": round(float(data.get('intellect')), 2),
                    "haste": round(float(data.get('haste')), 2),
                    "crit": round(float(data.get('crit')), 2),
                    "mastery": round(float(data.get('mastery')), 2),
                    "vers": round(float(data.get('vers')), 2),
                    "dpsW": round(float(data.get('wdps'), 2))
                })
        else:
            headers = ['profile', 'actor', 'DPS', 'increase']
            writer = csv.DictWriter(csv_fh, fieldnames=headers)
            writer.writeheader()

            for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                data = results[key]
                writer.writerow({
                    "profile": sim_type,
                    "actor": key,
                    "DPS": int(value),
                    "increase": round(float(get_change(value, base_dps)), 2)
                })
