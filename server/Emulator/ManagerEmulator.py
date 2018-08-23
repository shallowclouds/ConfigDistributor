import asyncio
import base64
import json

from Crypto.Cipher import ChaCha20

attrs = {
    'Method': 'SEND',
    'Server-List': [
        '0.0.0.0', '1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4',
        '5.5.5.5', '6.6.6.6', '7.7.7.7', '8.8.8.8', '9.9.9.9',
        '10.10.10.10', '11.11.11.11', '12.12.12.12', '13.13.13.13', '14.14.14.14',
        '15.15.15.15', '16.16.16.16', '17.17.17.17', '18.18.18.18', '19.19.19.19',
        '20.20.20.20'
    ],
    'Content-Length': 42,
}


def slicetest(slice_):
    print(slice_)


async def file_distribute(message, port, loop):
    print(json.dumps(attrs).encode())
    reader, writer = await asyncio.open_connection('google.com', port,
                                                   loop=loop)

    print('%d Send: %r' % (port, message,))
    writer.write(message.encode())

    data = await reader.read()
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()


def test():
    loop = asyncio.get_event_loop()
    # fs = [file_distribute("Hello from %d!" % (8887 + i), 8887 + i, loop) for i in range(0, 2)]
    loop.run_until_complete(file_distribute("Hello from %d!" % 8887, 80, loop))
    # loop.run_until_complete(asyncio.gather(file_distribute("Hello from %d!" % 8887, 8887, loop),
    #                                       file_distribute("Hello from %d!" % 8888, 8888, loop),))

    loop.close()


def decrypt(encrypted_json_str: str, key: bytes) -> dict:
    encrypted_json = json.loads(encrypted_json_str)
    cipher_text = base64.b64decode(encrypted_json['ciphertext'])
    nonce = base64.b64decode(encrypted_json['nonce'])
    cipher = ChaCha20.new(key=key, nonce=nonce)
    json_attr = cipher.decrypt(cipher_text)
    return json.loads(json_attr)


def encrypt(plain_attr: dict, cipher: ChaCha20.ChaCha20Cipher) -> str:
    json_attr = json.dumps(plain_attr).encode()
    encrypted_data_bytes = cipher.encrypt(json_attr)

    nonce = base64.b64encode(cipher.nonce).decode()
    encrypted_data = base64.b64encode(encrypted_data_bytes).decode()

    return json.dumps({'nonce': nonce, 'ciphertext': encrypted_data})


def main():
    key = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'
    cipher = ChaCha20.new(key=key)
    enc = encrypt(
        {
            'Method': 'SEND',
            'Server-List': [
                'google.com',
                '127.0.0.1'
            ],
            'Content-Length': 42,
            'Timeout': 100
        }, cipher)
    print(type(enc), enc)
    dec = decrypt(enc, key)
    print(type(dec), dec)


if __name__ == '__main__':
    main()
    '''
    core_cnt = 3
    block_len = max(int(len(attrs['Server-List']) / core_cnt), 5)
    block_cnt = int(len(attrs['Server-List']) / block_len)
    block_cnt += 1 if len(attrs['Server-List']) % block_len else 0
    serv_addrs = []
    for i in range(0, block_cnt):
        serv_addrs.append(attrs['Server-List'][i * block_len:min((i + 1) * block_len, len(attrs['Server-List']))])
        print(i * block_len, min(((i + 1) * block_len - 1), len(attrs['Server-List'])))
    print(serv_addrs)
    '''
