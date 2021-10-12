#include "Wire.h"

#define MPU_SAMPLING_RATE 20       // 20Hz
#define MYOWARE_SAMPLING_RATE 500  // 500Hz

#define HANDSHAKE 'h'
#define ACK 1
#define IMU_DATA 2
#define EMG_DATA 3

int c = 0;
const int MPU = 0x68; //  MPU6050 I2C address
float accX, accY, accZ;  
float gyroX, gyroY, gyroZ; 
float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ; 
float roll, pitch, yaw;
float accErrorX, accErrorY, gyroErrorX, gyroErrorY, gyroErrorZ;
float currentTimeGyro, previousTimeGyro, elapsedTimeGyro;

float myoware[100];
int i;
unsigned int j = 0;
int myowareSensor;
float movingAverage = 0;
int RMS, MAV, ZCR;

float currentTime, previousTimeMPU;
float previousTimeMyoware = 0;

int isDancing = 0;
float previousIdleTime = 0;

void (*reset) (void) = 0;
boolean handshake = false;
boolean confirmed = false;

struct Datapacket {
  int8_t type;
  int8_t aX;
  int8_t aY;
  int8_t aZ;
  int16_t gX;
  int16_t gY;
  int16_t gZ;
  int16_t y;
  int16_t p;
  int16_t r;
  int16_t start_move;
  int16_t checksum;
};

struct Ackpacket {
  int8_t type;
  int16_t padding_1;
  int16_t padding_2;
  int16_t padding_3;
  int16_t padding_4;
  int16_t padding_5;
  int16_t padding_6;
  int16_t padding_7;
  int16_t padding_8;
  int8_t padding_9;
  int16_t checksum;
};

struct Emgpacket {
  int8_t type;
  int16_t data_1;
  int16_t data_2;
  int16_t padding_1;
  int16_t padding_2;
  int16_t padding_3;
  int16_t padding_4;
  int16_t padding_5;
  int16_t padding_6;
  int8_t padding_7;
  int16_t checksum;
  
};

void setup() {
  Serial.begin(115200);           //  initialize serial communication
  Wire.begin();                   //  join I2C bus

  Wire.beginTransmission(MPU);    //  start communication with MPU6050
  Wire.write(0x6B);               //  talk to register 6B
  Wire.write(0);
  Wire.endTransmission(true);         

  Wire.beginTransmission(MPU);
  Wire.write(0x1C);               //  talk to register 28 (ACCEL_CONFIG)
  Wire.write(0x08);               //  set AFS_SEL to 1 (+-4g)
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU);    
  Wire.write(0x1B);               //  talk to register 27 (GYRO_CONFIG)
  Wire.write(0x00);               //  set FS_SEL to 0 (+-250deg/s)
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU);
  Wire.write(0x1A);               //  talk to register 26 (CONFIG)
  Wire.write(0x06);               //  set DLPF_CFG to 6 (5Hz digital low pass filter)
  Wire.endTransmission(true);

  calculate_MPU_error();
  delay(20);

  for(i = 0; i < 100; ++i) {
    myoware[i] = 0.0;
  }  

  previousTimeMPU = millis();
}

