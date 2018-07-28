import sys
import json
from socketserver import BaseRequestHandler, TCPServer


class EchoHandler(BaseRequestHandler):
    def handle(self):
        print("Get connection from", self.client_address)
        while True:
            msg = self.request.recv(8192)
            attrs = json.loads(msg.decode())
            print("Msg from", self.client_address, ":", msg)
            print(attrs['Server-List'])
            if not msg:
                break
            while True:
                msg = input("Msg: ")
                self.request.send(msg.encode())
                if msg == 'End\n':
                    break


if __name__ == '__main__':
    serv = TCPServer(('', int(sys.argv[1])), EchoHandler)
    serv.serve_forever()
