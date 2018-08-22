import functools
import time

from server import WebHandlers
from server.utils import Encryptor
from server.utils import Logger

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


def main():
    attrs = {
        'Method': 'SEND',
        'Msg': 'TTTTTTTTTTT',
        'Content-Length': 42,
        'Timeout': 4
    }
    server_list = [
        'google.com',
        '127.0.0.1'
    ]
    key = Encryptor.get_key32()
    key_ = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'
    WebHandlers.pass_attrs_to_clients(attrs, server_list, key_)


if __name__ == '__main__':
    Logger.set_debug(DEBUG_)
    main()
