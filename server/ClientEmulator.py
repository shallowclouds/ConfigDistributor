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
