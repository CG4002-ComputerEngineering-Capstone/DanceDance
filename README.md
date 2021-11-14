# DanceDance
Human Activity Recognition using wearable sensors. 

The aim of this project is to develop a gamified system that detects dance moves and relative positions of a 3-person dance group and provides real-time feedback on the performance. 
Due to the COVID-19 pandemic and the resulting restrictions, it has become increasingly difficult for groups of people to meet in person. Hence, this entire system is built to function remotely, allowing its users to dance together virtually from the comfort of their homes. 

Each dancer is equipped with a pair of wearable devices containing a Beetle BLE and an IMU sensor. The sensor data is transmitted to a remote processor (Ultra96), which processes the sensor data using an FPGA hardware accelerator to determine the dance move being executed, 
with high accuracy and low latency. The system also detects the relative position of the dancers, and the synchronization delay between the fastest and slowest dancer, which are displayed on a dashboard together with the predicted dance move. 
Overall, this system acts as a dance coach for its users, providing real-time feedback through an interactive dashboard. 


