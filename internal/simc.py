import subprocess
import os

def sim_local(simc_path, profile_location, output_location):
    resultList = output_location.split("/")
    update_profile(profile_location, resultList[-1])
    subprocess.run([simc_path, profile_location])
    try:
        os.rename(resultList[-1], output_location)
    except FileNotFoundError:
        print("{0} was not created (error in sim). Skipping file.".format(resultList[-1]))


def update_profile(profile_location, report_name):
    if check_for_existing_json(profile_location, report_name):
        with open(profile_location, 'a+') as file:
            file.write("json2={0}\n".format(report_name))
    
def check_for_existing_json(profile_location, report_name):
    with open(profile_location) as file:
        if "json2={0}".format(report_name) in file.read():
            return False
        else:
            return True

def raidbots(simc_path, profile_location, simc_build, output_location, report_name, iterations):
    sim_local(simc_path, profile_location, output_location)