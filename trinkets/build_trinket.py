import argparse
import numpy


def build_range(min_ilevel, max_ilevel):
    return numpy.arange(min_ilevel, (max_ilevel + 5), 5)


def build_trinket(name, item_id, ilevel):
    item_name = name.lower()
    return "profileset.\"{0}_{2}\"+=trinket1={3},id={1},ilevel={2}".format(name, item_id, ilevel, item_name)


def main():
    parser = argparse.ArgumentParser(description='Creates a trinket string')
    parser.add_argument('name', help='Name of the trinket to build: Trinket_Name')
    parser.add_argument('id', help='id of the item')
    parser.add_argument('min_ilevel', help='min ilevel to build items for')
    parser.add_argument('max_ilevel', help='max ilevel to build items for')
    args = parser.parse_args()

    ilevel_range = build_range(int(args.min_ilevel), int(args.max_ilevel))
    trinket_list = []
    for ilevel in ilevel_range:
        trinket_list.append(build_trinket(args.name, args.id, ilevel))

    for trinket in trinket_list:
        print(trinket)


if __name__ == "__main__":
    main()
