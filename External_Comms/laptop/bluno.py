from bluepy import btle
from time import time, sleep
from datetime import datetime
import threading
import struct
import time
import csv
import globals_
from dashboard import send_emg

service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"

BEETLE_4 = "b0:b1:13:2d:b4:19"
#BEETLE_5 = "b0:b1:13:2d:b5:13"
#BEETLE_6 = "b0:b1:13:2d:d4:86"

#>>>>> SETUP BLUNO MAC ADDRESS >>>>>>>>
address = [BEETLE_4]

Connect_Header = "++++++++++++++++++++++++++++++++++++++++++++++++++++"
Disconnect_Header = "----------------------------------------------------"
Data_Header = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
Reconnect_Header = "####################################################"
newline = "\n"

 
csv_time = 0
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
    
def checksum_ack(packet):
    check = packet[0] ^ packet[1] ^ packet[2] ^ packet[3] ^ packet[4] ^ packet[5] ^ packet[6] ^ packet[7] ^ packet[8] ^ packet[9]
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

def checksum_direction(packet):
    check = packet[0] ^ packet[1] ^ packet[2] ^ packet[3] ^ packet[4] ^ packet[5] ^ packet[6] ^ packet[7] ^ packet[8] ^ packet[9] ^ packet[10]
    if check == packet[11]:
        return True
    return False


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        self.address = params
        self.inDancingState = False
        # self.immediatePrevDancingState = False # dancing state right before timer event happen
        self.timer = None
        self.consecutiveIdlePacketsCount = 0
        self.consecutiveIdlePacketsThreshold = globals_.CONSECUTIVE_IDLE_PACKETS_THRESHOLD
        self.numActiveAfterPosChange = 0
        self.numPacketsAfterPosChange = 0
        self.assessingPositionalChange = False
        self.positionalChange = []

    def exitDancingState(self):
        print('********************************************************************')
        print(f'End of dancing state')
        print('********************************************************************')
        self.inDancingState = False

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
                        if(checksum_imu(packet)):
                            try:
                                print(f'isDancingState: {self.inDancingState}')

                                # check if 10 consecutive packets after receiving positional change are idle
                                if self.assessingPositionalChange:
                                    print(f'dancingState: {packet[7]}')
                                    self.numPacketsAfterPosChange += 1
                                    if packet[7] == 1:
                                        self.numActiveAfterPosChange += 1
                                    print(f'Num active packets after positional change: {self.numActiveAfterPosChange}')

                                    if self.numPacketsAfterPosChange == globals_.NUM_CONSECUTIVE_PACKETS_THRESHOLD:
                                        if self.numActiveAfterPosChange < globals_.NUM_ACTIVE_PACKETS_THRESHOLD:
                                            print(f'Positional change confirmed - adding "{self.positionalChange}" to queue now')
                                            globals_.dataQueue.put(self.positionalChange)
                                        else:
                                            print(f'Positional change REJECTED - {self.positionalChange}')
                                        self.numActiveAfterPosChange = 0
                                        self.numPacketsAfterPosChange = 0
                                        self.assessingPositionalChange = False


                                elif self.inDancingState == False:
                                    if packet[7] == 1:
                                        timestamp = time.time()
                                        self.inDancingState = True
                                        # self.timer = threading.Timer(4.2, self.exitDancingState)
                                        # self.timer.start()
                                        # if not self.immediatePrevDancingState == True:
                                            # means after 2 seconds the dancer is still dancing
                                        print('********************************************************************')
                                        print(f'Start of dance move')
                                        print('********************************************************************')
                                        packet_list = list(packet)
                                        sensor_values = packet_list[1:4] + packet_list[5:7]
                                        globals_.dataQueue.put([timestamp] + sensor_values)
                                        self.consecutiveIdlePacketsCount = 0
                                    
                                elif self.inDancingState == True:
                                    # add packet to queue to be sent to server
                                    if packet[7] == 0:
                                        self.consecutiveIdlePacketsCount += 1
                                        # if 10 consecutive idle packets has been received, set dancing state to false
                                        if self.consecutiveIdlePacketsCount >= self.consecutiveIdlePacketsThreshold:
                                            self.inDancingState = False
                                            self.consecutiveIdlePacketsCount = 0

                                        # else, continue to add packets to queue
                                        else: 
                                            packet_list = list(packet)
                                            sensor_values = packet_list[1:4] + packet_list[5:7]
                                            globals_.dataQueue.put(sensor_values)
                                    else:
                                        self.consecutiveIdlePacketsCount = 0
                                        packet_list = list(packet)
                                        sensor_values = packet_list[1:4] + packet_list[5:7]
                                        globals_.dataQueue.put(sensor_values)
                                    # print(f'added sensor values to queue {sensor_values}')
                                    # time.sleep(0.1)
                            except Exception as e:
                                print("ERROR ERROR ERROR ERROR ERROR ERROR ERROR")
                                print(e)
                                print("ERROR ERROR ERROR ERROR ERROR ERROR ERROR")
                            

                        elif(not checksum_imu(packet)):
                            print("WRONG CHECKSUM")
                                            

                    elif packet_type == 3 and handshake_map[addr] == True:
                        packet = struct.unpack("<bhhhhhhhhbh", packet)
                        print(Data_Header)
                        print("Receiving EMG data from beetle ID: ", i)
                        if(checksum_emg(packet)):
                            send_emg(packet[1:4])

                    elif packet_type == 4 and handshake_map[addr] == True:
                        packet = struct.unpack("<bbbhhhhhhhbh", packet)
                        print(Data_Header)
                        print("Receiving DIR data from beetle ID: ", i)
                        if(checksum_direction(packet)):
                            print("Checksum correct for DIR !")
                            # TODO send position change to dashboard and ultra96
                            # globals_.dataQueue.put([packet[1]])
                            self.numActiveAfterPosChange = 0
                            self.assessingPositionalChange = True
                            self.positionalChange = [packet[1]]
                            print('Assessing positional change now....')



class Setup:
    def setPeripheral(address):
        try:
            beetle = btle.Peripheral(address,addrType=btle.ADDR_TYPE_PUBLIC,iface=0)
        except:
            print("error forming peripheral")
            return 1
        return beetle
        

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
        sleep(1)
        print(Connect_Header)
        print("Attempting handshake with Beetle ID ", self.ID)
        self.serial_char.write(bytes("h", "utf-8"), withResponse = False)
        print("Handshake packet sent to Beetle ID ", self.ID)
        print(Connect_Header)
        print(newline)
        
        #three-way handshake
        if self.beetle.waitForNotifications(2.0):
            if (handshake_map[self.beetle.addr]):
                self.serial_char.write(bytes("a", "utf-8"), withResponse = False)

    def reconnect(self):
        sleep(1)
        print(newline)
        print(Reconnect_Header)
        print("Trying reconnection wih Beetle ID: ", self.ID)
        print(Reconnect_Header)
        print(newline)
        try:
            self.beetle.connect(self.beetle.addr)
            sleep(1)
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
