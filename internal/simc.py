"""local simc functions"""
import subprocess
import os


def sim_local(simc_path, profile_location, output_location, iterations):
    # pylint: disable=bare-except
    """sim against a local simc instance"""
    location_list = output_location.split("/")
    with open(output_location.replace("json", "log"), 'w', encoding="utf8") as file:
        try:
            subprocess.check_call(
                [
                    simc_path,
                    "json2={0}".format(output_location),
                    "iterations={0}".format(iterations),
                    profile_location
                ], stdout=file, stderr=file)
        except:
            print(
                "-- {0} has an error. Skipping file.".format(location_list[-1]))
            with open(output_location.replace("json", "log"), encoding="utf8") as file:
                lines = file.readlines()
                print("-- {0}".format(lines[-1]))

        os.remove(output_location.replace("json", "log"))
        file.close()


def raidbots(simc_path, profile_location, simc_build, output_location, report_name, iterations):
    # pylint: disable=unused-argument, too-many-arguments
    """just pass through to sim_local"""
    sim_local(simc_path, profile_location, output_location, iterations)
