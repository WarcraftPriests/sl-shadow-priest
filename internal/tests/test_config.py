'tests for config module'

import os
import sys
import yaml

sys.path.insert(0, os.path.abspath( # This should be the path back to the root directory.
    os.path.join(os.path.dirname(__file__), '..', '..')))

from internal.config import config # pylint: disable=wrong-import-position

def test_config():
    'test loading the config'
    original_config = None
    with open("config.yml", "r") as ymlfile:
        original_config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    assert original_config is not None, 'unable to load config'

    # yeah this test is pretty eh, but not sure what to do here.
    assert config == original_config
