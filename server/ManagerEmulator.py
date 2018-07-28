import asyncio
import json

attrs = {
    'Method': 'SEND',
    'Server-List': [
        '0.0.0.0', '1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4',
        '5.5.5.5', '6.6.6.6', '7.7.7.7', '8.8.8.8', '9.9.9.9',
        '10.10.10.10', '11.11.11.11', '12.12.12.12', '13.13.13.13', '14.14.14.14',
        '15.15.15.15', '16.16.16.16', '17.17.17.17', '18.18.18.18', '19.19.19.19',
    ],
    'Content-Length': 42,
}


def slicetest(slice_):
    print(slice_)


async def file_distribute(message, port, loop):
    print(json.dumps(attrs).encode())
    reader, writer = await asyncio.open_connection('127.0.0.1', port,
                                                   loop=loop)

    print('%d Send: %r' % (port, message,))
    writer.write(json.dumps(attrs).encode())

    data = await reader.readuntil(separator=b'End')
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()


def test():
    loop = asyncio.get_event_loop()
    # fs = [file_distribute("Hello from %d!" % (8887 + i), 8887 + i, loop) for i in range(0, 2)]
    loop.run_until_complete(file_distribute("Hello from %d!" % 8887, 8887, loop))
    # loop.run_until_complete(asyncio.gather(file_distribute("Hello from %d!" % 8887, 8887, loop),
    #                                       file_distribute("Hello from %d!" % 8888, 8888, loop),))

    loop.close()


if __name__ == '__main__':
    # test()
    core_cnt = 3
    block_len = int(len(attrs['Server-List']) / core_cnt)
    block_cnt = core_cnt if len(attrs['Server-List']) % core_cnt == 0 else core_cnt + 1
    serv_addrs = []
    for i in range(0, block_cnt):
        serv_addrs.append(attrs['Server-List'][i * block_len:min(((i + 1) * block_len - 1), len(attrs['Server-List']))])
    print(serv_addrs)