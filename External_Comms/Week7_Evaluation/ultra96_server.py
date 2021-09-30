import socket
import time
import queue
import threading
import sys
from concurrent.futures import ThreadPoolExecutor

HOST = '127.0.0.1'
PORT = 65432        # Port to listen on

NUM_THREADS = 3
barrier = threading.Barrier(NUM_THREADS + 1)
clockSyncBarrier = threading.Barrier(NUM_THREADS)
clockSyncLock = threading.Lock()

class Ultra96Server():
    def __init__(self, ip_addr, port):
        self.clients = {}
        self.dancer_start_times = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip_addr, port))
        print('Socket server listening on', self.socket.getsockname())
        self.socket.listen()

    def send_message(self, connection, message):
        bytes_message = str.encode(str(message))
        connection.sendall(bytes_message)

    def receive_message(self, connection):
        data = connection.recv(1024)
        return data.decode()

    def broadcast_message(self, message):
        for connection, addr in self.clients.values():
            self.send_message(connection, message)
        
    
    def clock_sync(self, connection):
        for i in range(5):
            # notify start of clock sync
            self.send_message(connection, 'ready')

            data = self.receive_message(connection)
            t1 = time.time()

            if data == 'syncpacket':
                t2 = time.time()
                self.send_message(connection, str(t1) + '|' + str(t2))

                print(f'Sending t1 {t1} and t2 {t2}')
                data = self.receive_message(connection)
                if data != 'end':
                    print('Clock sync failed')
                    sys.exit()
            else:
                print('Clock sync failed')
                sys.exit()

    def handle_client(self, connection, dancerId):
        print(f'Dancer {dancerId} connected')
        # 1. wait for all dancers to conenct
        barrier.wait()

        while 1:
            # 2. Receive data from clients
            data = self.receive_message(connection)
            # print('received:', data)
            if not data:
                break
            if data == 'sync':
                # 3. Ensure all threads reach this point, then allow one by one to perform clock sync
                clockSyncBarrier.wait()
                clockSyncLock.acquire()
                print(f'Dancer {dancerId} starting clock sync')
                self.clock_sync(connection)
                print(f'Dancer {dancerId} finished clock sync')
                clockSyncLock.release()
            else:
                self.dancer_start_times[dancerId] = float(data)

            # 4. Wait for all threads to finish computation
            barrier.wait()
            # 5. Wait for syncdelay computation
            barrier.wait()
            
            
        connection.close()
        print(f'Dancer {dancerId} has disconnected')

    def start(self):
        # 1. Accept connections from dancers
        with ThreadPoolExecutor() as executor:
            for i in range(NUM_THREADS):
                client_connection, addr = self.socket.accept()
                print('Connected to:', addr)
                dancerId = self.receive_message(client_connection)
                executor.submit(self.handle_client, client_connection, dancerId)
                self.clients[dancerId] = (client_connection, addr)   

            # 2. Signal to client threads that all dancers have conencted
            barrier.wait()
            commands = ['sync', 'test', 'end']
            
            while 1:
                # 3. Enter command
                print()
                command = input('Enter command: ')
                print(f'command entered: {command}')
                while command not in commands:
                    command = input('Valid commands:\n\tsync\n\ttest\n\tend\nPlease try again: ')
                    print(f'command entered: {command}')
                self.broadcast_message(command)
                if command == 'end':
                    break

                # 4. Wait until all threads finished computation
                barrier.wait()

                if command == 'test':
                    earliest_start_time = min(self.dancer_start_times.values())
                    latest_start_time = max(self.dancer_start_times.values())
                    syncdelay = latest_start_time - earliest_start_time
                    print(f'Syncdelay: {syncdelay}')
                barrier.wait()

    def close(self):
        self.socket.close()    


if __name__ == '__main__':
    server = Ultra96Server(HOST, PORT)
    print('Starting server now')
    server.start()
    print('Closing server now')
    server.close()
