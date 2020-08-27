import json
import os

__all__ = ["GLOBAL_CONFIG"]


class Config(object):
    def __init__(self):
        self._file = os.path.dirname(__file__) + os.sep + "config.json"
        self._dict = {}

        with open(self._file, "r") as f:
            self._dict = json.load(f)

    def _save(self):
        with open(self._file, "w") as f:
            json.dump(self._dict, f, indent=4)

    def set_user_sid(self, sid: str):
        self._dict["user"]["SessionId"] = sid
        self._save()

    def get_user_sid(self):
        return self._dict["user"]["SessionId"]

    def get_user_token(self):
        return self._dict["user"]["Token"]

    def set_user_token(self, token: str):
        self._dict["user"]["Token"] = token
        self._save()


# 全局配置
GLOBAL_CONFIG = Config()
