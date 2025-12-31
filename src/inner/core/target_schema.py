from __future__ import annotations
from copy import deepcopy

SCHEMA_VERSION = 1

DEFAULT_TARGET: dict = {
    "id": None,                 
    "type": "host",             
    "host": None,               
    "url": None,                
    "tags": [],                 
    "auth": {                   
        "ssh": None,            
        "http": None            
    },
    "meta": {                   
        "note": None,
        "os_guess": None
    }
}

def new_target() -> dict:
    return deepcopy(DEFAULT_TARGET)
