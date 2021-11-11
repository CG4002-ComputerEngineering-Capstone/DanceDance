import socket
import time
import queue
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
import base64

from config import BLUNO_LAPTOP_CONNECTED, BLUNO_LAPTOP_DISCONNECTED, NUM_CLOCK_SYNC_ITERATIONS, PREPROCESSED_VECTOR_LEN, SERVER_PORT, SERVER_HOST, NUM_DANCERS
from dashboard import send_move, send_alert


clockSyncLock = threading.Lock()

class Dancer(threading.Thread):
    def __init__(self, dancerId, connection, dataQueue, readyForEval, clockSyncFlag, clearDataQueueFlag, prediction, predictionLock, dancerIsConnected, hasRecvPositionalChange, shutdown, predictionListPtr, predictionListPtrLock):
        threading.Thread.__init__(self)
        self.dancerId = dancerId
        self.connection = connection
        self.dataQueue = dataQueue
        self.readyForEval = readyForEval
        self.clockSyncFlag = clockSyncFlag
        self.clearDataQueueFlag = clearDataQueueFlag
        self.prediction = prediction
        self.predictionLock = predictionLock
        self.dancerIsConnected = dancerIsConnected
        self.hasRecvPositionalChange = hasRecvPositionalChange
        self.shutdown = shutdown
        self.predictionListPtr = predictionListPtr
        self.predictionListPtrLock = predictionListPtrLock

    def send_message(self, message):
        bytes_message = base64.b64encode(str.encode(str(message)))
        self.connection.sendall(bytes_message)

    def receive_message(self):
        data = self.connection.recv(1024)
        # print(f'recv_msg data: {data}')

        return base64.b64decode(data).decode()

    def clock_sync(self):
        print(f'[{self.dancerId}] ******************************start clock sync************************')
        for i in range(NUM_CLOCK_SYNC_ITERATIONS):
            # notify start of clock sync
            self.send_message('ready')

            data = self.receive_complete()
            t1 = time.time()

            if data[0] == 'syncpacket':
                t2 = time.time()
                self.send_message(str(t1) + '|' + str(t2))

                # print(f'Sending t1 {t1} and t2 {t2}')
                data = self.receive_complete()
                # print(f'clock sync data: {data}')
                if data[0] != 'end':
                        print(f'[{self.dancerId}] Clock sync failed')
                        sys.exit()

                # handle incoming data if received more than 'end' message
                if len(data) > 1:
                    for idx, element in enumerate(data):
                        if idx == 0: continue
                        if element == 'L' or element == 'R':
                            self.handle_poschange(element)
                        elif element == BLUNO_LAPTOP_CONNECTED or element == BLUNO_LAPTOP_DISCONNECTED:
                            self.handle_bluno_laptop_state(element)
                        else:
                            self.handle_dancemove_data(element, False)

            else:
                print(f'[{self.dancerId}] Clock sync failed')
                sys.exit()


    def receive_complete(self):
        data = b''
        is_complete = False
        while not is_complete: 
            data += self.connection.recv(4096)
            if not data:
                return ['']
            if data[-1] == 124: # 124 is ascii value of '|', which is used as delimiter between sets of sample values
                is_complete = True

        data_array = data.split(b'|')
        decoded_data_array = []
        try:
            for x in data_array:
                decoded = base64.b64decode(x).decode()
                if decoded != '':
                    decoded_data_array.append(decoded)
            # print(f'[{self.dancerId}] successfully received full data')
            return decoded_data_array
        except Exception as e:
            print(e)
            print(data)
            print(data_array)
            print(x)
            sys.exit()
            

    def handle_clocksync(self):
        clockSyncLock.acquire()
        print(f'[{self.dancerId}] Dancer {self.dancerId} starting clock sync')
        self.clock_sync()
        print(f'[{self.dancerId}] Dancer {self.dancerId} finished clock sync')
        clockSyncLock.release()

    
    def handle_poschange(self, position_change):
        if not self.hasRecvPositionalChange[self.dancerId-1]:
            print(f'[{self.dancerId}] receive position shift "{position_change}"')
            if NUM_DANCERS == 1:
                send_alert(f"Position change: {position_change}")
            self.predictionLock.acquire()
            self.prediction['position_shift'][self.dancerId] = position_change
            self.predictionLock.release()
            self.hasRecvPositionalChange[self.dancerId-1] = True


    def handle_dancemove_data(self, data, isClearingData):
        
        # print(f'[{self.dancerId}] receive sensor data for dance move')
        vector = data.split(',')
        vector = list(map(float, vector))
        if len(vector) > PREPROCESSED_VECTOR_LEN:
            timestamp = vector.pop(0)
            print(f'[{self.dancerId}] received timestamp: {timestamp}')
            self.dataQueue.put([timestamp])

        if not isClearingData:
            self.dataQueue.put(vector)



    def handle_bluno_laptop_state(self, data):
        if data == BLUNO_LAPTOP_CONNECTED:
            # set connected state to True
            self.dancerIsConnected[self.dancerId - 1] = True
            send_move(self.dancerId, 'CONNECTED')
            print(f'[{self.dancerId}] CONNECTED')
            self.predictionListPtrLock.acquire()
            self.predictionListPtr[0] += 1
            self.predictionListPtrLock.release()
        elif data == BLUNO_LAPTOP_DISCONNECTED:
            # set connected state to False
            self.dancerIsConnected[self.dancerId - 1] = False
            send_move(self.dancerId, 'DISCONNECTED')
            print(f'[{self.dancerId}] DISCONNECTED')
            self.predictionListPtrLock.acquire()
            self.predictionListPtr[0] -= 1
            self.predictionListPtrLock.release()
        

    def run(self):
        print(f'Dancer {self.dancerId} connected')
        self.send_message('server_ready')
        time.sleep(0.1)

        # initial clock sync 
        self.send_message('sync')

        while not self.shutdown.is_set():
            # 2. Receive data from clients
            data = self.receive_complete()
            if not data or (len(data) == 1 and data[0] == ''):
                break
            
            # print(f'[{self.dancerId}] received:', len(data))
            
            if self.clearDataQueueFlag.is_set():
                # when clearDataQueueFlag is set, means enough data gathered for prediction, so ignore incoming sensor data packets and clear queue

                # print(f'[{self.dancerId}] Dancer {self.dancerId} waiting for eval, clearing queue and discarding data.......')
                for element in data:
                    if element == 'sync':
                        # perform clock sync
                        self.handle_clocksync()
                    elif element == 'L' or element == 'R':
                        self.handle_poschange(element)
                    elif element == BLUNO_LAPTOP_CONNECTED or element == BLUNO_LAPTOP_DISCONNECTED:
                        self.handle_bluno_laptop_state(element)
                    else:
                        self.handle_dancemove_data(element, True)
                try:
                    throw_away = self.dataQueue.get_nowait()
                    if len(throw_away) == 1: # if ultra96 received timestamp during clearDataQueue, dont clear time stamp
                        self.dataQueue.put(throw_away)
                    continue
                except queue.Empty:
                    continue
                
            else:
                for element in data:
                    if element == 'sync':
                        # perform clock sync
                        self.handle_clocksync()
                    elif element == 'L' or element == 'R':
                        self.handle_poschange(element)
                    elif element == BLUNO_LAPTOP_CONNECTED or element == BLUNO_LAPTOP_DISCONNECTED:
                        self.handle_bluno_laptop_state(element)
                    else:
                        # default receiving packets
                        self.handle_dancemove_data(element, False)
                        
            
            

        self.connection.close()
        print(f'[{self.dancerId}] Dancer {self.dancerId} has disconnected')
        send_move(self.dancerId, '-')
        if self.dancerIsConnected[self.dancerId - 1] != False:
            self.dancerIsConnected[self.dancerId - 1] = False
            self.predictionListPtrLock.acquire()
            self.predictionListPtr[0] -= 1
            self.predictionListPtrLock.release()


