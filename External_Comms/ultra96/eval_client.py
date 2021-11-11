import socket
from Crypto.Cipher import AES
import base64
import time
import threading

from config import DUMMY_SYNCDELAY, IS_EVAL, NUM_DANCERS, SECRET_KEY
from dashboard import send_position, send_syncdelay, send_alert

dummy_message = '#1 2 3|dab|1.87'

CURR_POS_TO_NEW_POS_MAPPINGS = {
    '1 2 3': {
        'N N N': '1 2 3',
        'R L N': '2 1 3',
        'N R L': '1 3 2',
        'R N L': '3 2 1',
        'R R L': '3 1 2',
        'R L L': '2 3 1'
    },
    '2 1 3': {
        'N N N': '2 1 3',
        'L R N': '1 2 3',
        'L R L': '1 3 2',
        'R R L': '3 2 1',
        'N R L': '3 1 2',
        'R N L': '2 3 1'
    },
    '1 3 2': {
        'N N N': '1 3 2',
        'N L R': '1 2 3',
        'R L R': '2 1 3',
        'R L L': '3 2 1',
        'R N L': '3 1 2',
        'R L N': '2 3 1'
    },
    '3 2 1': {
        'N N N': '3 2 1',
        'L N R': '1 2 3',
        'L L R': '2 1 3',
        'L R R': '1 3 2',
        'L R N': '3 1 2',
        'N L R': '2 3 1'
    },
    '3 1 2': {
        'N N N': '3 1 2',
        'L L R': '1 2 3',
        'N L R': '2 1 3',
        'L N R': '1 3 2',
        'R L N': '3 2 1',
        'R L R': '2 3 1'
    },
    '2 3 1': {
        'N N N': '2 3 1',
        'L R R': '1 2 3',
        'L N R': '2 1 3',
        'L R N': '1 3 2',
        'N R L': '3 2 1',
        'L R L': '3 1 2'
    }
}

