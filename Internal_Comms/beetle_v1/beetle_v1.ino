#define HANDSHAKE 'h'
#define ACK 1
#define IMU_DATA 2
#define EMG_DATA 3


void (*reset) (void) = 0;
unsigned long start_time = 0;
boolean handshake = false;
boolean confirmed = false;
int16_t aX, aY, aZ;
int16_t gX, gY, gZ;
//int16_t yaw, pitch, roll;


//dummy data
float accX[] = {-1.99};
float accY[] = {-0.56};
float accZ[] = {0.4};
float gyrX[] = {100.0};
float gyrY[] = {-150.0};
float yaw[] = {340.5};
float pitch[] = {200.6};
float roll[] = {134.7};

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
    Serial.begin(115200);               //initial the Serial
}
 
void loop(){
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

   if (confirmed){
    senddata();
    //sendemg();
  }
}

//comment out and debug
void senddata(){
  Datapacket packet;
  packet.type = IMU_DATA;
  packet.aX = int8_t(accX[0]); 
  packet.aY = int8_t(accX[0]);
  packet.aZ = int8_t(accX[0]);
  packet.gX = int16_t(gyrX[0]);
  packet.gY = int16_t(gyrX[0]);
  packet.gZ = int16_t(gyrX[0]);
  packet.y = 6;
  packet.p = 6;
  packet.r = 6;
  packet.start_move = 0;
  packet.checksum = getChecksum(packet);
  Serial.write((uint8_t *)&packet, sizeof(packet));

  delay(48);
  //delay(45);
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
  delay(1000);
  
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
