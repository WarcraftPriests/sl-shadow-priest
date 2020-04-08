from optparse import OptionParser
import os
import json
from os import path


def parse(filename, isCsv, hideHeaders, hideProfiles, hideActors, dpsOnly):
    separator = ',' if isCsv else '\t'
    if (hideHeaders):
        ret = ''
    else:
        ret = filename + '\n'
        ret += 'actor' + separator + 'DD' + separator + 'DPS\n'
        if not dpsOnly:
            ret += separator + 'int' + separator + 'haste' + separator + 'crit' + separator + 'mastery' + separator + 'vers\n'
    with open(filename, "r") as f:
        s = f.read()
        sim = json.loads(s)
        results = sim['sim']['players']
        for player in sorted(results, key=lambda k: k['name']):
            if dpsOnly or 'Int' in player['scale_factors']:
                if (not hideProfiles):
                    ret += path.splitext(filename)[0] + separator
                if (not hideActors):
                    ret += player['name'] + separator
                ret += '{0:.{1}f}'.format(player['collected_data']['dmg']['mean'], 2) + separator
                ret += '{0:.{1}f}'.format(player['collected_data']['dps']['mean'], 2) + separator
                if not dpsOnly:
                    weights = player['scale_factors']
                    ret += '{0:.{1}f}'.format(weights['Int'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Haste'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Crit'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Mastery'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Vers'], 2)
                ret += '\n'
    if 'profilesets' in sim['sim']:
        ret += parseProfileSets(filename, isCsv, hideHeaders, hideProfiles, hideActors, dpsOnly)
    return ret + '\n' if not hideHeaders else ret


def parseProfileSets(filename, isCsv, hideHeaders, hideProfiles, hideActors, dpsOnly):
    separator = ',' if isCsv else '\t'
    ret = ''
    with open(filename, "r") as f:
        s = f.read()
        sim = json.loads(s)
        results = sim['sim']['profilesets']['results']
        for profile in sorted(results, key=lambda k: k['name']):
            if dpsOnly or 'Int' in profile['scale_factors']:
                if not hideProfiles:
                    ret += path.splitext(filename)[0] + separator
                if not hideActors:
                    ret += profile['name'] + separator
                ret += '{0:.{1}f}'.format(0, 2) + separator
                ret += '{0:.{1}f}'.format(profile['mean'], 2) + separator
                if not dpsOnly:
                    weights = profile['scale_factors']
                    ret += '{0:.{1}f}'.format(weights['Int'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Haste'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Crit'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Mastery'], 2) + separator
                    ret += '{0:.{1}f}'.format(weights['Vers'], 2)
                ret += '\n'
    return ret + '\n' if not hideHeaders else ret


def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-d", "--directory", dest="directory", default=None, help="the target directory")
    parser.add_option("-p", "--prefix", dest="prefix", default='', help="the target files prefix")
    parser.add_option("-o", "--output", dest="output", default='statweights.txt',
                      help="the output file to be created. Will overwrite if the file already exists")
    parser.add_option("-c", "--csv", action="store_true", dest="csv", default=False,
                      help="Checks if the output file should be in the CSV format or TXT")
    parser.add_option("-r", "--hide-headers", action="store_true", dest="hideHeaders", default=False,
                      help="hides the headers from files for better sheet export")
    parser.add_option("-a", "--hide-actors", action="store_true", dest="hideActors", default=False,
                      help="hides the actors column in the output file")
    parser.add_option("-f", "--hide-profiles", action="store_true", dest="hideProfiles", default=False,
                      help="hides the profiles column in the output file")
    parser.add_option("-s", "--dps-only", action="store_true", dest="dpsOnly", default=False,
                      help="extracts only the DPS from the profiles")

    (options, args) = parser.parse_args()

    if options.directory is not None:
        os.chdir(options.directory)

    separator = ',' if options.csv else '\t'

    parses = ''
    if options.hideHeaders:
        if not options.hideProfiles:
            parses += 'profile' + separator
        if not options.hideActors:
            parses += 'actor' + separator
        if not options.dpsOnly:
            parses += 'DD' + separator + 'DPS' + separator + 'int' + separator + 'haste' + separator + 'crit' + separator + 'mastery' + separator + 'vers\n'
        else:
            parses += 'DD' + separator + 'DPS\n'

    for filename in os.listdir(os.getcwd()):
        if filename.startswith(options.prefix) and filename.endswith('.json'):
            parses += parse(filename, options.csv, options.hideHeaders, options.hideProfiles, options.hideActors,
                            options.dpsOnly)

    with open(options.output, "w") as ofile:
        print(parses, file=ofile)


if __name__ == "__main__":
    main()
