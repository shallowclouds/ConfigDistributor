'''
import json
import sys
from socketserver import BaseRequestHandler, TCPServer


class EchoHandler(BaseRequestHandler):
    def handle(self):
        print("Get connection from", self.client_address)
        msg = self.request.recv(8192)
        attrs = json.loads(msg.decode())
        print("Msg from", self.client_address, ":", msg.decode())
        try:
            print(attrs['Server-List'])
        except:
            pass
        if not msg:
            print('Empty Msg!')
        while True:
            msg = input("Msg: ")
            self.request.send(msg.encode())
            if msg == 'End':
                break


if __name__ == '__main__':
    with TCPServer(('', int(sys.argv[1])), EchoHandler) as server:
        server.serve_forever()
'''
import base64
# current_dir = os.path.abspath(os.path.dirname(__file__))
# server_cert = os.path.join(current_dir, "Crt", 'server.crt')
# server_key = os.path.join(current_dir, "Crt", 'server.key')
# client_certs = os.path.join(current_dir, "Crt", 'client.crt')
# client_key = os.path.join(current_dir, "Crt", 'client.key')
#  context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# # context.verify_mode = ssl.CERT_REQUIRED
# # context.load_cert_chain(certfile=server_cert, keyfile=server_key)
# # context.load_verify_locations(cafile=client_certs)
import json
import socket

import server.utils.Encryptor as Encryptor
import server.utils.Logger as Logger

def server():
    listen_addr = '127.0.0.1'
    listen_port = 8888

    bindsocket = socket.socket()
    bindsocket.bind((listen_addr, listen_port))
    bindsocket.listen(5)

    key = b'\x0c@\xf0\x0f +\xd1g\x84\xf1#Z\xc3\xe4\xabX|\xe7\xa4\x00\x94\xc5{\x0eS\x8e\x1f\x1e\x07\xd0eh'
    while True:
        print("Waiting for client")
        conn, fromaddr = bindsocket.accept()
        # conn.setblocking(False)
        print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
        # conn = context.wrap_socket(newsocket, server_side=True)
        # print("SSL established. Peer: {}".format(conn.getpeercert()))
        buf = b''  # Buffer to hold received client data
        try:
            while True:
                data = conn.recv(1)
                if data == b'\n':
                    break
                buf += data
            print("Received:", buf)
            attrs = Encryptor.dict_decrypt(buf, key)
            print("Msg from", fromaddr, ":", data)
            print("attrs:", attrs)
            print(base64.b64decode(attrs['file-content'].encode()))
        except Exception as e:
            Logger.info(type(e), e)
            raise e
        finally:
            attrs_ret = {
                'Result': True
            }
            send_data = (Encryptor.dict_encrypt(attrs_ret, key) + '\n').encode()
            conn.send(send_data)
            print('send_data:', send_data)
            print("Closing connection")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()


if __name__ == '__main__':
    Logger.set_debug(True)
    server()
