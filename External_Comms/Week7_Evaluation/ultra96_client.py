import socket
from Crypto.Cipher import AES
import base64
import time

SECRET_KEY = b'123456789abcdefg'  # 16 byte secret key used for AES
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

dummy_message = '#1 2 3|dab|1.87'


class Ultra96Client():
    def __init__(self, ip_addr, port_num):
        self.secret_key = SECRET_KEY
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_addr, port_num))
        print('Connected to Evaluation Server:', (ip_addr, port_num))

    def encrypt_message(self, message):
        cipher = AES.new(self.secret_key, AES.MODE_CBC)

        # pad message
        message += ' ' * (AES.block_size - (len(message) % AES.block_size))

        encrypted_msg = cipher.encrypt(message.encode())

        encoded_msg = base64.b64encode(cipher.iv + encrypted_msg)

        return encoded_msg

    def start(self):
        while 1:
            dance_move = input('Enter dance move: ')

            message = ''
            if dance_move == 'logout':
                message = '#|logout|'
            else:
                dancer_positions = input('Enter dancer positions: ')
                syncdelay = input('Enter sync delay: ')
                if dancer_positions == '' or dance_move == '' or syncdelay == '':
                    message = dummy_message
                else:
                    message = f'#{dancer_positions}|{dance_move}|{syncdelay}'

            try:
                print(f'Sending message: {message}')
                self.socket.sendall(self.encrypt_message(message))
                if dance_move == 'logout':
                    break
                data = self.socket.recv(1024)
                if not data:
                    print('No data received, server closed')
                    break
                print('New Dancer Positions (ground truth):', data.decode())
            except Exception as e:
                print('Error Host closed:', e)
                break

    def close(self):
        self.socket.close()


def main():
    client = Ultra96Client(HOST, PORT)
    client.start()
    client.close()


if __name__ == '__main__':
    main()
