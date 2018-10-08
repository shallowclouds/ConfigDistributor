# If DEBUG == True, Server will output some debug information.
DEBUG_ = True


def timethis(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Function: ", func.__name__, "spent ", end - start, "s.")
        return result

    return wrapper


def main(general_settings: dict):
    attr_get = {
        "type": "GET",
        "uuid": "1be317fc-c871-11e8-89be-3cf862da4116",
        "client_list": [
            {
                "id": 1,
                "ip_address": "google.com"
            },
            {
                "id": 2,
                "ip_address": "127.0.0.1"
            }
        ],
        "remote_path": [
            "/home/rileywen/Documents/Test/get1.txt",
            "/home/rileywen/Documents/Test/get2.txt"
        ]
    }
    attr_post = {
        "type": "POST",
        "uuid": "1be317fc-c871-11e8-89be-3cf862da4116",
        "client_list": [
            {
                "id": 1,
                "ip_address": "google.com"
            },
            {
                "id": 2,
                "ip_address": "127.0.0.1"
            }
        ],
        "file_list": [
            {
                "remote_path": "/home/rileywen/Documents/Test/get2.txt",
                "file-content-b64": "<base64 encode>"
            },
            {
                "remote_path": "/home/rileywen/Documents/Test/get1.txt",
                "file-content-b64": "<base64 encode>"
            },
        ],
    }
    client_list = attr_get.pop("client_list")

    Logger.info(attr_get)
    Logger.info(client_list)

    """
    attrs = {
        'method': 'check_conn',
        'bool': True,
        'local-path': 'C:/Users/76033/Desktop/Test/Server/FireShot Capture 4.png',
        'remote-path': 'C:/Users/76033/Desktop/Test/Client/FireShot Capture 4.png',
        'timeout': 4
    }
    client_list = [
        'google.com',
        '127.0.0.1'
    ]
    """

    key = DataPacking.get_key32()
    key_ = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'
    ret_val = WebHandlers.pass_attrs_to_clients(attr_get, client_list, general_settings['key'],
                                                general_settings['timeout'])
    Logger.info("Concatenated result of all subprocess: ", ret_val, level=Logger.DEBUG)
    pprint(ret_val)


if __name__ == '__main__':
    import sys
    import os

    server_path = os.path.dirname(os.path.realpath(__file__))
    project_path = os.path.join(os.path.sep, *server_path.split(os.sep)[0:-1])
    sys.path.append(project_path)

    import functools
    import time
    import json
    import base64
    from pprint import pprint
    from server import WebHandlers
    from server.utils import DataPacking
    from server.utils import Logger

    Logger.set_debug(DEBUG_)

    settings_path = os.path.join(project_path, 'general-settings.json')
    with open(settings_path) as settings_file:
        general_settings = json.load(settings_file)
    general_settings['key'] = base64.b64decode(general_settings['key-b64'])
    Logger.info(general_settings['key'])
    main(general_settings)
