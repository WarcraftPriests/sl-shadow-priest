'auto_download test file'
from unittest.mock import Mock
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))
from internal.auto_download import download_latest, BASE_URL, _cleanup_older_files, _find_7zip  # pylint: disable=wrong-import-position


def assert_not_called_with(self, *args, **kwargs):
    'Inverted assert_called_with function'
    try:
        self.assert_called_with(*args, **kwargs)
    except AssertionError:
        return
    raise AssertionError('Expected %s to not have been called.' %
                         self._format_mock_call_signature(args, kwargs))  # pylint: disable=protected-access


Mock.assert_not_called_with = assert_not_called_with


def test_download_latest(mocker):
    'test for the main download_latest function'

    mocker.patch('os.path.exists', return_value=False)
    spy1 = mocker.patch('internal.auto_download._find_7zip', return_value="7z")
    spy2 = mocker.patch(
        'internal.auto_download._ensure_download_path',
        return_value=f"{os.path.sep}tmp"
    )
    spy3 = mocker.patch(
        'internal.auto_download._get_latest_filename',
        return_value="latest_filename.7z"
    )
    spy4 = mocker.patch('internal.auto_download._download_simc_version')
    spy5 = mocker.patch('subprocess.call')
    mocker.patch('time.sleep')
    mocker.patch('internal.auto_download._rename_directory')
    mocker.patch('internal.auto_download._cleanup_older_files')

    result = download_latest()

    spy1.assert_called_once_with(["7z.exe", "C:/Program Files/7-Zip/7z.exe"])
    spy2.assert_called_once_with()
    spy3.assert_called_once_with()
    spy4.assert_called_once_with(
        f"{BASE_URL}/latest_filename.7z",
        f"{os.path.sep}tmp{os.path.sep}latest_filename.7z"
    )
    spy5.assert_called_once_with(
        f"7z x \"{os.path.sep}tmp{os.path.sep}latest_filename.7z\" -aoa -o\"{os.path.sep}tmp\""
    )

    assert result == f"{os.path.sep}tmp{os.path.sep}latest_filename{os.path.sep}"


def test_cleanup_old_files(mocker):
    'test for _cleanup_older_files'
    should_delete = [
        "/tmp/old-file",
    ]
    shouldnt_delete = [
        "/tmp/new-file",
    ]

    glob_spy = mocker.patch(
        'glob.glob', return_value=should_delete + shouldnt_delete)
    os_rm_spy = mocker.patch('os.remove')

    _cleanup_older_files('/tmp', "new-file")

    glob_spy.assert_called_once_with("/tmp/simc*")

    for file in should_delete:
        os_rm_spy.assert_any_call(file)
    for file in shouldnt_delete:
        os_rm_spy.assert_not_called_with(file)


def test_find_seven_zip(mocker):
    'test for _find_7zip()'

    paths = ["path-1", "path-2", "path-3"]

    # return that the only the 2nd path exists
    spy = mocker.patch('os.path.exists', side_effect=[False, True])
    mocker.patch('os.access', return_value=True)

    path = _find_7zip(paths)

    assert path == "path-2"
    for path in paths[:-1]:  # Removing the last entry
        spy.assert_any_call(path)
