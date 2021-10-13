import socket
import time
import queue
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
import base64

from config import SERVER_PORT, SERVER_HOST, NUM_DANCERS


barrier = threading.Barrier(NUM_DANCERS + 1)
clockSyncBarrier = threading.Barrier(NUM_DANCERS)
clockSyncLock = threading.Lock()

class Dancer(threading.Thread):
    def __init__(self, dancerId, connection, dataQueue, readyForEval):
        threading.Thread.__init__(self)
        self.dancerId = dancerId
        self.connection = connection
        self.dataQueue = dataQueue
        self.readyForEval = readyForEval

    def send_message(self, message):
        bytes_message = base64.b64encode(str.encode(str(message)))
        self.connection.sendall(bytes_message)

    def receive_message(self):
        data = self.connection.recv(1024)

        return base64.b64decode(data).decode()

    def clock_sync(self):
        for i in range(5):
            # notify start of clock sync
            self.send_message('ready')

            data = self.receive_message()
            t1 = time.time()

            if data == 'syncpacket':
                t2 = time.time()
                self.send_message(str(t1) + '|' + str(t2))

                print(f'Sending t1 {t1} and t2 {t2}')
                data = self.receive_message()
                if data != 'end':
                    print('Clock sync failed')
                    sys.exit()
            else:
                print('Clock sync failed')
                sys.exit()


    def receive_complete(self):
        data = b''
        is_complete = False
        while not is_complete: # 124 is ascii value of '|', which is used as delimiter between sets of sample values
            data += self.connection.recv(4096)
            if not data:
                return ['']
            if data[-1] == 124:
                is_complete = True

        data_array = data.split(b'|')
        decoded_data_array = []
        try:
            for x in data_array:
                decoded = base64.b64decode(x).decode()
                if decoded != '':
                    decoded_data_array.append(decoded)
            print('successfully received full data')
            return decoded_data_array
        except Exception as e:
            print(e)
            print(data)
            print(data_array)
            print(x)
            sys.exit()
            


    def run(self):
        print(f'Dancer {self.dancerId} connected')
        self.send_message('server_ready')
        # 1. wait for all dancers to conenct
        time.sleep(2)

        sensor_data = []
        # self.timer.start()
        # while not self.evaluation_ended.is_set():
        while 1:
            print('Receiving data from client loop..')            

            # 2. Receive data from clients
            data = self.receive_complete()
            if not data or (len(data) == 1 and data[0] == ''):
                break
            
            print('received:', len(data))
            
            if data[0]== 'sync':
                # 3. Ensure all threads reach this point, then allow one by one to perform clock sync
                clockSyncBarrier.wait()
                clockSyncLock.acquire()
                print(f'Dancer {self.dancerId} starting clock sync')
                self.clock_sync()
                print(f'Dancer {self.dancerId} finished clock sync')
                clockSyncLock.release()
            else:
                # default receiving packets
                for window in data:
                    vector = window.split(',')
                    vector = list(map(float, vector))
                    self.dataQueue.put(vector)
                    print('added to preprocessed vector queue')
            

        self.connection.close()
        print(f'Dancer {self.dancerId} has disconnected')

class Ultra96Server(threading.Thread):
    def __init__(self, ip_addr, port, dataQueues, prediction, readyForEval):
        threading.Thread.__init__(self)
        self.clients = {}
        self.dancer_start_times = {}
        self.dataQueues = dataQueues
        self.prediction = prediction
        self.readyForEval = readyForEval

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip_addr, port))
        print('Socket server listening on', self.socket.getsockname())
        self.socket.listen(0)

        self.evaluation_ended = threading.Event()
        # self.timer = threading.Timer(60, self.end_eval)


    def broadcast_message(self, message):
        for dancer in self.clients.values():
            # self.send_message(connection, message)
            dancer.send_message(message)
    
    def receive_message(self, connection):
        data = connection.recv(1024)
        return base64.b64decode(data).decode()


    def end_eval(self):
        print("eval ended")
        self.evaluation_ended.set()
        print(self.evaluation_ended.is_set())


    def accept_connections(self):
        while not self.evaluation_ended.is_set():
            # print('start of loop')
            try:
                self.socket.settimeout(5.0)
                client_connection, addr = self.socket.accept()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print('keyboardInterrupt')
                sys.exit()
            print('Connected to:', addr)
            dancerId = self.receive_message(client_connection)
            # if dancerId in self.clients:
            #     available_dancerIds = [x for x in range(1, 3) if x not in self.clients]
            #     self.send_message(client_connection, f'DancerId already exists, please try again with one of the available dancerIds: {available_dancerIds}')

            self.clients[dancerId] = Dancer(dancerId, client_connection, self.dataQueues[int(dancerId)-1], self.readyForEval)
            self.clients[dancerId].start()

            # executor.submit(self.handle_client, client_connection, dancerId)
            print(self.evaluation_ended.is_set())

    def run(self):
        
        # 1. Accept connections from dancers
        print('Server started, ready to receive conenctions from dancers')
        # self.timer.start()
        self.accept_connections()

        # 2. 
        

        # with ThreadPoolExecutor() as executor:
            
            # print("eval ended, not accepting more threads")
                

            # 2. Signal to client threads that all dancers have conencted
            # barrier.wait()
            # commands = ['sync', 'test', 'end']
            
            # while 1:
            #     # 3. Enter command
            #     print()
            #     # command = input('Enter command: ')
            #     # print(f'command entered: {command}')
            #     # while command not in commands:
            #     #     command = input('Valid commands:\n\tsync\n\ttest\n\tend\nPlease try again: ')
            #     #     print(f'command entered: {command}')
            #     # self.broadcast_message(command)
            #     # if command == 'end':
            #     #     break

            #     # 4. Wait until all threads finished computation
            #     barrier.wait()

            #     if command == 'test':
            #         earliest_start_time = min(self.dancer_start_times.values())
            #         latest_start_time = max(self.dancer_start_times.values())
            #         syncdelay = latest_start_time - earliest_start_time
            #         print(f'Syncdelay: {syncdelay}')
            #     barrier.wait()
        
        # After all threads close
        print('Closing server now')
        self.close()

    def close(self):
        self.socket.close()    

def main():
    server = Ultra96Server(SERVER_HOST, SERVER_PORT)
    print('Starting server now')
    server.start()

if __name__ == '__main__':
    main()
