from datetime import datetime
import queue
import sys

import client
import bluno
import globals_


BEETLE_0 = "b0:b1:13:2d:b3:1a"
BEETLE_1 = "b0:b1:13:2d:b4:7d"
BEETLE_2 = "b0:b1:13:2d:d7:97"

Connect_Header = "++++++++++++++++++++++++++++++++++++++++++++++++++++"
Disconnect_Header = "----------------------------------------------------"
Data_Header = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
Reconnect_Header = "####################################################"
newline = "\n"

address = [BEETLE_0, BEETLE_1, BEETLE_2]
address_map = {}

inputQueue = queue.Queue() 

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Invalid number of arguments')
        print('python main.py [Dancer ID]')
        sys.exit()
    dancerId = int(sys.argv[1])
    handleServer = client.LaptopClient(dancerId)
    handleServer.start()
    for i in range(10):
        globals_.dataQueue.put(f'test packet {i}')
    
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
