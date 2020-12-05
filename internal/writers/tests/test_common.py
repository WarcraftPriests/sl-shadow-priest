'tests for config module'

import os
import sys

sys.path.insert(0, os.path.abspath( # This should be the path back to the root directory.
    os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# pylint: disable=wrong-import-position
from internal.writers import common


def test_generate_report_name():
    'test for simple name usage'
    assert common.generate_report_name('a') == 'a'
    assert common.generate_report_name('a', 'b') == 'a - b'
    assert common.generate_report_name('a', 'b', 'c') == 'a - b - c'


def test_generate_report_name_complex():
    'test for simple name usage'
    assert common.generate_report_name('Lok\'tar Agar') == 'Lok\'tar Agar'
    assert common.generate_report_name(
        'Lok\'tar Agar', 'ForTheAll1an_ce__') == 'Lok\'tar Agar - ForTheAll1an_ce'
    assert common.generate_report_name('a', '1', r'__') == 'a - 1 - '


def test_assure_path_exists__already_exists(mocker):
    'tests assure_path_exists skips creating a path when it exists' 
    mocker.patch('os.path.exists', return_value=True)
    spy_makedirs = mocker.patch('os.makedirs', return_value=None)
    
    common.assure_path_exists('some/test/path/to/check/')
    spy_makedirs.assert_not_called()


def test_assure_path_exists__doesnt_exist(mocker):
    'tests assure_path_exists creates a path when it doesnt exist' 
    mocker.patch('os.path.exists', return_value=False)
    spy_makedirs = mocker.patch('os.makedirs', return_value=None)
    
    common.assure_path_exists('some/test/path/to/check/')
    spy_makedirs.assert_called_with('some/test/path/to/check')


def test_build_output_string(mocker):
    mocker.patch('internal.writers.common.assure_path_exists', return_value=None)

    assert common.build_output_string(
        'base_path',
        'sim_type',
        'talent',
        'covenant',
        'file_ext'
    ) == r'base_path\results\Results_sim_typetalentcovenant.file_ext'
