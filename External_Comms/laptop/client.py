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
# from liveProcess import append, resetCumData
# from elevenLive import append, resetCumData
from finaleLive import append, resetCumData


LOCAL_PORTS = [65432, 65431, 65430]
LOCAL_PORT = 65432
REMOTE_PORT = 65432

STEP_DIRECTION_MAPPING = {
    1: 'L',
    2: 'R'
}


class LaptopClient(threading.Thread):
    def __init__(self, dancerId, clientConnectedFlag):
        threading.Thread.__init__(self)
        self.dancerId = dancerId
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clock_offset = 0
        self.clientConnectedFlag = clientConnectedFlag
        self.sendMsgLock = threading.Lock()
        self.shutdown = threading.Event()

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
            local_bind_address=('127.0.0.1', LOCAL_PORTS[self.dancerId-1]),
            ssh_username='xilinx',
            ssh_password='xilinx'
        )
        tunnel2.start()
        print(f'Connection to tunnel2 OK: {tunnel2.tunnel_bindings}')

        self.socket.connect(('localhost', LOCAL_PORTS[self.dancerId-1]))
        print('Successfully connected to Ultra96!')
        self.clientConnectedFlag.set()
        self.send_message(self.dancerId)

    def clock_sync(self):
        print(f'[clock sync thread] Acquiring sendMsgLock...')
        self.sendMsgLock.acquire()
        print(f'[clock sync thread] Acquired sendMsgLock!')

        self.send_message('sync')
        offsets_array = []
        for i in range(globals_.NUM_CLOCK_SYNC_ITERATIONS):
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

        print(f'Average Clock Offset: {self.clock_offset}')
        print(f'[clock sync thread] Releasing sendMsgLock...')
        self.sendMsgLock.release()
        print(f'[clock sync thread] Released sendMsgLock!')


    def handle_server(self):
        while not self.shutdown.is_set():
            # wait for command from server to begin clock_sync
            command = self.receive_message()
            if command == 'logout':
                self.shutdown.set()
            elif command == 'sync':
                self.clock_sync()
                

    def run(self):
        self.setup_connection()
        
        command = self.receive_message()
        print('received message:', command)
        if command != 'server_ready':
            print('did not receive "server_ready" from server, exiting..')
            return
        
        handle_server_thread = threading.Thread(target=self.handle_server)
        handle_server_thread.start()

        while not self.shutdown.is_set():
            # receive data indicating server is ready
            sample = []
            timestamp = None
            while not self.shutdown.is_set() and len(sample) < globals_.PACKET_WINDOW_SIZE:
                data = globals_.dataQueue.get()
                # print(f'data from bluno: {data}')
                # print(type(data))
                
                if len(data) == 1:
                    if data[0] == globals_.BLUNO_LAPTOP_DISCONNECTED or data[0] == globals_.BLUNO_LAPTOP_CONNECTED:
                        # bluno-laptop connections and disconnections
                        message_to_send = data[0]
                    else:
                        # positional change packet
                        message_to_send = STEP_DIRECTION_MAPPING[data[0]]
                    print(f'[main client thread] Acquiring sendMsgLock...')
                    self.sendMsgLock.acquire()
                    print(f'[main client thread] Acquired sendMsgLock! sending "{message_to_send}"')

                    self.send_message(message_to_send)

                    print(f'[main client thread] Releasing sendMsgLock...')
                    self.sendMsgLock.release()
                    print(f'[main client thread] Released sendMsgLock!')
                    
                elif len(data) == 6: 
                    # If data is the packet containing timestamp of start of dance move i.e. timestamp + 6 sensor values, call resetCumData, clear sample and append to sample
                    resetCumData()
                    sample = []
                    print(f'RESET SAMPLE - sample length: {len(sample)}')

                    timestamp = float(data[0]) - self.clock_offset
                    print(f'timestamp: {timestamp}')
                    sample.append(data[1:])
                    # print(f'Sample length: {len(sample)}')
                else:
                    # normal IMU sensor data packet
                    sample.append(data)
                    # print(f'Sample length: {len(sample)}')

            if self.shutdown.is_set():
                break

            # print(f'enough sample length: {sample}')
                        
            # send sensor readings to dashboard
            print('send_sensor to dashboard')
            send_sensor(self.dancerId, sample)

            # preprocess data before sending to ultra96
            vector = append(sample)
            # print(f'vector shape: {vector.shape}')
            
            for v in vector:
                if self.shutdown.is_set():
                    break
                v = list(v)
                if timestamp is not None:
                    v.insert(0, timestamp)
                    timestamp = None
                # print(f'Length of vector to send: {len(v)}')
                vector_string = ','.join(list(map(str, v)))
                
                # print(f'[main client thread] Acquiring sendMsgLock...')
                self.sendMsgLock.acquire()
                # print(f'[main client thread] Acquired sendMsgLock!')
                self.send_message(vector_string)
                # print(f'[main client thread] Releasing sendMsgLock...')
                self.sendMsgLock.release()
                # print(f'[main client thread] Released sendMsgLock!')
                time.sleep(0.1)

        
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
    LOCAL_PORT = LOCAL_PORTS[dancerId - 1]
    client = LaptopClient(dancerId)
    client.start()


if __name__ == '__main__':
    main()
