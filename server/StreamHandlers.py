import asyncio
import concurrent.futures
import os

from server.utils import Encryptor
from server.utils import Logger


class StreamHandlers:
    def __init__(self, addr: str, timeout: int, loop, key: bytes):
        self.loop = loop
        self.addr = addr
        self.key = key
        self.timeout = timeout

    async def __aenter__(self):
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(self.addr, 8888, loop=self.loop), timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.writer.close()

    def send_attrs(self, attrs: dict):
        data_to_sent = (Encryptor.dict_encrypt(attrs, self.key) + '\n').encode()
        Logger.info(data_to_sent, level=Logger.DEBUG)

        self.writer.write(data_to_sent)

    async def recv_attrs(self) -> dict:
        attr_recv_enc = await self.reader.readuntil(separator=b'\n')
        Logger.info('attr_recv_enc:', attr_recv_enc)
        attr_recv = Encryptor.dict_decrypt(attr_recv_enc[:-1], self.key)
        Logger.info('Received attr_encrypted: %r from' % attr_recv_enc, self.addr, level=Logger.DEBUG)
        Logger.info('attr_recv:', attr_recv)
        return attr_recv


async def do_method(attrs: dict, addr: str, loop, key: bytes):
    try:
        async with StreamHandlers(addr, attrs['Timeout'], loop, key) as handler:
            handler.send_attrs(attrs)
            attr_recv = await handler.recv_attrs()
            print(attr_recv['Result'])
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

    fs = [do_method(attrs, server_list[i], loop, key) for i in range(0, len(server_list))]

    loop.run_until_complete(asyncio.wait(fs, return_when=asyncio.ALL_COMPLETED))
    # loop.close()


def pass_attrs_to_clients(attrs: dict, key: bytes):
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
