import json
from pathlib import Path

class ConfigLoader: 

    config_path=Path(__file__).with_name("appconfig.json")
    config = None

    def __init__(self):
        with open(self.config_path) as config_file:
            self.config = json.load(config_file)

    def getConfig(self, param: str):
        return self.config.get(param)
