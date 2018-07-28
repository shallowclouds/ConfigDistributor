import asyncio
import concurrent.futures
import functools
import inspect
import os
import time

# If DEBUG == True, Server will output some debug information.
DEBUG_ = True

# Some const variable
CRED = '\033[91m'
CGREEN2 = '\33[92m'
CEND = '\033[0m'
DEBUG = 10
INFO = 20
LOGGING_LEVEL = 0


def info(*args, level=INFO):
    if level < LOGGING_LEVEL:
        return

    prompt = ''
    if level == DEBUG:
        prompt = 'Info'
    elif level == INFO:
        prompt = 'Debug'
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


async def file_distribute(message, port, loop):
    print("aaaaaaaaaaaa")
    reader, writer = await asyncio.open_connection('127.0.0.1', port,
                                                   loop=loop)

    print('%d Send: %r' % (port, message,))
    writer.write(message.encode())

    data = await reader.readuntil(separator=b'End')
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()


@timethis
def subprocess_routine(serv_addr: list, path: str):
    loop = asyncio.get_event_loop()
    fs = [file_distribute("Hello from %d!" % (8887 + i), 8887 + i, loop) for i in range(0, 2)]
    print("xxxxxxxxxxxxxx")
    '''
    loop.run_until_complete(asyncio.gather(file_distribute("Hello from %d!" % 8887, 8887, loop),
                                           file_distribute("Hello from %d!" % 8888, 8888, loop),))
    loop.close()

    while True:
        done, pending = 
        print("--SubProcess[%d]: Is pending set empty %d" % (index, not pending,))
        if not pending:
            break
    '''


def send_files(attrs: dict):
    core_cnt = os.cpu_count()
    block_len = int(len(attrs['Server-List']) / core_cnt)
    block_cnt = core_cnt if len(attrs['Server-List']) % core_cnt == 0 else core_cnt + 1

    serv_addrs = []
    for i in range(0, block_cnt):
        serv_addrs.append(attrs['Server-List'][i * block_len:min(((i + 1) * block_len - 1), len(attrs['Server-List']))])

    with concurrent.futures.ProcessPoolExecutor(max_workers=core_cnt) as executor:
        sp_routines = [executor.submit(subprocess_routine, serv_addrs[i], attrs['Path']) for i in range(0, block_cnt)]
        print(sp_routines)
        for future in concurrent.futures.as_completed(sp_routines):
            pass


def main():
    global LOGGING_LEVEL
    if DEBUG_:
        LOGGING_LEVEL = DEBUG
    else:
        LOGGING_LEVEL = INFO
    info('test!')


if __name__ == '__main__':
    main()