class EvalClient(threading.Thread):
    def __init__(self, ip_addr, port_num, prediction, readyForEval, predictionLock, submittedToEval, dancerIsConnected, shutdown):
        threading.Thread.__init__(self)
        self.secret_key = SECRET_KEY
        self.prediction = prediction
        self.readyForEval = readyForEval
        self.predictionLock = predictionLock
        self.submittedToEval = submittedToEval
        self.dancerIsConnected = dancerIsConnected
        self.shutdown = shutdown
        
        if IS_EVAL:
            # ====================== WITH EVAL SERVER ======================
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip_addr, port_num))
            print('Connected to Evaluation Server:', (ip_addr, port_num))
            # ====================== WITH EVAL SERVER ======================

    def receive_message(self):
        data = self.socket.recv(1024)
        return data.decode()

    def send_message(self, message):
        self.socket.sendall(self.encrypt_message(message))

    def encrypt_message(self, message):
        cipher = AES.new(self.secret_key, AES.MODE_CBC)

        # pad message
        message += ' ' * (AES.block_size - (len(message) % AES.block_size))

        encrypted_msg = cipher.encrypt(message.encode())

        encoded_msg = base64.b64encode(cipher.iv + encrypted_msg)

        return encoded_msg

    def find_closest_positions_match(self, curr_position, predicted_position_shift):
        # pick first mapping with most number of matching position shifts
        most_similar = curr_position
        similarity_count = 0
        for position_shift in CURR_POS_TO_NEW_POS_MAPPINGS[curr_position]:
            matches = 0
            for i in range(0, 5, 2):
                if predicted_position_shift[i] == position_shift[i]:
                    matches += 1

            if matches > similarity_count:
                most_similar = position_shift
                similarity_count = matches

        return CURR_POS_TO_NEW_POS_MAPPINGS[curr_position][most_similar]
        
    
    def get_avg_dance_move(self, dance_moves):
        freq = {}
        for dance_move in dance_moves:
            if dance_move is None:
                continue
            if dance_move in freq.keys():
                freq[dance_move] += 1
                
            else:
                freq[dance_move] = 1
        return max(freq, key=freq.get)

    def run(self):
        while not self.shutdown.is_set():
            
            print('Eval Client: waiting for evaluation ready')
            self.readyForEval.wait()
            print('Eval Client: ready for evaluation')
            try:
                self.predictionLock.acquire()
                print('Acquired lock')

                # dance_move = self.get_avg_dance_move(self.prediction['dance_move'].values())
                dance_move = self.get_avg_dance_move([dancemove for dancerId in range(1, NUM_DANCERS+1) for dancemove in self.prediction['dance_moves_list'][dancerId]])
                print(f'\nFINAL dance moves: {dance_move}\n')

                if dance_move == 'logout':
                    self.shutdown.set()

                if NUM_DANCERS == 3:
                    # ========= FOR 3 DANCERS ========= relative position submission
                    curr_position = self.prediction['curr_position']
                    position_shift = ' '.join(self.prediction['position_shift'].values())

                    if position_shift not in CURR_POS_TO_NEW_POS_MAPPINGS[curr_position]:
                        print('POSITIONAL CHANGE WRONG................... no mapping found, using find closest matching position')
                        # find closest match to guess
                        self.prediction['new_position'] = self.find_closest_positions_match(curr_position, position_shift)
                    else:
                        self.prediction['new_position'] = CURR_POS_TO_NEW_POS_MAPPINGS[curr_position][position_shift]

                    new_positions = self.prediction['new_position']
                    print(f'\nFINAL relative positions: {new_positions}\n')
                    # ========= FOR 3 DANCERS =========
                elif NUM_DANCERS == 2:
                    # ========= FOR 2 DANCERS =========
                    new_positions = self.prediction["position_shift"][1] + self.prediction["position_shift"][2]
                    print(f'\nFINAL position shift: {new_positions}\n')
                    # ========= FOR 2 DANCERS =========
                else:
                    # ========= FOR 1 DANCER WTIHOUT EVAL SERVER =========
                    new_positions = self.prediction["position_shift"][1]
                    print(f'\nFINAL position shift: {new_positions}\n')
                    # ========= FOR 1 DANCER WTIHOUT EVAL SERVER =========

                start_timestamps = [timestamp for timestamp in self.prediction['start_timestamps'].values() if timestamp is not None]
                print(f'{len(start_timestamps)} start timestamps: {start_timestamps}')
                if len(start_timestamps) == 0 or len(start_timestamps) == 1:
                    print('SYNC DELAY WRONG........................................')
                    syncdelay = str(int(DUMMY_SYNCDELAY))
                else:
                    syncdelay = str(int((max(start_timestamps) - min(start_timestamps)) * 1000))
                print(f'\nFINAL syncdelay: {syncdelay}\n')


                submission = '#' + '|'.join([new_positions, dance_move, syncdelay])

                send_syncdelay(int(syncdelay))

                print(f'Sending message to eval server: {submission}')

                if IS_EVAL:
                    # ====================== WITH EVAL SERVER ======================
                    self.send_message(submission)

                    ground_truth_positions = self.receive_message()
                    if not ground_truth_positions:
                        print('No data received, server closed')
                        break
                    print('New Dancer Positions (ground truth):', ground_truth_positions)
                    send_position(ground_truth_positions)

                    # reset prediction object
                    self.prediction['curr_position'] = ground_truth_positions
                    self.prediction['new_position'] = None
                    # ====================== WITH EVAL SERVER ======================
                else:
                    # ====================== WITHOUT EVAL SERVER ======================
                    ground_truth_positions = new_positions
                    send_position(new_positions)
                    # ====================== WITHOUT EVAL SERVER ======================
                for i in range(1, NUM_DANCERS+1):
                    self.prediction['position_shift'][i] = 'N'
                    self.prediction['dance_move'][i] = None
                    self.prediction['start_timestamps'][i] = None
                    self.prediction['dance_moves_list'][i] = []

                send_alert(f'Submitted {dance_move}!')
            except Exception as e:
                print('Error Host closed:', e)
                break
            self.predictionLock.release()
            self.submittedToEval.set()
            self.readyForEval.clear()

        # ====================== WITH EVAL SERVER ======================
        if IS_EVAL:
            self.close()
        # ====================== WITH EVAL SERVER ======================
    def close(self):
        self.socket.close()

