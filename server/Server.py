import asyncio
import base64
import concurrent.futures
import functools
import inspect
import json
import os
import time

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

# If DEBUG == True, Server will output some debug information.
DEBUG_ = True

# Some const variable
CRED = '\033[91m'
CGREEN2 = '\33[92m'
CEND = '\033[0m'
DEBUG = 10
INFO = 20
ERROR = 30
LOGGING_LEVEL = 0


def info(*args, level=INFO):
    if level < LOGGING_LEVEL:
        return

    prompt = ''
    if level == DEBUG:
        prompt = 'Debug'
    elif level == INFO:
        prompt = 'Info'
    elif level == ERROR:
        prompt = 'Error'
    if DEBUG_:
        current_frame = inspect.currentframe()
        if current_frame is not None:
            func = inspect.getframeinfo(current_frame.f_back).function
            print(CRED + ('[%s] <%s>' % (prompt, func)) + CGREEN2, *args, CEND)
        else:
            print(CRED + ('[%s]' % prompt) + CGREEN2, *args, CEND)
    else:
        print(CRED + ('[%s]' % prompt) + CGREEN2, *args, CEND)


def timethis(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Function: ", func.__name__, "spent ", end - start, "s.")
        return result

    return wrapper


def encrypt(plain_attr: dict, key: bytes) -> str:
    cipher = ChaCha20.new(key=key)
    json_attr = json.dumps(plain_attr).encode()
    encrypted_data_bytes = cipher.encrypt(json_attr)

    nonce = base64.b64encode(cipher.nonce).decode()
    encrypted_data = base64.b64encode(encrypted_data_bytes).decode()

    return json.dumps({'nonce': nonce, 'ciphertext': encrypted_data})


def decrypt(encrypted_json_str: str, key: bytes) -> dict:
    encrypted_json = json.loads(encrypted_json_str)
    cipher_text = base64.b64decode(encrypted_json['ciphertext'])
    nonce = base64.b64decode(encrypted_json['nonce'])
    cipher = ChaCha20.new(key=key, nonce=nonce)
    json_attr = cipher.decrypt(cipher_text)
    return json.loads(json_attr)


async def file_distribute(attr: dict, addr: str, loop, key: bytes):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(addr, 8888, loop=loop), timeout=attr['Timeout'])

        data_to_sent = encrypt(attr, key).encode()
        info(data_to_sent, level=DEBUG)

        writer.write(data_to_sent)
        writer.write_eof()

        data = await reader.read()
        attr = decrypt(data, key)
        info('Received: %r from' % data, addr, level=DEBUG)
        info('Send file:', attr['Result'])

        info('Close the socket:', addr, level=DEBUG)
        writer.close()
    except (TimeoutError, asyncio.TimeoutError):
        info('Timeout Error: Failed to connect to %s.' % addr,
             'Please check the availability of the connection.', level=ERROR)
    except ConnectionRefusedError:
        info('Connection Refused Error: %s refused to establish connection.' % addr)
    except Exception as e:
        info(type(e), ':', e, level=ERROR)


def subprocess_routine(attrs: dict, key: bytes):
    info(attrs, level=DEBUG)
    server_list = attrs['Server-List']
    attrs.pop('Server-List')

    loop = asyncio.get_event_loop()

    fs = [file_distribute(attrs, server_list[i], loop, key) for i in range(0, len(server_list))]

    loop.run_until_complete(asyncio.wait(fs, return_when=asyncio.ALL_COMPLETED))
    # loop.close()


def send_files(attrs: dict, key: bytes):
    core_cnt = os.cpu_count()
    block_len = max(int(len(attrs['Server-List']) / core_cnt), 5)
    block_cnt = int(len(attrs['Server-List']) / block_len)
    block_cnt += 1 if len(attrs['Server-List']) % block_len else 0
    serv_addr_slices = []
    for i in range(0, block_cnt):
        serv_addr_slices.append(
            attrs['Server-List'][i * block_len: min((i + 1) * block_len, len(attrs['Server-List']))])

    new_attrs = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=core_cnt) as executor:
        sp_routines = []
        for i in range(0, block_cnt):
            new_attrs.append({**attrs})
            new_attrs[i]['Server-List'] = serv_addr_slices[i]
            sp_routines.append(executor.submit(subprocess_routine, new_attrs[i], key))
        info(sp_routines, level=DEBUG)
        concurrent.futures.wait(sp_routines)


def main():
    attrs = {
        'Method': 'SEND',
        'Server-List': [
            'google.com',
            '127.0.0.1'
        ],
        'Content-Length': 42,
        'Timeout': 4
    }
    key = get_random_bytes(32)
    key_ = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'
    send_files(attrs, key_)


if __name__ == '__main__':
    if DEBUG_:
        LOGGING_LEVEL = DEBUG
    else:
        LOGGING_LEVEL = INFO
    main()
