from bluepy import btle
from time import time, sleep
from datetime import datetime
import threading
import struct
import time
import csv

service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
#BEETLE_0 = "b0:b1:13:2d:b3:1a"
BEETLE_1 = "b0:b1:13:2d:d4:86"
#BEETLE_2 = "b0:b1:13:2d:d7:97"
#BEETLE_0 = "b0:b1:13:2d:b4:19"
#BEETLE_3 = "b0:b1:13:2d:b4:7d"

Connect_Header = "++++++++++++++++++++++++++++++++++++++++++++++++++++"
Disconnect_Header = "----------------------------------------------------"
Data_Header = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
Reconnect_Header = "####################################################"
newline = "\n"

 
csv_time = 0
address = [BEETLE_1]
global_delegate = []
[global_delegate.append(0) for idx in range(len(address))]
address_map = {}
disconnect_map = {}
handshake_map = {}
start_time = {}
buffer_map = {} 
train_data = []
for i in range(len(address)):
    address_map[address[i]] = i

for i in range(len(address)):
    disconnect_map[address[i]] = False

for i in range(len(address)):
    start_time[address[i]] = 0

for i in range(len(address)):
    buffer_map[address[i]] = b""

for i in range(len(address)):
    handshake_map[address[i]] = False


def main():
    #BLE = Setup.scan()
    for addr in address:
        count = 0
        start = datetime.now()
        print(newline)
        print(Connect_Header)
        print("Attempting to connect to beetle ID: ", address_map[addr], "at", start)
        beetle = Setup.setPeripheral(addr)
        if (beetle != 1):
            print("Succesfully formed peripheral w beetleID ", address_map[addr])
            main_thread(beetle, address_map[addr]).start()

        else:
            print("retry peripheral connection\n")
            while (count < 3):
                count += 1
                beetle = Setup.setPeripheral(addr)

            if(beetle == 1):
                print("tried 3 times, cannot form peri\n")
            else:
                print("successful retry to form peripheral w beetleID ", address_map[addr])
                print(Connect_Header)
                print(newline)
                main_thread(beetle, address_map[addr]).start()
            continue


    #print("\n")
    #print("Formed peripheral with ", no_of_beetles, " beetles")
    
def checksum_ack(packet):
    check = packet[0] ^ packet[1] ^ packet[2] ^ packet[3] ^ packet[4] ^ packet[5] ^ packet[6] ^ packet[7] ^ packet[8] ^ packet[9]
    print(check)
    if check == packet[10]:
        return True
    return False

def checksum_imu(packet):
    check = packet[0] ^ packet[1] ^ packet[2] ^ packet[3] ^ packet[4] ^ packet[5] ^ packet[6] ^ packet[7] 
    if check == packet[8]:
        return True
    return False


