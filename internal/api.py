"""submits sims to raidbots and waits for the result"""
import json
import time
import requests
import yaml
import tqdm

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

num_of_retries = int(config["raidbots"]["numOfRetries"])
retry_interval = int(config["raidbots"]["retryInterval"])

session = requests.Session()
session.headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Publik\'s Raidbots API Script'
}


def submit_sim(api_url_base, api_key, profile_location, simc_build, report_name, iterations):
    # pylint: disable=too-many-arguments, too-many-return-statements, too-many-locals
    """submits a sim to the raidbots api"""

    iterations = int(iterations) if iterations != "smart" else iterations
    simc_input = open(profile_location, 'r').read()
    api_url = f'{api_url_base}/sim'
    data = {
        'apiKey': api_key,
        'type': 'advanced',
        'advancedInput': simc_input,
        'simcVersion': simc_build,
        'reportName': report_name,
        'iterations': iterations,
    }

    current_try = 0
    while current_try < num_of_retries:
        response = session.post(api_url, json=data)
        status = response.status_code
        if status >= 500:
            current_try += 1
            print(f'[!] [{status}] Server Error')
            time.sleep(retry_interval * current_try)

        elif status == 429:
            current_try += 1
            print(f'[!] [{status}] Too many API jobs running"')
            time.sleep(retry_interval * current_try)

        elif status == 404:
            print(f'[!] [{status}] URL not found: [{api_url}]')
            return None

        elif status == 401:
            print(f'[!] [{status}] Authentication Failed')
            return None

        elif status >= 400:
            print(f'[!] [{status}] Bad Request')
            print("=== Bad request data ===")
            print(data)
            print(response.content)
            print("=== End bad request data ===")
            return None

        elif status == 200:
            sim = json.loads(response.content)
            return sim

        else:
            print(
                f'[?] Unexpected Error: [HTTP {status}]: Content: {response.content}')
            return None

    # we've exceeded the maximum tries
    print("Exceeded retries - exiting")
    return None


def poll_status(api_url_base, sim_id):
    """polls the raidbots api to get status of a sim"""

    api_url = f'{api_url_base}/api/job/{sim_id}'

    # Disables TQDM monitoring thread
    tqdm.tqdm.monitor_interval = 0

    last_update = 0
    started = False
    current_try = 0

    with tqdm.tqdm(total=100, unit='%', ncols=100) as pbar:
        while current_try < num_of_retries:
            response = session.get(api_url)
            status = response.status_code 
            if status >= 500:
                current_try += 1
                pbar.write(f'[!] [{status}] Server Error')
                time.sleep(retry_interval * current_try)

            elif status == 404:
                pbar.close()
                print(
                    f'[!] [{status}] URL not found: [{api_url}]')
                return

            elif status == 200:
                sim_status = response.json()

                # Check if we have a progress in the job data
                if not 'progress' in sim_status['job']:
                    pbar.close()
                    print(
                        f"Error getting progress from 200 response json: {sim_status}")
                    return

                progress = sim_status['job']['progress']

                # Check if there has been any progress 
                # if so update our progress bar and save that progress.
                diff = progress - last_update
                if diff:
                    last_update = progress
                    pbar.update(diff)

                state = sim_status['job']['state']
                if state == "complete":
                    pbar.close()
                    pbar.write(f"Sim {sim_id} finished.")
                    return

                if state == "inactive":
                    pbar.write(f"Sim {sim_id} in queue.")
                    time.sleep(retry_interval)

                elif state == "active":
                    if not started:
                        pbar.write(f"Sim {sim_id} started.")
                        started = True

                    time.sleep(retry_interval)

                else:
                    current_try += 1
                    print(
                        f"Unknown state: {state} when getting {sim_id}. - Retry {current_try}"
                    )
            else:
                print(
                    f'[?] Unexpected Error: [HTTP {status}]: Content: {response.content}')
                return None

        # we've exceeded the maximum tries
        pbar.write("Exceeded retries - exiting")
        return None


def retrieve_data(api_url_base, sim_id, data_file):
    """get final sim data from raidbots"""

    api_url = f'{api_url_base}/reports/{sim_id}/{data_file}'
    current_try = 0

    while current_try < num_of_retries:
        response = session.get(api_url)
        status = response.status_code
        if status >= 500:
            current_try += 1
            print(f'[!] [{status}] Server Error')
            time.sleep(retry_interval * current_try)

        elif status == 404:
            print(f'[!] [{status}] URL not found: [{api_url}]')
            return None

        elif status == 200:
            sim_data = json.loads(response.content)
            return sim_data

        else:
            print(
                f'[?] Unexpected Error: [HTTP {status}]: Content: {response.content}')
            return None

    print("Exceeded retries - exiting")


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
        print(f"Saved results to {output_location}")
    else:
        print("Error getting data from Raidbots")

if __name__ == "__main__":
    poll_status("https://raidbots.com", "7dRu7se1Hbh3K3EAUneWDH")