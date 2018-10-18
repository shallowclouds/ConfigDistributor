import asyncio


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
        Logger.info('Connection established.', level=Logger.DEBUG)
        attrs_recv = await handler.recv_attr()
        Logger.info(attrs_recv, level=Logger.DEBUG)

        ret = {'result': True}

        if attrs_recv['type'] == 'POST':
            ret.update({'file_list': []})
            for file_info in attrs_recv['file_list']:
                try:
                    DataPacking.b64str_to_file(file_info['remote_path'], file_info['file_content_b64'])
                except Exception as e:
                    exc_type = str(type(e)).split("'")[1]
                    exc_val = str(e)
                    ret['file_list'].append({
                        'remote_path': file_info['remote_path'],
                        'result': False,
                        'failure_reason': exc_type + ': ' + exc_val
                    })
                else:
                    ret['file_list'].append({
                        'remote_path': file_info['remote_path'],
                        'result': True
                    })
        elif attrs_recv['type'] == 'GET':
            ret.update({'file_list': []})
            for path in attrs_recv['remote_path']:
                try:
                    file_info = {
                        'path': path,
                        'result': True,
                        "file_content_b64": DataPacking.file_to_b64str(path)
                    }
                    ret['file_list'].append(file_info)
                except Exception as e:
                    exc_type = str(type(e)).split("'")[1]
                    exc_val = str(e)
                    ret['file_list'].append({
                        'remote_path': path,
                        'result': False,
                        'failure_reason': exc_type + ': ' + exc_val
                    })
        elif attrs_recv['type'] == 'TEST':
            pass
    except Exception as e:
        Logger.info(type(e), e, level=Logger.DEBUG)
        handler.send_attrs({
            'result': False,
            'failure_reason': str(type(e)).split("'")[1] + ': ' + str(e)
        })
    else:
        handler.send_attrs(ret)


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
    import sys
    import os

    server_path = os.path.dirname(os.path.realpath(__file__))
    project_path = os.path.join(os.path.sep, *server_path.split(os.sep)[0:-1])
    sys.path.append(project_path)

    import server.utils.DataPacking as DataPacking
    import server.utils.Logger as Logger
    import json
    import base64

    # project_path = 'C:\\Users\\76033\\PycharmProjects\\ConfigDistributor'
    settings_path = os.path.join(project_path, 'general-settings.json')
    with open(settings_path) as settings_file:
        general_settings = json.load(settings_file)
    key_ = base64.b64decode(general_settings['key-b64'])
    main()
