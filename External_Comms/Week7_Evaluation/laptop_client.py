import getpass
import sshtunnel
import socket
import time
import sys

ports = [65432, 65431, 65430]
LOCAL_PORT = 65432
REMOTE_PORT = 65432


class LaptopClient():
    def __init__(self, dancerId):
        self.dancerId = dancerId
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup_connection()
        self.clock_offset = 0

    def send_message(self, message):
        bytes_message = str.encode(str(message))
        self.socket.sendall(bytes_message)

    def receive_message(self, bytes=1024):
        data = self.socket.recv(bytes)
        return data.decode()

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
        self.send_message(dancerId)

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

    def start(self):
        command = self.receive_message()
        while command != 'end':
            # receive data indicating server is ready
            print('')
            print(f'command: {command}')
            if command == 'sync':
                self.send_message('sync')
                self.clock_sync()
            elif command == 'test':
                if LOCAL_PORT == 65432:
                    time.sleep(0.2)
                elif LOCAL_PORT == 65431:
                    time.sleep(0.4)

                timestamp = str(time.time() - self.clock_offset)
                print(f'timestamp: {timestamp}')
                self.socket.sendall(str.encode(timestamp))

            command = self.receive_message()

    def close(self):
        print('Disconnecting from Server...')
        self.socket.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments')
        print('python laptop_client.py [Dancer ID]')
        sys.exit()
    dancerId = int(sys.argv[1])
    LOCAL_PORT = ports[dancerId - 1]
    client = LaptopClient(dancerId)
    client.start()
    client.close()
