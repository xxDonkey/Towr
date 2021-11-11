import os
import json
from typing import Any

_OS_KEY: str = 'Windows 10'
_VERSION_KEY: str = '20H2'
filepath = os.path.join(os.getcwd(), 'win10-syscalls.json')

datum: dict[Any, Any]
with open(filepath) as file:
    datum = json.load(file)

SYSCALLS: dict[str, int] = {}

for data, v in datum.items():
    if _OS_KEY in v and _VERSION_KEY in v[_OS_KEY]:
        SYSCALLS[data] = v[_OS_KEY][_VERSION_KEY]

