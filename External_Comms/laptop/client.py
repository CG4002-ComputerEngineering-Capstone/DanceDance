import getpass
import sshtunnel
import socket
import time
import sys
import threading
import base64

import globals_

ports = [65432, 65431, 65430]
LOCAL_PORT = 65432
REMOTE_PORT = 65432


class LaptopClient(threading.Thread):
    def __init__(self, dancerId):
        threading.Thread.__init__(self)
        self.dancerId = dancerId
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clock_offset = 0

    def send_message(self, message):
        bytes_message = base64.b64encode(str.encode(str(message)))
        self.socket.sendall(bytes_message + '|'.encode())

    def receive_message(self, bytes=1024):
        data = self.socket.recv(bytes)
        return base64.b64decode(data).decode()

    def setup_connection(self):
        username = input('Enter Sunfire username: ')
        password = getpass.getpass('Enter Sunfire password: ')
        tunnel1 = sshtunnel.SSHTunnelForwarder(
            ssh_address_or_host=('sunfire.comp.nus.edu.sg', 22),
            remote_bind_address=('137.132.86.235', 22),
            ssh_username=username,
            ssh_password=password
        )
        tunnel1.start()
        print(f'Connection to tunnel1 OK: {tunnel1.tunnel_bindings}')

        tunnel2 = sshtunnel.SSHTunnelForwarder(
            ssh_address_or_host=('127.0.0.1', tunnel1.local_bind_port),
            remote_bind_address=('127.0.0.1', REMOTE_PORT),
            local_bind_address=('127.0.0.1', LOCAL_PORT),
            ssh_username='xilinx',
            ssh_password='xilinx'
        )
        tunnel2.start()
        print(f'Connection to tunnel2 OK: {tunnel2.tunnel_bindings}')

        self.socket.connect(('localhost', LOCAL_PORT))
        print('Successfully connected to Ultra96!')
        self.send_message(self.dancerId)

    def clock_sync(self):
        offsets_array = []
        for i in range(5):
            data = self.receive_message()
            if data != 'ready':
                print('Clock sync ready packet wrong')
                sys.exit()

            print(f'Clock sync iteration #{i+1}')
            t0 = time.time()
            self.send_message('syncpacket')

            data = self.receive_message()
            t3 = time.time()

            t1, t2 = map(float, data.split('|'))
            print(f't0: {t0}\nt1: {t1}\nt2: {t2}\nt3: {t3}')

            rtt = (t1 - t0) - (t2 - t3)
            print(f'RTT #{i+1}: {rtt}')
            offset = t0 - t1 - (rtt/2)
            print(f'Offset #{i+1}: {offset}\n')

            offsets_array.append(offset)
            self.send_message('end')

        self.clock_offset = sum(offsets_array) / len(offsets_array)
        print(f'Average Clock Offset: {self.clock_offset}')

    def run(self):
        self.setup_connection()
        command = self.receive_message()
        if command != 'server_ready':
            print('did not rececive "server_ready" from server, exiting..')
            return
        self.send_message('sync')
        self.clock_sync()
        time.sleep(1)
        for i in range(10):
            # receive data indicating server is ready
            print('')
            data = globals_.dataQueue.get()
            self.send_message(data)

            # timestamp = str(time.time() - self.clock_offset)
            # print(f'timestamp: {timestamp}')
            # self.send_message(timestamp)
            # time.sleep(1)

            # command = self.receive_message()
        self.close()

    def close(self):
        print('Disconnecting from Server...')
        self.socket.close()


def main():
    if len(sys.argv) != 2:
        print('Invalid number of arguments')
        print('python client.py [Dancer ID]')
        sys.exit()
    dancerId = int(sys.argv[1])
    LOCAL_PORT = ports[dancerId - 1]
    client = LaptopClient(dancerId)
    client.start()


if __name__ == '__main__':
    main()