void loop() {
  char msg;
  if(Serial.available()){
    msg = Serial.read();
    switch(msg) {  
      case HANDSHAKE:
        sendack();
        break;

      case 'a':
        confirmed = true;
        break;

      case 'r':
        confirmed = false;
        reset();
    }
  }
  
  currentTime = millis();
  
  if((currentTime - previousTimeMyoware) > (1000 / MYOWARE_SAMPLING_RATE)) {
    myowareSensor = analogRead(A0);
    movingAverage = (0.9 * movingAverage) + (0.1 * myowareSensor);
    
    if(j > 100) {
      j = 0;
    }
    
    myoware[j] = myowareSensor - movingAverage;
    /*
    if(j == 100) {
      RMS = calculateRMS();
      MAV = calculateMAV();
      ZCR = calculateZCR();

      Serial.print("RMS: ");
      Serial.print(RMS);
      Serial.print(" MAV: ");
      Serial.print(MAV);
      Serial.print(" ZCR: ");
      Serial.println(ZCR);      
    }
    */
    previousTimeMyoware = currentTime;
    j++;
  }

  if(1) { //(currentTime - previousTimeMPU) > (1000 / MPU_SAMPLING_RATE)
    Wire.beginTransmission(MPU);
    Wire.write(0x3B); //  accelerometer data, first address 3B
    Wire.endTransmission();
    Wire.requestFrom(MPU, 6, true);
    accX = (Wire.read() << 8 | Wire.read()) / 8192.0; //  for +-4g, divide by 8192.0 according to datasheet
    accY = (Wire.read() << 8 | Wire.read()) / 8192.0;
    accZ = (Wire.read() << 8 | Wire.read()) / 8192.0;
  
    accAngleX = (atan(accY / sqrt(pow(accX, 2) + pow(accZ, 2))) * 180 / PI) - accErrorX; 
    accAngleY = (atan(-1 * accX / sqrt(pow(accY, 2) + pow(accZ, 2))) * 180 / PI) - accErrorY; 
  
    previousTimeGyro = currentTimeGyro;                             //  previous time is stored before reading current time
    currentTimeGyro = millis();                                     //  read current time
    elapsedTimeGyro  = (currentTimeGyro - previousTimeGyro) / 1000; //  elapsed time in seconds
  
    Wire.beginTransmission(MPU);
    Wire.write(0x43); // gyro data, first address 0x43
    Wire.endTransmission();
    Wire.requestFrom(MPU, 6, true);
    gyroX = (Wire.read() << 8 | Wire.read()) / 131.0;   //  for 250deg/s, divide by 131.0 according to datasheet
    gyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
    gyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
  
    gyroX = gyroX - gyroErrorX;
    gyroY = gyroY - gyroErrorY;
    gyroZ = gyroZ - gyroErrorZ;
  
    gyroAngleX = gyroX * elapsedTimeGyro;                   //  deg is calculated by multiplying deg/s by s
    gyroAngleY = gyroY * elapsedTimeGyro;
    yaw = yaw + (gyroZ * elapsedTimeGyro);
  
    roll = 0.96 * gyroAngleX + 0.04 * accAngleX;        //  complimentary filter, accelerometer and gyro angle values are combined to remove noise
    pitch = 0.96 * gyroAngleY + 0.04 * accAngleY;

    if((accX > 0.30 || accX < -0.30) && (accY > 1.10 || accY < 0.90)) {   //  detection of start of dance move
     isDancing = 1;
    } else {
     if(currentTime > previousIdleTime + 2000) {      // go back into idle state if no movement for 2s
       isDancing = 0;
       previousIdleTime = currentTime;
     }
    }
    
    if(confirmed){
      sendData();
    }             
    
    /*
    if(isDancing == 1) {
      Serial.print(accX);
      Serial.print(", ");
      Serial.print(accY);
      Serial.print(", ");
      Serial.print(accZ);
      Serial.print(", ");
      Serial.print(gyroX);
      Serial.print(", ");
      Serial.print(gyroY);
      Serial.print(", ");    
      Serial.print(gyroZ);
      Serial.print(", "); 
      Serial.print(pitch);
      Serial.print(", ");  
      Serial.print(roll);
      Serial.print(", ");     
      Serial.println(yaw);   
    }
    */
    
  }
}

void calculate_MPU_error() {        //  Place IMU flat to calculate accelerometer and gyro data error
  while (c < 200) {                 //  Read accelerometer values 200 times
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false); 
    Wire.requestFrom(MPU, 6, true);
    accX = (Wire.read() << 8 | Wire.read()) / 8192.0 ;
    accY = (Wire.read() << 8 | Wire.read()) / 8192.0 ;
    accZ = (Wire.read() << 8 | Wire.read()) / 8192.0 ;
    // Sum all readings
    accErrorX = accErrorX + ((atan((accY) / sqrt(pow((accX), 2) + pow((accZ), 2))) * 180 / PI));
    accErrorY = accErrorY + ((atan(-1 * (accX) / sqrt(pow((accY), 2) + pow((accZ), 2))) * 180 / PI));
    c++;
  }
  
  accErrorX = accErrorX / 200;     //  Divide the sum by 200 to get the error value
  accErrorY = accErrorY / 200;
  c = 0;

  while (c < 200) {                // Read gyro values 200 times
    Wire.beginTransmission(MPU);
    Wire.write(0x43);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    gyroX = Wire.read() << 8 | Wire.read();
    gyroY = Wire.read() << 8 | Wire.read();
    gyroZ = Wire.read() << 8 | Wire.read();
    // Sum all readings
    gyroErrorX = gyroErrorX + (gyroX / 131.0);
    gyroErrorY = gyroErrorY + (gyroY / 131.0);
    gyroErrorZ = gyroErrorZ + (gyroZ / 131.0);
    c++;
  }
  gyroErrorX = gyroErrorX / 200;  //  Divide the sum by 200 to get the error value
  gyroErrorY = gyroErrorY / 200;
  gyroErrorZ = gyroErrorZ / 200;

  /*
  Serial.print("accErrorX: ");
  Serial.println(accErrorX);
  Serial.print("accErrorY: ");
  Serial.println(accErrorY);
  Serial.print("gyroErrorX: ");
  Serial.println(gyroErrorX);
  Serial.print("gyroErrorY: ");
  Serial.println(gyroErrorY);
  Serial.print("gyroErrorZ: ");
  Serial.println(gyroErrorZ);
  */
}

