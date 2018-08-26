import asyncio
import concurrent.futures
import os

from server.utils import DataPacking
from server.utils import Logger


class RetObj:
    def __init__(self, address: str, result: bool, exp_type: str = None, exc_val: str = None):
        self.result = result
        self.address = address
        if exp_type is not None:
            self.exp_type = exp_type
            self.exp_val = exc_val

    def return_dict(self):
        if self.result:
            return {self.address: {'result': self.result}}
        else:
            return {self.address: {'result': self.result, 'exp_type': self.exp_type, 'exp_val': self.exp_val}}


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
        data_to_sent = DataPacking.dict_encrypt(attrs, self.key) + b'\n'
        Logger.info(data_to_sent, level=Logger.DEBUG)

        self.writer.write(data_to_sent)

    async def recv_attrs(self) -> dict:
        attr_recv_enc = b''
        while True:
            try:
                attr_recv_enc += await self.reader.readuntil(separator=b'\n')
            except asyncio.LimitOverrunError as exc:
                Logger.info('Consumed:', exc.consumed, level=Logger.DEBUG)
                attr_recv_enc += await self.reader.read(exc.consumed)
            else:
                break
        Logger.info('attr_recv_enc:', attr_recv_enc)
        attr_recv = DataPacking.dict_decrypt(attr_recv_enc[:-1], self.key)
        Logger.info('Received attr_encrypted: %r from' % attr_recv_enc, self.addr, level=Logger.DEBUG)
        Logger.info('attr_recv:', attr_recv)
        return attr_recv


async def do_method(attrs: dict, addr: str, loop, key: bytes):
    """
    Handle different methods in attributes dict here

    the following lists all the methods:
    send, get, check_conn, close

    :param attrs: the attributes to be sent to client specified by addr
    :param addr: the address of client
    :param loop: the event loop that the subprocess uses
    :param key: the key of cipher
    """
    try:
        async with StreamHandlers(addr, attrs['timeout'], loop, key) as handler:
            if attrs['method'] == 'send':
                attrs['file-content-b64'] = DataPacking.file_to_b64str(attrs['local-path'])
                Logger.info(attrs, level=Logger.DEBUG)

                handler.send_attrs(attrs)

                attr_recv = await handler.recv_attrs()
                if attr_recv['result']:
                    return RetObj(addr, True)
                else:
                    return RetObj(addr, False, attr_recv['exc_type'], attr_recv['exc_val'])
            elif attrs['method'] == 'get':
                handler.send_attrs(attrs)
                attr_recv = await handler.recv_attrs()
                if attr_recv['result']:
                    DataPacking.b64str_to_file(attrs['local-path'], attr_recv['file-content-b64'])
                    return RetObj(addr, True)
                else:
                    return RetObj(addr, False, attr_recv['exc_type'], attr_recv['exc_val'])
    except (TimeoutError, asyncio.TimeoutError):
        exc_val = 'Timeout Error: Failed to connect to %s. ' \
                  'Please check the availability of the connection.' % addr
        Logger.info(exc_val, level=Logger.DEBUG)
        return RetObj(addr, False, 'TimeoutError', exc_val)
    except ConnectionRefusedError:
        exc_val = 'Connection Refused Error: %s refused to establish connection.' % addr
        Logger.info(exc_val, level=Logger.DEBUG)
        return RetObj(addr, False, 'ConnectionRefusedError', exc_val)
    except Exception as e:
        exc_type = str(type(e)).split("'")[1]
        exc_val = str(e)
        Logger.info(exc_type, ':', exc_val, level=Logger.ERROR)
        return RetObj(addr, False, exc_type, exc_val)


def subprocess_routine(attrs: dict, client_list_slice: list, key: bytes):
    Logger.info(attrs, level=Logger.DEBUG)

    loop = asyncio.get_event_loop()

    fs = [do_method(attrs, client_list_slice[i], loop, key) for i in range(0, len(client_list_slice))]

    ret = {}
    done, _ = loop.run_until_complete(asyncio.wait(fs, return_when=asyncio.ALL_COMPLETED))
    for fut in done:
        ret.update(fut.result().return_dict())
    loop.close()
    # Logger.info('Result of single subprocess:', ret, level=Logger.DEBUG)
    return ret


def pass_attrs_to_clients(attrs: dict, client_list: list, key: bytes):
    core_cnt = os.cpu_count()
    block_len = max(int(len(client_list) / core_cnt), 5)
    block_cnt = int(len(client_list) / block_len)
    block_cnt += 1 if len(client_list) % block_len else 0
    client_list_slices = []
    for i in range(0, block_cnt):
        client_list_slices.append(
            client_list[i * block_len: min((i + 1) * block_len, len(client_list))])

    with concurrent.futures.ProcessPoolExecutor(max_workers=core_cnt) as executor:
        sp_routines = []
        for i in range(0, block_cnt):
            sp_routines.append(executor.submit(subprocess_routine, attrs, client_list_slices[i], key))
        Logger.info(sp_routines, level=Logger.DEBUG)
        done, _ = concurrent.futures.wait(sp_routines)

    ret = {}
    for fut in done:
        ret.update(fut.result())
    Logger.info("Concatenated result of all subprocess: ", ret, level=Logger.DEBUG)
    return ret
