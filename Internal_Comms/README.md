# Internal Communications # 

### Final working versions for the project ###

1. beetle_basic.ino is the initial code version in the earlier stages of the project. Final working version after integration with hardware is under Hardware > beetle_v5 > beetle_v5.ino
2. laptop_v2.py is used for data collection and is purely internal comms code. Final working version after integration with external comms are under External_Comms > laptop > bluno.py, main.py


### For data collection ####

1. Make sure you are in the correct directory `cd Internal_Comms`
2. Type `bluetoothctl` first
3. Type `scan on` to find out your bluno's mac address
4. Type `exit` to exit bluetoothctl mode
5. In laptop_v2.py file, edit **line 17** to include your bluno's mac address and **line 18** to rename your file in the correct format. You might have to comment/uncomment out other mac addresses above line 17
6. Run the file by typing `python3 laptop_v2.py` into the terminal
7. Once you see *"Successfully received ACK packet from Beetle ID: 0"*, **start** dancing 
8. **Stop** dancing when you see *"Reached CSV"* with the time taken to collect readings
9. `ls` to check if the csv file has been added correctly


### Debug bluetooth issues ###

1. If your beetle does not connect within 30 seconds, there are probably some issues with your bluetooth
2. Type `bluetoothctl` first
3. Type `scan on` to find out your beetle's mac address
4. Type `exit`to exit bluetoothctl mode
5. If you are unable to see any devices under scan, it is probably a bluetooth issue
6. Type `hciconfig`
7. Ideally, under hci0, it should show "UP RUNNING PSCAN ISCAN"
8. If it is "DOWN", try `sudo hciconfig hci0 up`
9. Now, typing `hciconfig` should show "UP RUNNING"
10. If it is just "UP RUNNING", try `sudo hciconfig hci0 piscan`
11. Now, typing `hciconfig` should show "UP RUNNING PSCAN ISCAN"
12. Try steps 2-4 to see if your beetle's mac address appears, if it does, bluetooth is fixed
13. Run code again to see if beetle connects within 30 seconds
14. If it still does not connect, try uploading the arduino code again
