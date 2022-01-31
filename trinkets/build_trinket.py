"""
builds trinket strings
python build_trinket.py Empyreal_Ordnance 180117 158 226
"""
import argparse
import numpy


def build_range(min_ilevel, max_ilevel):
    """build the numpy range"""
    return numpy.arange(min_ilevel, (max_ilevel + 5), 3)


def build_trinket(name, item_id, ilevel):
    """build the correct trinket string"""
    item_name = name.lower()
    return f"profileset.\"{name}_{ilevel}\"+=trinket1={item_name},id={item_id},ilevel={ilevel}"


def build_trinket_with_options(name, item_id, ilevel, options):
    """builds a trinket but with an additional option in the name"""
    trinkets = []
    if name == "Inscrutable_Quantum_Device_Only_Opener":
        trinkets.append(build_trinket(name, item_id, ilevel))
        trinkets.append(build_option(name, ilevel, options[0]))
    else:
        for option in options:
            trinkets.append(build_trinket(name + "_" + option, item_id, ilevel))
            trinkets.append(build_option(name, ilevel, option))
    return trinkets


def build_option(name, ilevel, option):
    # pylint: disable=line-too-long
    """build additional option into the profileset"""
    if name == "Soleahs_Secret_Technique":
        return f"profileset.\"{name}_{option}_{ilevel}\"+=shadowlands.soleahs_secret_technique_type={option.lower()}"
    if name == "Unbound_Changeling":
        return f"profileset.\"{name}_{option}_{ilevel}\"+=shadowlands.unbound_changeling_stat_type={option.lower()}"
    if name == "Inscrutable_Quantum_Device_Only_Opener":
        return f"profileset.\"{name}_{ilevel}\"+=shadowlands.iqd_stat_fail_chance={option}"
    return ""


def main():
    """main function"""
    parser = argparse.ArgumentParser(description='Creates a trinket string')
    parser.add_argument(
        'name', help='Name of the trinket to build: Trinket_Name')
    parser.add_argument('id', help='id of the item')
    parser.add_argument('min_ilevel', help='min ilevel to build items for')
    parser.add_argument('max_ilevel', help='max ilevel to build items for')
    args = parser.parse_args()

    # Shadowlands ilvls are not static
    # ilevel_range = build_range(int(args.min_ilevel), int(args.max_ilevel))
    ilevel_range = [236, 239, 242, 246, 249, 252,
                    255, 259, 262, 265, 268, 272, 275, 278]
    trinket_list = []
    for ilevel in ilevel_range:
        if ilevel < int(args.min_ilevel) or ilevel > int(args.max_ilevel):
            continue
        if args.name == "Soleahs_Secret_Technique":
            trinket_list.extend(build_trinket_with_options(
                args.name, args.id, ilevel, ['Haste', 'Versatility', 'Crit', 'Mastery']))
        elif args.name == "Unbound_Changeling":
            trinket_list.extend(build_trinket_with_options(
                args.name, args.id, ilevel, ['Haste', 'Crit', 'Mastery', 'All']))
        elif args.name == "Inscrutable_Quantum_Device_Only_Opener":
            trinket_list.extend(build_trinket_with_options(
                args.name, args.id, ilevel, [1.0]))
        else:
            trinket_list.append(build_trinket(args.name, args.id, ilevel))

    trinket_list.sort()
    for trinket in trinket_list:
        print(trinket)


if __name__ == "__main__":
    main()