def checksum_emg(packet):
    check = packet[0] ^ packet[1] ^ packet[2] ^ packet[3] ^ packet[4] ^ packet[5] ^ packet[6] ^ packet[7] ^ packet[8] ^ packet[9]
    if check == packet[10]:
        return True
    return False


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        self.address = params

    def handleNotification(self, cHandle, data):
        for i in range(len(address)):
            if address[i] == self.address:
                packet = data
                size = len(packet)
                addr = self.address
                correct_size = False


                if size < 20:                
                    if buffer_map[addr] == b"":
                        buffer_map[addr] = packet
                        print(Data_Header)
                        print("Beetle ID: ", i)
                        print("New fragmented data found of size:", size, " bytes")
                        print(Data_Header)
                        print(newline)

                    else:
                        packet = buffer_map[addr] + data
                        if len(packet) == 20:
                            print(Data_Header)
                            print("Beetle ID: ", i)
                            print("Fragmented data has been stitched up")
                            print(Data_Header)
                            print(newline)
                            correct_size = True
                            buffer_map[addr] = b""
                        else:
                            print("still fragmented")
                            buffer_map[addr] = packet
                            if(len(buffer_map[addr]) > 20):
                                buffer_map[addr] =  b""
            

                else:
                    correct_size = True


                if(correct_size):
                    buffer_map[addr] =  b""
                    packet_type = struct.unpack("!b", packet[:1])[0]
                    #print(packet_type)

                    if packet_type == 1:
                        packet = struct.unpack("<bhhhhhhhhbh", packet)
                        if (checksum_ack(packet)):
                            handshake_map[addr] = True
                            print(Connect_Header)
                            print("Successfully Received ACK packet from beetle ID ", i)
                            print("Checksum correct!")
                            print(packet)
                            print(Connect_Header)
                            print(newline)

                    elif packet_type == 2 and handshake_map[addr] == True:
                        packet = struct.unpack("<bhhhihhbi", packet)
                        global csv_time
                        #print(Data_Header)
                        #print("Receiving data from beetle ID: ", i)
                        if(checksum_imu(packet)):
                            #print("Checksum correct!")
                            #print(packet)
                            #print(Data_Header)
                            #print(newline)
                            #print(time.time() - csv_time)
                            #csv_time = time.time()
                            if (len(train_data) < 3100):
                                real_data = packet[1:10]
                                #print("real data:", real_data)
                                train_data.append(list(real_data))

                        elif(not checksum_imu(packet)):
                            print("WRONG CHECKSUM")

                        if (len(train_data) == 1200):
                            print("reached CSV")
                            #print(train_data)
                            print(type(real_data))
                            print(time.time() - csv_time)
                            with open("jamesbond_matthew_4_.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(train_data)
                                            

                    elif packet_type == 3 and handshake_map[addr] == True:
                        packet = struct.unpack("<bhhhhhhhhbh", packet)
                        print(Data_Header)
                        print("Receiving data from beetle ID: ", i)
                        if(checksum_emg(packet)):
                            print("Checksum correct!")
                        print(packet)
                        print(Data_Header)
                        print(newline)

                        #print(packet)

                        


                


                #packetType = struct.unpack("!b", data[:1])[0]
                #print(len(data))
                #print(packetType)
                #print(data)
            #packet = struct.unpack('!c', data)         
            #print("Notif received")
            #print(cHandle)
            #print(packet[0])


class Setup:
    def setPeripheral(address):
        try:
            beetle = btle.Peripheral(address,addrType=btle.ADDR_TYPE_PUBLIC,iface=0)
        except:
            print("error forming peripheral")
            return 1
        return beetle
        
    

    def scan():
        count = 0
        print("Scanning for devices...")
        scanner = btle.Scanner(0)
        devices = scanner.scan(5)
        for device in devices:
            if device.addr in address:
                count += 1
        print("Found beetles: ", count)
        return devices



class main_thread(threading.Thread):
    def __init__(self, beetle, ID):
        threading.Thread.__init__(self)
        self.beetle = beetle
        self.ID = ID
        self.serial_service = beetle.getServiceByUUID(service_uuid)
        self.serial_char = self.serial_service.getCharacteristics()[0]


    def run(self):
        global csv_time
        handshake_map[self.beetle.addr] = False
        try:
            self.beetle.setDelegate(MyDelegate(self.beetle.addr))
            #print(self.beetle.setDelegate(MyDelegate(self.beetle.addr)))
            global_delegate[self.ID] = self.beetle.setDelegate(MyDelegate(self.beetle.addr))
            #print(global_delegate[self.ID])
            self.handshake()
            if (handshake_map[self.beetle.addr]):
                csv_time = time.time()
                start_time[self.beetle.addr] = time.time()
                while True:
                    if (self.beetle.waitForNotifications(1.0) and not disconnect_map[self.beetle.addr]):
                        start_time[self.beetle.addr] = time.time()
                        continue

                    #Reset in the event of too many error packets
                    elif (disconnect_map[self.beetle.addr]):
                        print("too many error packets - reset beetle")
                        disconnect_map[self.beetle.addr] = False
                        self.beetle.disconnect()
                        self.reconnect()

                    #Handling disconnections
                    else:
                        #print(time.time(), start_time[self.beetle.addr])
                        if (time.time() - start_time[self.beetle.addr] > 15):
                            print(newline)
                            print(Disconnect_Header)
                            print("Disconnected with - Beetle ID: ", self.ID)
                            print(Disconnect_Header)
                            handshake_map[self.beetle.addr] = False
                            self.beetle.disconnect()
                            self.reconnect()

                    continue
    

            else:
                print(newline)
                print(Disconnect_Header)
                print("Error forming handshake with beetle ID: ", self.ID)
                print(Disconnect_Header)
                print(newline)
                handshake_map[self.beetle.addr] = False
                self.beetle.disconnect()
                self.reconnect()

        except btle.BTLEDisconnectError:
            print(newline)
            print(Disconnect_Header)
            print("Disconneted ERROR - Beetle ID: ", self.ID)
            print(Disconnect_Header)
            print(newline)
            handshake_map[self.beetle.addr] = False
            self.beetle.disconnect()
            self.reconnect()


    def handshake(self):
        self.serial_char.write(bytes("r", "utf-8"), withResponse = False)
        print(Connect_Header)
        print("Attempting handshake with Beetle ID ", self.ID)
        handshake_start = time.time()
        self.serial_char.write(bytes("h", "utf-8"), withResponse = False)
        print("Handshake packet sent to Beetle ID ", self.ID)
        print(Connect_Header)
        print(newline)
        

        #three-way handshake
        if self.beetle.waitForNotifications(2.0):
            handshake_end = time.time()
            #print(handshake_end - handshake_start)
            #print("Successfully made connection with beetle ID ", self.ID)
            if (handshake_map[self.beetle.addr]):
                self.serial_char.write(bytes("a", "utf-8"), withResponse = False)


    def reconnect(self):
        sleep(5)
        print(newline)
        print(Reconnect_Header)
        print("Trying reconnection wih Beetle ID: ", self.ID)
        print(Reconnect_Header)
        print(newline)
        try:
            self.beetle.connect(self.beetle.addr)
            sleep(5)
            print("Reconnection successful with Beetle ID: ", self.ID)
            print(Reconnect_Header)
            print(newline)
            self.run()

        except Exception as error:
            print(newline)
            print(Disconnect_Header)
            print("Error! Trying to reconnect with Beetle ID: ", self.ID)
            self.reconnect()



if __name__ == '__main__':
    main()
