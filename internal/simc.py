import glob
import os
import re
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen, urlretrieve


def sim_local(simc_path, profile_location, output_location, iterations):
    locationList = output_location.split("/")
    output = open(output_location.replace("json", "log"), 'w')

    try:
        subprocess.check_call([simc_path, "json2={0}".format(output_location), "iterations={0}".format(iterations), profile_location], stdout=output, stderr=output)
        output.close()
    except:
        output.close()
        print("-- {0} has an error. Skipping file.".format(locationList[-1]))
        with open(output_location.replace("json", "log")) as file:
            lines = file.readlines()
            print("-- {0}".format(lines[-1]))

    os.remove(output_location.replace("json", "log"))


def raidbots(simc_path, profile_location, simc_build, output_location, report_name, iterations):
    sim_local(simc_path, profile_location, output_location, iterations)


def download_latest():
    seven_zip_paths = ["7z.exe", "C:/Program Files/7-Zip/7z.exe"]
    seven_zip_executable = _find_7zip(seven_zip_paths)

    print(f"Starting auto download check of SimulationCraft.")

    # Application root path, and destination path
    rootpath = os.path.dirname(os.path.realpath(__file__))
    download_dir = os.path.join(rootpath, "..", "auto_download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    base_path = "http://downloads.simulationcraft.org/nightly"

    # Get filename of latest build of simc
    try:
        html = urlopen(f"{base_path}/?C=M;O=D").read().decode("utf-8")
    except URLError:
        print(f"Could not access download directory on simulationcraft.org")
    # filename = re.search(r'<a href="(simc.+win64.+7z)">', html).group(1)
    filename = list(
        filter(None, re.findall(r'.+nonetwork.+|<a href="(simc.+win64.+7z)">', html))
    )[0]
    print(f"Latest simc: {filename}")

    # Download latest build of simc
    filepath = os.path.join(download_dir, filename)
    if not os.path.exists(filepath):
        url = f"{base_path}/{filename}"
        print(f"Retrieving simc from url '{url}' to '{filepath}'.")
        urlretrieve(url, filepath)
    else:
        print(f"Latest simc version already downloaded at {filename}.")
        return filepath.strip(".7z")

    # Unpack downloaded build and set simc_path
    dir_name = filename[: filename.find(".7z")]
    simc_path = os.path.join(download_dir, dir_name, "simc.exe")
    if not os.path.exists(simc_path):
        try:
            cmd = f'{seven_zip_executable} x "{filepath}" -aoa -o"{download_dir}"'
            print(f"Running unpack command '{cmd}'")
            subprocess.call(cmd)

            time.sleep(1)

            # Nightly builds include their commit hash, we need to strip that out.
            commit = dir_name.rsplit("-")[-1]
            _rename_directory(f"{download_dir}/simc-*-win64/", commit)

        except Exception as e:
            print(f"Exception when unpacking: {e}")

        # keep the latest 7z to remember current version, but clean up any other ones
        _cleanup_older_files(download_dir, dir_name)

    else:
        print(f"Simc already exists at '{repr(simc_path)}'.")

    return os.path.join(download_dir, dir_name)


def _find_7zip(search_paths):
    # Try to find 7zip, and raise an error if not
    for executable in search_paths:
        try:
            if not os.path.exists(executable):
                print(f"7Zip executable at '{executable}' does not exist.")
                continue
            else:
                return executable
                break
        except:
            continue
    else:
        raise RuntimeError(
            "Could not unpack the auto downloaded SimulationCraft executable."
            f"Please note that you need 7Zip installed at one of the following locations: {search_paths}."
        )


def _cleanup_older_files(download_dir, current_dir):
    try:
        files = glob.glob(f"{download_dir}/simc*")
        for f in files:
            if (
                os.path.basename(f) != current_dir
                and os.path.basename(f) != f"{current_dir}.7z"
            ):
                print(f"Removing old simc from '{os.path.basename(f)}'.")
                os.remove(f)
    except:
        print(
            "Unable to automatically remove files, you may want to cleanup old files in auto_download/"
        )


def _rename_directory(glob_path, commit):
    for folder in glob.glob(glob_path):
        print(f"renaming {folder} -> {folder}-{commit}")
        os.rename(folder, f"{folder[:-1]}-{commit}")
