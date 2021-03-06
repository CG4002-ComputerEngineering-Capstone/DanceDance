# DanceDance
Human Activity Recognition using wearable sensors. 

The aim of this project is to develop a gamified system that detects dance moves and relative positions of a 3-person dance group and provides real-time feedback on the performance. 
Due to the COVID-19 pandemic and the resulting restrictions, it has become increasingly difficult for groups of people to meet in person. Hence, this entire system is built to function remotely, allowing its users to dance together virtually from the comfort of their homes. 

Each dancer is equipped with a wearable device containing a Beetle BLE and an IMU sensor. The sensor data is transmitted to a remote processor (Ultra96), where it is processed using an FPGA hardware accelerator to determine the dance move being executed, 
with high accuracy and low latency. The system also detects the relative positions of dancers, and the synchronization delay between the fastest & slowest dancer, which are displayed on a dashboard along with the predicted dance move. 

On the whole, this system acts as a dance coach for its users, providing real-time feedback through an interactive dashboard. 

<img width="1031" alt="Screenshot 2021-11-17 at 3 49 33 PM" src="https://user-images.githubusercontent.com/42378151/142158019-9c5e3e12-b5ed-448e-82dc-67d0693fb9fa.png">

| Name | Role |
| --- | --- |
| Chan Hong Yi, Matthew | Hardware Sensors |
| Nishanth Elango | Hardware FPGA |
| Divakaran Haritha | Internal Communications |
| Lim Hao Xiang, Sean | External Communications|
| Priyan Rajamohan | Machine Learning |
| Lim Chek Jun | Dashboard |

The detailed report of the CG4002 Engineering Capstone Project is available [here](https://github.com/CG4002-ComputerEngineering-Capstone/DanceDance/blob/main/Report/Final%20Capstone%20Report%20-%20Group%2012.pdf)
