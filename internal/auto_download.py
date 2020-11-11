"""downloads the nightly simc"""
#!/usr/bin/env python
import glob
import os
import re
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen, urlretrieve


def download_latest():
    """main download function"""
    seven_zip_paths = ["7z.exe", "C:/Program Files/7-Zip/7z.exe"]
    seven_zip_executable = _find_7zip(seven_zip_paths)

    print("Starting auto download check of SimulationCraft.")

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
        print("Could not access download directory on simulationcraft.org")
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
        # pylint: disable=broad-except
        try:
            cmd = f'{seven_zip_executable} x "{filepath}" -aoa -o"{download_dir}"'
            print(f"Running unpack command '{cmd}'")
            subprocess.call(cmd)

            time.sleep(1)

            # Nightly builds include their commit hash, we need to strip that out.
            commit = dir_name.rsplit("-")[-1]
            _rename_directory(f"{download_dir}/simc-*-win64/", commit)

        except Exception as error:
            print(f"Exception when unpacking: {error}")

        # keep the latest 7z to remember current version, but clean up any other ones
        _cleanup_older_files(download_dir, dir_name)

    else:
        print(f"Simc already exists at '{repr(simc_path)}'.")

    return os.path.join(download_dir, dir_name)


def _find_7zip(search_paths):
    """Try to find 7zip, and raise an error if not"""
    # pylint: disable=bare-except, unreachable
    for executable in search_paths:
        try:
            if not os.path.exists(executable):
                print(f"7Zip executable at '{executable}' does not exist.")
                continue
            return executable
            break
        except:
            continue
    else:
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
        print(f"renaming {folder} -> {folder}-{commit}")
        os.rename(folder, f"{folder[:-1]}-{commit}")
