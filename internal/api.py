"""submits sims to raidbots and waits for the result"""
import json
import time
import requests
import yaml

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


def submit_sim(api_url_base, api_key, profile_location, simc_build, report_name, iterations):
    # pylint: disable=too-many-arguments, too-many-return-statements, too-many-locals
    """submits a sim to the raidbots api"""
    if iterations != "smart":
        iterations = int(iterations)
    simc_file = open(profile_location, 'r')
    simc_input = simc_file.read()
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Publik\'s Raidbots API Script'
    }
    api_url = '{0}/sim'.format(api_url_base)
    data = {
        'apiKey': api_key,
        'type': 'advanced',
        'advancedInput': simc_input,
        'simcVersion': simc_build,
        'reportName': report_name,
        'iterations': iterations,
    }
    num_of_retries = int(config["raidbots"]["numOfRetries"])
    retry_interval = int(config["raidbots"]["retryInterval"])
    current_try = 0

    while True:
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code >= 500:
            current_try += 1
            print('[!] [{0}] Server Error'.format(response.status_code))
            time.sleep(retry_interval * current_try)
            if current_try >= num_of_retries:
                print("Exceeded retries - exiting")
                return None
        elif response.status_code == 429:
            current_try += 1
            print('[!] [{0}] Too many API jobs running"'.format(
                response.status_code))
            time.sleep(retry_interval * current_try)
            if current_try >= num_of_retries:
                print("Exceeded retries - exiting")
                return None
        elif response.status_code == 404:
            print('[!] [{0}] URL not found: [{1}]'.format(
                response.status_code, api_url))
            return None
        elif response.status_code == 401:
            print('[!] [{0}] Authentication Failed'.format(
                response.status_code))
            return None
        elif response.status_code >= 400:
            print('[!] [{0}] Bad Request'.format(response.status_code))
            print(data)
            print(response.content)
            return None
        elif response.status_code == 200:
            sim = json.loads(response.content)
            return sim
        else:
            print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))
            return None


def poll_status(api_url_base, sim_id):
    """polls the raidbots api to get status of a sim"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Publik\'s Raidbots API Script'
    }
    api_url = '{0}/api/job/{1}'.format(api_url_base, sim_id)
    num_of_retries = int(config["raidbots"]["numOfRetries"])
    retry_interval = int(config["raidbots"]["retryInterval"])
    current_try = 0
    while True:
        response = requests.get(api_url, headers=headers)
        if response.status_code >= 500:
            current_try += 1
            print('[!] [{0}] Server Error'.format(response.status_code))
            time.sleep(retry_interval * current_try)
            if current_try >= num_of_retries:
                print("Exceeded retries - exiting")
                break
        elif response.status_code == 404:
            print('[!] [{0}] URL not found: [{1}]'.format(
                response.status_code, api_url))
            break
        elif response.status_code == 200:
            sim_status = json.loads(response.content)
            if not 'progress' in sim_status['job']:
                print(
                    "Error getting progress from 200 response json: {0}".format(sim_status))
                break
            progress = sim_status['job']['progress']
            state = sim_status['job']['state']
            if state == "complete":
                print("Sim {0} finished.".format(sim_id))
                break
            elif state == "inactive":
                print("Sim {0} in queue.".format(sim_id))
                time.sleep(retry_interval)
            elif state == "active":
                print("Sim {0} progress: {1}".format(sim_id, progress))
                time.sleep(retry_interval)
            else:
                current_try += 1
                print(
                    "Unknown state: {0} when getting {1}. - Retry {2}".format(
                        state, sim_id, current_try)
                )
                if current_try >= num_of_retries:
                    print("Exceeded retries - exiting")
                    break
        else:
            print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))
            return None


def retrieve_data(api_url_base, sim_id, data_file):
    """get final sim data from raidbots"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Publik\'s Raidbots API Script'
    }
    api_url = '{0}/reports/{1}/{2}'.format(api_url_base, sim_id, data_file)
    num_of_retries = int(config["raidbots"]["numOfRetries"])
    retry_interval = int(config["raidbots"]["retryInterval"])
    current_try = 0

    while True:
        response = requests.get(api_url, headers=headers)
        if response.status_code >= 500:
            current_try += 1
            print('[!] [{0}] Server Error'.format(response.status_code))
            time.sleep(retry_interval * current_try)
            if current_try >= num_of_retries:
                print("Exceeded retries - exiting")
                return None
        elif response.status_code == 404:
            print('[!] [{0}] URL not found: [{1}]'.format(
                response.status_code, api_url))
            return None
        elif response.status_code == 200:
            sim_data = json.loads(response.content)
            return sim_data
        else:
            print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))
            return None


def raidbots(api_key, profile_location, simc_build, output_location, report_name, iterations):
    # pylint: disable=too-many-arguments
    """calls the appropriate functions to run a sim to raidbots"""
    api_url_base = config["raidbots"]["apiUrlBase"]

    # submit initial sim -> get back sim_id
    sim = submit_sim(api_url_base, api_key, profile_location,
                     simc_build, report_name, iterations)
    if sim is not None:
        sim_id = sim['simId']
        # wait for the sim to finish
        poll_status(api_url_base, sim_id)
    else:
        print("Could not find simId in successful response from Raidbots")
    # pull back results from the sim
    sim_data = retrieve_data(api_url_base, sim_id, 'data.json')
    if sim_data is not None:
        # raidbots uses hasFullJson to indicate that there is another file with more info
        if 'hasFullJson' in sim_data['simbot']:
            sim_data = retrieve_data(api_url_base, sim_id, 'data.full.json')
        output_file = open(output_location, 'w')
        output_file.write(json.dumps(sim_data))
        print("Saved results to {0}".format(output_location))
    else:
        print("Error getting data from Raidbots")
