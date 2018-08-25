import asyncio

import server.utils.DataPacking as DataPacking
import server.utils.Logger as Logger

key_ = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'


async def response_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        Logger.info('Connection established.', level=Logger.DEBUG)
        data = await reader.readuntil(separator=b'\n')
        attrs_recv: dict = DataPacking.dict_decrypt(data, key_)
        Logger.info(attrs_recv, level=Logger.DEBUG)
        if attrs_recv['method'] == 'send':
            Logger.info("attrs_recv['method'] is 'send'", level=Logger.DEBUG)
            DataPacking.b64str_to_file(attrs_recv['remote-path'], attrs_recv['file-content-b64'])
        elif attrs_recv['method'] == 'get':
            Logger.info("attrs_recv['method'] is 'get'", level=Logger.DEBUG)
    except Exception as e:
        Logger.info(type(e), e, level=Logger.DEBUG)
        writer.write(DataPacking.dict_encrypt({
            'result': False,
            'exc_type': str(type(e)).split("'")[1],
            'exc_val': str(e)
        }, key_))
    else:
        writer.write(DataPacking.dict_encrypt({
            'result': True
        }, key_))


def main():
    Logger.set_debug(True)
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(response_handler, '127.0.0.1', 8888, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    Logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
