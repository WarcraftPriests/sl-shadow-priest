'Markdown (.md) file writer'

import operator

from internal.writers.common import build_output_string, generate_report_name, get_change


def build_markdown(sim_type, talent_string, results, base_path, weights, base_dps, covenant_string):
    # pylint: disable=too-many-arguments
    """converts result data into markdown files"""
    output_file = build_output_string(base_path,
        sim_type, talent_string, covenant_string, "md")
    with open(output_file, 'w+') as results_md:
        if weights:
            results_md.write(
                '# {0}\n| Actor | DPS | Int | Haste | Crit | Mastery | Vers | DPS Weight '
                '|\n|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n'.format(
                    generate_report_name(sim_type, talent_string, covenant_string
                                         )))
            # Take the dict of dicts and created a new dict to be able to sort our keys
            actor_dps = {}
            for key, value in results.items():
                actor_dps[key] = value.get('dps')
            # sort the keys in the actor_dps dict by the dps value
            # use that key to lookup the actual dict of values
            for key, value in sorted(actor_dps.items(), key=operator.itemgetter(1), reverse=True):
                results_md.write("|%s|%.0f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|\n" % (
                    key,
                    results[key].get('dps'),
                    results[key].get('intellect'),
                    results[key].get('haste'),
                    results[key].get('crit'),
                    results[key].get('mastery'),
                    results[key].get('vers'),
                    results[key].get('wdps'))
                )
        else:
            results_md.write('# {0}\n| Actor | DPS | Increase |\n|---|:---:|:---:|\n'.format(
                generate_report_name(sim_type, talent_string, covenant_string)))
            for key, value in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
                results_md.write("|%s|%.0f|%.2f%%|\n" %
                                 (key, value, get_change(value, base_dps)))
