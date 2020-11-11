"""local simc functions"""
import subprocess
import os


def sim_local(simc_path, profile_location, output_location, iterations):
    # pylint: disable=bare-except
    """sim against a local simc instance"""
    location_list = output_location.split("/")
    output = open(output_location.replace("json", "log"), 'w')

    try:
        subprocess.check_call(
            [
                simc_path,
                "json2={0}".format(output_location),
                "iterations={0}".format(iterations),
                profile_location
            ], stdout=output, stderr=output)
        output.close()
    except:
        output.close()
        print("-- {0} has an error. Skipping file.".format(location_list[-1]))
        with open(output_location.replace("json", "log")) as file:
            lines = file.readlines()
            print("-- {0}".format(lines[-1]))

    os.remove(output_location.replace("json", "log"))


def raidbots(simc_path, profile_location, simc_build, output_location, report_name, iterations):
    # pylint: disable=unused-argument, too-many-arguments
    """just pass through to sim_local"""
    sim_local(simc_path, profile_location, output_location, iterations)
