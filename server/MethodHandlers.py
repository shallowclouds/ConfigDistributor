import asyncio
import concurrent.futures
import os

from server.utils import Encryptor
from server.utils import Logger


async def file_distribute(attr: dict, addr: str, loop, key: bytes):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(addr, 8888, loop=loop), timeout=attr['Timeout'])

        data_to_sent = Encryptor.dict_encrypt(attr, key).encode()
        Logger.info(data_to_sent, level=Logger.DEBUG)

        writer.write(data_to_sent)
        writer.write_eof()

        attr_recv_enc = await reader.read()
        attr = Encryptor.dict_decrypt(attr_recv_enc, key)
        Logger.info('Received: %r from' % attr_recv_enc, addr, level=Logger.DEBUG)
        Logger.info('Send file:', attr['Result'])

        Logger.info('Close the socket:', addr, level=Logger.DEBUG)
        writer.close()
    except (TimeoutError, asyncio.TimeoutError):
        Logger.info('Timeout Error: Failed to connect to %s.' % addr,
                    'Please check the availability of the connection.', level=Logger.ERROR)
    except ConnectionRefusedError:
        Logger.info('Connection Refused Error: %s refused to establish connection.' % addr)
    except Exception as e:
        Logger.info(type(e), ':', e, level=Logger.ERROR)


def subprocess_routine(attrs: dict, key: bytes):
    Logger.info(attrs, level=Logger.DEBUG)
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
        Logger.info(sp_routines, level=Logger.DEBUG)
        concurrent.futures.wait(sp_routines)
