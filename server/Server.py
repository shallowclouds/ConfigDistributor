import asyncio
import concurrent.futures
import functools
import inspect
import json
import os
import sys
import time

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


async def file_distribute(attr: dict, addr: str, loop):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(addr, 8888, loop=loop), timeout=1)
        writer.write(json.dumps(attr).encode())
        data = await reader.readuntil(separator=b'End')
        info('Received: %r from' % data.decode(), addr, level=DEBUG)
        info('Close the socket:', addr, level=DEBUG)
        writer.close()
    except (TimeoutError, asyncio.TimeoutError):
        info('Timeout Error: Failed to connect to %s.' % addr,
             'Please check the availability of the connection.', level=ERROR)
    except ConnectionRefusedError:
        info('Connection Refused Error: %s refused to establish connection.' % addr)
    except Exception as e:
        info(type(e), ':', e, level=ERROR)


def subprocess_routine(attrs: dict):
    info(attrs, level=DEBUG)
    server_list = attrs['Server-List']
    attrs.pop('Server-List')

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    fs = [file_distribute(attrs, server_list[i], loop) for i in range(0, len(server_list))]

    loop.run_until_complete(asyncio.wait(fs, return_when=asyncio.ALL_COMPLETED))
    loop.close()


def send_files(attrs: dict):
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
            sp_routines.append(executor.submit(subprocess_routine, new_attrs[i]))
        info(sp_routines, level=DEBUG)
        concurrent.futures.wait(sp_routines)


def main():
    attrs = {
        'Method': 'SEND',
        'Server-List': [
            'google.com',
            '127.0.0.1'
        ],
        'Content-Length': 42
    }
    send_files(attrs)


if __name__ == '__main__':
    if DEBUG_:
        LOGGING_LEVEL = DEBUG
    else:
        LOGGING_LEVEL = INFO
    main()
