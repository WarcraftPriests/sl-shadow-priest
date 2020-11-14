"""downloads the nightly simc"""
#!/usr/bin/env python
import glob
import os
import re
import subprocess
import time
import shutil
import requests
from requests.exceptions import RequestException


BASE_URL = "http://downloads.simulationcraft.org/nightly"


def download_latest():
    """Find, download, and extract the latest version of simulationcraft if required. Returns the basepath."""
    seven_zip_paths = ["7z.exe", "C:/Program Files/7-Zip/7z.exe"]
    seven_zip_executable = _find_7zip(seven_zip_paths)

    print("Starting auto download check of SimulationCraft.")

    # Application root path, and destination path
    download_dir = _ensure_download_path()

    # Get filename of latest build of simc
    latest_file = _get_latest_filename()
    print(f"Latest simc: {latest_file}")

    # Download latest build of simc
    filepath = os.path.join(download_dir, latest_file)
    if os.path.exists(filepath):
        print(f"Latest simc version already downloaded at {latest_file}.")
        return filepath.strip(".7z")

    _download_simc_version(f"{BASE_URL}/{latest_file}", filepath)

    # Unpack downloaded build and set simc_path
    dir_name = filepath[: filepath.find(".7z")]
    print(download_dir, dir_name)
    simc_path = os.path.join(download_dir, dir_name, "simc.exe")
    if not os.path.exists(simc_path):
        _unpack_file(seven_zip_executable, filepath, download_dir)

        # keep the latest 7z to remember current version, but clean up any other ones
        _cleanup_older_files(download_dir, dir_name)

    else:
        print(f"Simc already exists at '{repr(simc_path)}'.")
    return simc_path.rstrip('simc.exe')


def _find_7zip(search_paths):
    """Try to find 7zip, and raise an error if not"""
    for exe in search_paths:
        try:
            if not os.path.exists(exe):
                print(
                    f"7Zip executable at '{exe}' does not exist, or is not executable.")
                continue
            return exe
        except OSError:
            continue
    raise RuntimeError(
        "Could not unpack the auto downloaded SimulationCraft executable."
        f"Install 7Zip at one of the following locations: {search_paths}."
    )


def _cleanup_older_files(download_dir, current_dir):
    # pylint: disable=bare-except
    try:
        files = glob.glob(f"{download_dir}/simc*")
        for file in files:
            if (
                os.path.basename(file) != current_dir
                and os.path.basename(file) != f"{current_dir}.7z"
            ):
                print(f"Removing old simc from '{os.path.basename(file)}'.")
                os.remove(file)
    except:
        print("Unable to automatically remove files, cleanup old files in auto_download/")


def _rename_directory(glob_path, commit):
    for folder in glob.glob(glob_path):
        print(f"Renaming {folder}")
        os.rename(folder, f"{folder[:-1]}-{commit}")


def _ensure_download_path():
    'Create and return the auto_download path'
    rootpath = os.path.dirname(os.path.realpath(__file__))
    download_dir = os.path.join(rootpath, "..", "auto_download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    return download_dir


def _get_latest_filename():
    'Attempts to find the name of the latest file from simulationcraft'
    try:
        html = requests.get(f"{BASE_URL}/?C=M;O=D").text
    except RequestException:
        print("Could not access download directory on simulationcraft.org")
    # filename = re.search(r'<a href="(simc.+win64.+7z)">', html).group(1)
    filename = list(
        filter(None, re.findall(r'.+nonetwork.+|<a href="(simc.+win64.+7z)">', html))
    )[0]
    return filename


def _download_simc_version(url, filepath):
    'Download the specific file'
    print(f"Retrieving simc from url '{url}' to '{filepath}'.")
    with requests.get(url, stream=True) as req:
        with open(filepath, 'wb') as handler:
            shutil.copyfileobj(req.raw, handler)


def _unpack_file(seven_zip_executable, filepath, download_dir):
    'Unpacks a 7z archive into the provided directory'
    try:
        cmd = f'{seven_zip_executable} x "{filepath}" -aoa -o"{download_dir}"'
        print(f"Running unpack command '{cmd}'")
        subprocess.call(cmd)

        time.sleep(1)

        # Nightly builds include their commit hash, we need to strip that out.
        commit = filepath[: filepath.find(".7z")].rsplit("-")[-1]
        _rename_directory(f"{download_dir}/simc-*-win64/", commit)

    except OSError as error:
        print(f"Exception when unpacking: {error}")
