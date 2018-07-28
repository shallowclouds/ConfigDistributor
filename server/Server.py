import asyncio
import concurrent.futures
import functools
import os
import time


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

    reader, writer = await asyncio.open_connection('127.0.0.1', port,
                                                   loop=loop)

    print('%d Send: %r' % (port, message,))
    writer.write(message.encode())

    data = await reader.readuntil(separator=b'End')
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()


@timethis
def subprocess_routine(index: int):
    loop = asyncio.get_event_loop()
    fs = [file_distribute("Hello from %d!" % 8887 + i, 8887 + i, loop) for i in range(0, 2)]
    while True:

        done, pending = loop.run_until_complete(asyncio.wait(fs, return_when=asyncio.FIRST_COMPLETED))
        print("--SubProcess[%d]: Is pending set empty %d" % (index, not pending,))
        break


def subprocess_distributor():
    core_cnt = os.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(max_workers=core_cnt) as executor:
        sp_routines = [executor.submit(subprocess_routine, i) for i in range(0, 2)]
        print(sp_routines)
        for future in concurrent.futures.as_completed(sp_routines):
            pass


def main():
    subprocess_distributor()


def test():
    message = 'Hello World!'
    loop = asyncio.get_event_loop()
    '''loop.run_until_complete(asyncio.gather(tcp_echo_client(message, 8887, loop),
                                           tcp_echo_client(message, 8888, loop),
                                           tcp_echo_client(message, 8889, loop)))
    '''
    loop.close()


if __name__ == '__main__':
    main()
