import subprocess
import os

def sim_local(simc_path, profile_location, output_location):
    locationList = output_location.split("/")
    output = open(output_location.replace("json", "log"), 'w')
    try:
        subprocess.check_call([simc_path, "json2={0}".format(output_location), profile_location], stdout=output, stderr=output)
        output.close()
        os.remove(output_location.replace("json", "log"))
    except:
        print("{0} was not created. Skipping file (see detailed informations in {1})".format(locationList[-1], output_location.replace("json", "log")))


def raidbots(simc_path, profile_location, simc_build, output_location, report_name, iterations):
    sim_local(simc_path, profile_location, output_location)