'tests for analyze module'

import os
import sys
from unittest.mock import call
sys.path.insert(0, os.path.abspath( # This should be the path back to the root directory.
    os.path.join(os.path.dirname(__file__), '..', '..')))

from internal.analyze import analyze # pylint: disable=wrong-import-position


def test_analyze(mocker):
    'test for the main analyze function'
    spy_pandas = mocker.patch('pandas.read_csv', return_value={})
    spy_build_results = mocker.patch(
        'internal.analyze.build_results', return_value={})
    spy_build_md = mocker.patch(
        'internal.analyze.build_markdown', return_value=None)
    spy_build_csv = mocker.patch(
        'internal.analyze.build_csv', return_value=None)
    spy_build_json = mocker.patch(
        'internal.analyze.build_json', return_value=None)

    # Not dungeon run
    analyze("talent", "gear", False, "weights", "timestamp", "covenant")

    spy_pandas.assert_called_once_with(
        os.path.join('gear', 'output', 'talent', 'covenant', 'statweights.csv'),
        usecols=['profile', 'actor', 'DD', 'DPS',
                 'int', 'haste', 'crit', 'mastery', 'vers']
    )
    spy_build_results.assert_has_calls([
        call({}, 'weights', 'Composite', 'gear'),
        call({}, 'weights', 'Single', 'gear')
    ])
    spy_build_md.assert_has_calls([
        call('Composite', '_talent', {}, 'gear', 'weights', None, '_covenant'),
        call('Single', '_talent', {}, 'gear', 'weights', None, '_covenant')
    ])
    spy_build_csv.assert_has_calls([
        call('Composite', '_talent', {}, 'gear', 'weights', None, '_covenant'),
        call('Single', '_talent', {}, 'gear', 'weights', None, '_covenant')
    ])
    spy_build_json.assert_not_called()


def test_analyze_dungeon_run(mocker):
    'tests running analyze with the dungeon flag set true'
    spy_pandas = mocker.patch('pandas.read_csv', return_value={})
    spy_build_results = mocker.patch(
        'internal.analyze.build_results', return_value={})
    spy_build_md = mocker.patch(
        'internal.analyze.build_markdown', return_value=None)
    spy_build_csv = mocker.patch(
        'internal.analyze.build_csv', return_value=None)
    spy_build_json = mocker.patch(
        'internal.analyze.build_json', return_value=None)

    # Dungeon run
    analyze("talent", "gear", True, "weights", "timestamp", "covenant")

    spy_pandas.assert_called_once_with(
        os.path.join('gear', 'output', 'talent', 'covenant', 'statweights.csv'),
        usecols=['profile', 'actor', 'DD', 'DPS',
                 'int', 'haste', 'crit', 'mastery', 'vers']
    )
    spy_build_results.assert_called_once_with(
        {}, 'weights', 'Dungeons', 'gear')
    spy_build_md.assert_called_once_with(
        'Dungeons', '_talent', {}, 'gear', 'weights', None, '_covenant'
    )
    spy_build_csv.assert_called_once_with(
        'Dungeons', '_talent', {}, 'gear', 'weights', None, '_covenant'
    )
    spy_build_json.assert_not_called()