class Ultra96Server(threading.Thread):
    def __init__(self, ip_addr, port, dataQueues, prediction, readyForEval, clockSyncFlags, clearDataQueueFlags, predictionLock, dancerIsConnected, hasRecvPositionalChange, shutdown, predictionListPtr, predictionListPtrLock):
        threading.Thread.__init__(self)
        self.clients = {}
        self.dataQueues = dataQueues
        self.prediction = prediction
        self.predictionLock = predictionLock
        self.readyForEval = readyForEval
        self.clockSyncFlags = clockSyncFlags
        self.clearDataQueueFlags = clearDataQueueFlags
        self.dancerIsConnected = dancerIsConnected
        self.hasRecvPositionalChange = hasRecvPositionalChange
        self.shutdown = shutdown
        self.predictionListPtr = predictionListPtr
        self.predictionListPtrLock = predictionListPtrLock

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip_addr, port))
        print('Socket server listening on', self.socket.getsockname())
        self.socket.listen(0)



    def broadcast_message(self, message):
        for dancer in self.clients.values():
            dancer.send_message(message)
    
    def receive_message(self, connection):
        data = connection.recv(1024)
        return base64.b64decode(data).decode()


    def accept_connections(self):
        while not self.shutdown.is_set():
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
            dancerId = int(dancerId)

            self.clients[dancerId] = Dancer(dancerId, client_connection, self.dataQueues[dancerId-1], self.readyForEval, self.clockSyncFlags[dancerId-1], self.clearDataQueueFlags[dancerId-1], self.prediction, self.predictionLock, self.dancerIsConnected, self.hasRecvPositionalChange, self.shutdown, self.predictionListPtr, self.predictionListPtrLock)
            self.clients[dancerId].start()
                
        # notify laptop clients of logout
        self.broadcast_message('logout')
    
    def handle_clocksyncs(self):
        while not self.shutdown.is_set():
            has_timed_out = False
            for i in range(len(self.clockSyncFlags)):
                result = self.clockSyncFlags[i].wait(timeout=2.0)
                if not result:
                    has_timed_out = True
                    break
            if has_timed_out:
                continue

            for i in range(len(self.clockSyncFlags)):
                self.clockSyncFlags[i].clear()
            # notify all clients to do clock sync
            time.sleep(0.1)
            self.broadcast_message('sync')

            

    def run(self):
        # 1. Accept connections from dancers
        print('Server started, ready to receive conenctions from dancers')
        handle_clocksyncs_thread = threading.Thread(target=self.handle_clocksyncs)
        handle_clocksyncs_thread.start()

        self.accept_connections()
        
        # After all threads close
        print('Closing server now')
        self.close()

    def close(self):
        self.socket.close()    

