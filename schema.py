from typing import Any

import yaml

from classes import Expandable
from context import context

faker_config: dict[str, Any] = {}
params: dict[str, Any] = {}
struct: dict[str, Any] = {}
env = Expandable()


def load_schema(file_name=None):
    global faker_config, params, struct, env

    if not file_name:
        file_name = "sample_schema.yaml"

    with open(file_name) as f:
        schema = yaml.load(f, yaml.FullLoader)

    faker_config = schema["faker"]
    params = schema["params"]
    struct = schema["struct"]

    def _make_env(obj: Expandable, dict_: dict):
        if not dict_:
            return
        for k, v in dict_.items():
            if type(v) is dict:
                o = Expandable()
                _make_env(o, v)
                obj.set(k, o)
            else:
                obj.set(k, v)

    env_dict = schema.get("env", {})
    _make_env(env, env_dict)

    context["env"] = env