int calculateRMS() {
  float sum = 0;
  for(i = 0; i < 100; ++i) {
    sum += pow(myoware[i], 2);
  }
  float result = pow((sum / 100), 0.5) * 100;
  return result;
}

int calculateMAV() {
  float sum = 0;
  for(i = 0; i < 100; ++i) {
    sum += abs(myoware[i]);
  }
  float result = sum;
  return result;
}

int calculateZCR() {
  float crossing = 0;
  bool isPositivePrevious = false;
  bool isPositiveNext;
  for(i = 1; i < 100; ++i) {
    isPositiveNext = myoware[i] > 0;
    if(isPositiveNext != isPositivePrevious) {
      crossing++;
    }
    isPositivePrevious = isPositiveNext;
  }
  float result = crossing;
  return result;
}

void sendData(){
  Datapacket packet;
  packet.type = IMU_DATA;
  packet.aX = int8_t(accX * 100); 
  packet.aY = int8_t(accY * 100);
  packet.aZ = int8_t(accZ * 100);
  packet.gX = int16_t(gyroX * 100);
  packet.gY = int16_t(gyroY * 100);
  packet.gZ = int16_t(gyroZ * 100);
  packet.y = int16_t(yaw * 100);
  packet.p = int16_t(pitch * 100);
  packet.r = int16_t(roll * 100);
  packet.start_move = int16_t(isDancing);
  packet.checksum = getChecksum(packet);
  Serial.write((uint8_t *)&packet, sizeof(packet));
  delay(50);
}

void sendack() {
  Ackpacket packet;
  packet.type = ACK;
  packet.padding_1 = 0;
  packet.padding_2 = 0;
  packet.padding_3 = 0;
  packet.padding_4 = 0;
  packet.padding_5 = 0;
  packet.padding_6 = 0;
  packet.padding_7 = 0;
  packet.padding_8 = 0;
  packet.padding_9 = 0;
  packet.checksum = getAckChecksum(packet);
  Serial.write((uint8_t *)&packet, sizeof(packet));
  delay(100);
}

void sendemg() {
  Emgpacket packet;
  packet.type = EMG_DATA;
  packet.data_1 = 5000;
  packet.data_2 = 7000;
  packet.padding_1 = 0;
  packet.padding_2 = 0;
  packet.padding_3 = 0;
  packet.padding_4 = 0;
  packet.padding_5 = 0;
  packet.padding_6 = 0;
  packet.padding_7 = 0;
  packet.checksum = getEmgChecksum(packet);
  Serial.write((uint8_t *)&packet, sizeof(packet));
  delay(10);
  
}

long getChecksum(Datapacket packet){
  return packet.type ^ packet.aX ^ packet.aY ^ packet.aZ ^ packet.gX ^ packet.gY ^ packet.gZ ^ packet.y ^ packet.p ^ packet.r ^ packet.start_move;
}

long getAckChecksum(Ackpacket packet){
  return packet.type ^ packet.padding_1 ^ packet.padding_2 ^ packet.padding_3 ^ packet.padding_4 ^ packet.padding_5 ^ packet.padding_6 ^ packet.padding_7 ^ packet.padding_8 ^ packet.padding_9;
}

long getEmgChecksum(Emgpacket packet){
  return packet.type ^ packet.data_1 ^ packet.data_2 ^ packet.padding_1 ^ packet.padding_2 ^ packet.padding_3 ^ packet.padding_4 ^ packet.padding_5 ^ packet.padding_6 ^ packet.padding_7;
}
