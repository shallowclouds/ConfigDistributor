import asyncio

import server.utils.DataPacking as DataPacking
import server.utils.Logger as Logger

key_ = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'


class StreamHandler:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, key: bytes):
        self.reader = reader
        self.writer = writer
        self.key = key

    async def recv_attr(self):
        attr_recv_enc = b''
        while True:
            try:
                attr_recv_enc += await self.reader.readuntil(separator=b'\n')
            except asyncio.LimitOverrunError as exc:
                Logger.info('Consumed:', exc.consumed, level=Logger.DEBUG)
                attr_recv_enc += await self.reader.read(exc.consumed)
            else:
                break
        attr_recv = DataPacking.dict_decrypt(attr_recv_enc[:-1], self.key)
        return attr_recv

    def send_attrs(self, attrs: dict):
        data_to_sent = DataPacking.dict_encrypt(attrs, self.key) + b'\n'
        Logger.info(data_to_sent, level=Logger.DEBUG)
        self.writer.write(data_to_sent)


async def response_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    handler = StreamHandler(reader, writer, key_)
    try:
        success_ret = {'result': True}

        Logger.info('Connection established.', level=Logger.DEBUG)
        attrs_recv = await handler.recv_attr()
        Logger.info(attrs_recv, level=Logger.DEBUG)

        if attrs_recv['method'] == 'send':
            DataPacking.b64str_to_file(attrs_recv['remote-path'], attrs_recv['file-content-b64'])
        elif attrs_recv['method'] == 'get':
            success_ret.update({
                'file-content-b64': DataPacking.file_to_b64str(attrs_recv['remote-path'])
            })
    except Exception as e:
        Logger.info(type(e), e, level=Logger.DEBUG)
        handler.send_attrs({
            'result': False,
            'exc_type': str(type(e)).split("'")[1],
            'exc_val': str(e)
        })
    else:
        handler.send_attrs(success_ret)


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
