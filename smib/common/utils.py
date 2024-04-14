import pickle
from pathlib import Path

import functools
import json

from slack_bolt.response import BoltResponse


def is_pickleable(obj):
    try:
        pickle.dumps(obj)
        return True
    except (pickle.PicklingError, AttributeError, TypeError):
        return False


def to_path(x):
    path = Path(f"/{x.lstrip('/')}").as_posix().lstrip('/')
    return path


def log_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'{e.__class__.__name__}: {e}')

    return wrapper


def singleton(class_):
    instances = {}

    def wrapper(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return wrapper


def http_bolt_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        # Return raw BoltResponse object
        if isinstance(response, BoltResponse):
            return response

        # Return BoltResponse with body as json if return value is a dict
        if isinstance(response, dict):
            return BoltResponse(status=200, body=json.dumps(response))

        # Return bolt response with specified status code and json body
        # used with: return 200, {"ok": True}
        if type(response) in (list, tuple):
            if len(response) == 2 and isinstance(response[0], int) and isinstance(response[1], dict):
                return BoltResponse(status=response[0], body=json.dumps(response[1]))

    return wrapper
