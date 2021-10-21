import getpass
import sshtunnel
import socket
import time
import sys
import threading
import base64

import globals_
from dashboard import send_sensor
# from sigpri import append, resetCumData
# from liveFeatures import append, resetCumData
from liveProcess import append, resetCumData

ports = [65432, 65431, 65430]
LOCAL_PORT = 65432
REMOTE_PORT = 65432


class LaptopClient(threading.Thread):
    def __init__(self, dancerId, clientConnectedFlag):
        threading.Thread.__init__(self)
        self.dancerId = dancerId
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clock_offset = 0
        self.clientConnectedFlag = clientConnectedFlag
        self.clockSyncFlag = threading.Event()
        self.sendMsgLock = threading.Lock()
        self.clock_offset_history = []

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
            local_bind_address=('127.0.0.1', ports[self.dancerId-1]),
            ssh_username='xilinx',
            ssh_password='xilinx'
        )
        tunnel2.start()
        print(f'Connection to tunnel2 OK: {tunnel2.tunnel_bindings}')

        self.socket.connect(('localhost', ports[self.dancerId-1]))
        print('Successfully connected to Ultra96!')
        self.clientConnectedFlag.set()
        self.send_message(self.dancerId)

    def clock_sync(self):
        while True:
            # wait for command from server to begin clock_sync
            command = self.receive_message()
            if command != 'sync':
                print('Clock sync error - packet received is not "sync"')
                sys.exit()
            self.clockSyncFlag.set()

            self.sendMsgLock.acquire()

            self.send_message('sync')
            offsets_array = []
            for i in range(10):
                data = self.receive_message()
                if data != 'ready':
                    print('Clock sync ready packet wrong')
                    sys.exit()

                print(f'Clock sync iteration #{i+1}')
                t0 = time.time()
                self.send_message('syncpacket')

                data = self.receive_message()
                print(data)
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
            self.clock_offset_history.append(sum(offsets_array) / len(offsets_array))
            print(f'Average Clock Offset: {self.clock_offset}')
            self.sendMsgLock.release()

    def run(self):
        self.setup_connection()
        
        command = self.receive_message()
        print('received message:', command)
        if command != 'server_ready':
            print('did not rececive "server_ready" from server, exiting..')
            return
        # self.send_message('sync')
        # self.clock_sync()
        clock_sync_thread = threading.Thread(target=self.clock_sync)
        clock_sync_thread.start()
        # time.sleep(1)
        while 1:
        # for i in range(1400):
            # receive data indicating server is ready
            sample = []
            timestamp = None
            while len(sample) < globals_.PACKET_WINDOW_SIZE:
                data = globals_.dataQueue.get()
                # print(f'data from bluno: {data}')
                # print(type(data))
                
                # TODO perform check for packet indicating start of dance move. 
                # If data is the packet containing timestamp of start of dance move i.e. timestamp + 6 sensor values, call resetCumData, clear sample and append to sample
                if len(data) == 7: 
                    resetCumData()
                    sample = []
                    print(f'RESET SAMPLE - sample length: {len(sample)}')
                    print(type(time.time()))
                    print(data[0])
                    print(data[1])

                    timestamp = float(data[0]) - self.clock_offset
                    print(f'timestamp: {timestamp}')
                    sample.append(data[1:])
                    print(f'Sample length: {len(sample)}')
                else:
                    sample.append(data)
                    print(f'Sample length: {len(sample)}')

            print(f'enough sample length: {sample}')

            # print(sample)
                        
            # send sensor readings to dashboard
            print('send_sensor to dashboard')
            # send_sensor(self.dancerId, sample)

            # preprocess data before sending to ultra96
            # vector = append(sample)
            # print(f'vector shape: {vector.shape}')
            test_vector = [float(int(self.dancerId)) for x in range(240)]
            # for v in vector:
            #     vector_string = ','.join(list(map(str, list(v.tolist()))))
            #     time.sleep(0.1)
            #     self.send_message(vector_string)

            # if start of dance move
            if timestamp is not None:
                test_vector.insert(0, timestamp)
            
            print(f'Length of vector to send: {len(test_vector)}')
            
            test = ','.join(list(map(str, test_vector)))

            self.sendMsgLock.acquire()
            self.send_message(test)
            self.sendMsgLock.release()

            
            # self.send_message(timestamp)
            # time.sleep(1)

            # command = self.receive_message()
        print(f'End of testing, clock offset history: {self.clock_offset_history}')
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
    global LOCAL_PORT
    LOCAL_PORT = ports[dancerId - 1]
    client = LaptopClient(dancerId)
    client.start()


if __name__ == '__main__':
    main()
