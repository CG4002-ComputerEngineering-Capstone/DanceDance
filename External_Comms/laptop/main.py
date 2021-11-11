from datetime import datetime
import queue
import sys
import random
import time
import threading
import client
import bluno
import globals_


BEETLE_4 = "b0:b1:13:2d:b4:19"
# BEETLE_5 = "b0:b1:13:2d:b5:13"
#BEETLE_6 = "b0:b1:13:2d:d4:86"

#>>>>> SETUP BLUNO MAC ADDRESS >>>>>>>>
address = [BEETLE_4]

Connect_Header = "++++++++++++++++++++++++++++++++++++++++++++++++++++"
Disconnect_Header = "----------------------------------------------------"
Data_Header = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
Reconnect_Header = "####################################################"
newline = "\n"
address_map = {}


for i in range(len(address)):
    address_map[address[i]] = i

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Invalid number of arguments')
        print('python main.py [Dancer ID]')
        sys.exit()

    clientConnectedFlag = threading.Event()
    dancerId = int(sys.argv[1])
    handleServer = client.LaptopClient(dancerId, clientConnectedFlag)
    handleServer.start()

    clientConnectedFlag.wait()
    print('Clients connected, waiting for bluetooth')
    
    for addr in address:
        count = 0
        start = datetime.now()
        print(newline)
        print(Connect_Header)
        print("Attempting to connect to beetle ID: ",
              address_map[addr], "at", start)
        beetle = bluno.Setup.setPeripheral(addr)
        if (beetle != 1):
            print("Succesfully formed peripheral w beetleID ",
                  address_map[addr])
            bluno.main_thread(beetle, address_map[addr]).start()

        else:
            print("retry peripheral connection\n")
            while (count < 3):
                count += 1
                beetle = bluno.Setup.setPeripheral(addr)

            if(beetle == 1):
                print("tried 3 times, cannot form peri\n")
            else:
                print("successful retry to form peripheral w beetleID ",
                      address_map[addr])
                print(Connect_Header)
                print(newline)
                bluno.main_thread(beetle, address_map[addr]).start()
            continue
