import socket
from Crypto.Cipher import AES
import base64
import time
import threading

from config import SECRET_KEY, EVAL_HOST, EVAL_PORT
from dashboard import send_prediction

dummy_message = '#1 2 3|dab|1.87'


class EvalClient(threading.Thread):
    def __init__(self, ip_addr, port_num, prediction, readyForEval, predictionLock):
        threading.Thread.__init__(self)
        self.secret_key = SECRET_KEY
        self.prediction = prediction
        self.readyForEval = readyForEval
        self.predictionLock = predictionLock

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_addr, port_num))
        print('Connected to Evaluation Server:', (ip_addr, port_num))

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
    
    def get_avg_dance_move(self, dance_moves):
        freq = {}
        for dance_move in dance_moves.values():
            if dance_move in freq.keys():
                freq[dance_move] += 1
                
            else:
                freq[dance_move] = 1
        return max(freq, key=freq.get)

    def run(self):
        # self.dancersConnected.wait()
        while 1:
            
            # dance_move = input('Enter dance move: ')

            # message = ''
            # if dance_move == 'logout':
            #     message = '#|logout|'
            # else:
            #     dancer_positions = input('Enter dancer positions: ')
            #     syncdelay = input('Enter sync delay: ')
            #     if dancer_positions == '' or dance_move == '' or syncdelay == '':
            #         message = dummy_message
            #     else:
            #         message = f'#{dancer_positions}|{dance_move}|{syncdelay}'
            print('Eval Client: waiting for evaluation ready')
            self.readyForEval.wait()
            print('Eval Client: ready for evaluation')
            try:
                self.predictionLock.acquire()
                print('Acquired lock')
                positions = self.prediction['positions']
                print('get positions')
                dance_move = self.get_avg_dance_move(self.prediction['dance_move'])
                print('get dance move')
                syncdelay = self.prediction['syncdelay']
                print('get syncdelay')
                submission = '|'.join([positions, dance_move, syncdelay])

                # TODO send sync delay to dashboard

                print(f'Sending message to eval server: {submission}')
                self.send_message(submission)
                # self.socket.sendall(self.encrypt_message(dummy_message))
                # if dance_move == 'logout':
                #     break
                data = self.receive_message()
                if not data:
                    print('No data received, server closed')
                    break
                print('New Dancer Positions (ground truth):', data)

                # reset prediction object
                for dancerId in self.prediction['dance_move']:
                    self.prediction['dance_move'][dancerId] = None

                # TODO if dancer position ground truth != submitted dancer positions, update dancer positions



                self.predictionLock.release()
            except Exception as e:
                print('Error Host closed:', e)
                break
            self.readyForEval.clear()
        self.close()

    def close(self):
        self.socket.close()


def main():
    client = EvalClient(EVAL_HOST, EVAL_PORT, {'positions': '1 2 3', 'dance_move': '', 'syncdelay': 1.87}, threading.Event())
    client.start()


if __name__ == '__main__':
    main()
