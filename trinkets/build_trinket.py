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
    return "profileset.\"{0}_{2}\"+=trinket1={3},id={1},ilevel={2}".format(
        name,
        item_id,
        ilevel,
        item_name
    )


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
    ilevel_range = [209, 213, 216, 220, 223,
                    226, 233, 236, 239, 242, 246, 249, 252]
    trinket_list = []
    for ilevel in ilevel_range:
        if ilevel < int(args.min_ilevel) or ilevel > int(args.max_ilevel):
            continue
        trinket_list.append(build_trinket(args.name, args.id, ilevel))

    for trinket in trinket_list:
        print(trinket)


if __name__ == "__main__":
    main()
