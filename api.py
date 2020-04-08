# USAGE:
# python3 api.py API_KEY test.simc
# file is saved to [simId].json

from __future__ import print_function

import time
import sys
import argparse
import json
import urllib.request
import urllib.parse
from urllib.error import URLError


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


parser = argparse.ArgumentParser()
parser.add_argument("api_key")
parser.add_argument("input_file")
parser.add_argument("--simc_version", default="nightly")
parser.add_argument("output_file")
parser.add_argument("report_name")
parser.add_argument("--iterations", default="smart")
args = parser.parse_args()

HOST = 'https://www.raidbots.com'

SIM_SUBMIT_URL = "%s/sim" % HOST

simc_file = open(args.input_file, 'r')
simc_input = simc_file.read()

num_of_retries = 2
time_interval = 20

reportName = args.input_file[:8] + args.output_file[16:-5]

if args.iterations == "smart":
    iterations = "smart"
else:
    iterations = int(args.iterations)

data = {
    'apiKey': args.api_key,
    'type': 'advanced',
    'advancedInput': simc_input,
    'simcVersion': args.simc_version,
    'reportName': args.report_name,
    'iterations': iterations,
}
body = json.dumps(data).encode('utf8')

res = None
try:
    eprint("Submitting " + args.report_name)
    req = urllib.request.Request(
        SIM_SUBMIT_URL,
        data=body,
        headers={
            'content-type': 'application/json',
            'User-Agent': 'Publik\'s Raidbots API Script'
        }
    )
    res = urllib.request.urlopen(req)
except urllib.error.URLError as e:
    print(e.reason)
    sys.exit(1)

sim = json.loads(res.read().decode('utf8'))
simId = sim['simId']

eprint('simId is %s' % simId)

while True:
    req = urllib.request.Request(
        "%s/api/job/%s" % (HOST, simId),
        headers={
            'content-type': 'application/json',
            'User-Agent': 'Publik\'s Raidbots API Script'
        }
    )
    for _ in range(num_of_retries):
        try:
            res = urllib.request.urlopen(req)
            break
        except urllib.error.URLError as e:
            print(e.reason)
            time.sleep(time_interval)
    else:
        raise Exception
    sim_status = json.loads(res.read().decode('utf8'))
    progress = sim_status['job']['progress']
    state = sim_status['job']['state']
    if state == "complete":
        eprint('Done')
        break
    if state == "inactive":
        eprint('In Queue')
    if state == "active":
        eprint('Progress: %s' % progress)

    time.sleep(time_interval)

eprint('Retrieving result')

req = urllib.request.Request(
    "%s/reports/%s/data.json" % (HOST, simId),
    headers={
        'User-Agent': 'Publik\'s Raidbots API Script'
    }
)
res = urllib.request.urlopen(req)
sim_data = json.loads(res.read().decode('utf8'))
if 'hasFullJson' in sim_data['simbot']:
    req = urllib.request.Request(
        "%s/reports/%s/data.full.json" % (HOST, simId),
        headers={
            'User-Agent': 'Publik\'s Raidbots API Script'
        }
    )
    res = urllib.request.urlopen(req)
    sim_data = json.loads(res.read().decode('utf8'))
output_file = open(args.output_file, 'w')
output_file.write(json.dumps(sim_data))

eprint('Result saved to %s' % args.output_file)
