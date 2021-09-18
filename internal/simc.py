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
                    f"json2={output_location}",
                    f"iterations={iterations}",
                    profile_location
                ], stdout=file, stderr=file)
        except:
            print(f"-- {location_list[-1]} has an error. Skipping file.")
            with open(output_location.replace("json", "log"), encoding="utf8") as file:
                lines = file.readlines()
                print(f"-- {lines[-1]}")

        os.remove(output_location.replace("json", "log"))
        file.close()


def raidbots(simc_path, profile_location, simc_build, output_location, report_name, iterations):
    # pylint: disable=unused-argument, too-many-arguments
    """just pass through to sim_local"""
    sim_local(simc_path, profile_location, output_location, iterations)
