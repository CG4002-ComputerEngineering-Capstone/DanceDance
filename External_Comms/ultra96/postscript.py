import json
import random
import requests
import threading
import time

class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()

POST_PREDICTION_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostPrediction"
POST_SENSOR_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostSensor"
POST_EMG_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostEMG"

mockPredictions = [
  {
    "position": [1, 2, 3],
    "move": ["cowboy", "cowboy", "cowboy"],
    "syncDelay": 100
  },
  {
    "position": [3, 1, 2],
    "move": ["dab", "dab", "dab"],
    "syncDelay": 200
  },
  {
    "position": [2, 3, 1],
    "move": ["jamesbond", "jamesbond", "jamesbond"],
    "syncDelay": 300
  },
  {
    "position": [1, 2, 3],
    "move": ["mermaid", "mermaid", "mermaid"],
    "syncDelay": 400
  },
  {
    "position": [3, 1, 2],
    "move": ["pushback", "pushback", "pushback"],
    "syncDelay": 400
  },
  {
    "position": [2, 3, 1],
    "move": ["scarecrow", "scarecrow", "scarecrow"],
    "syncDelay": 300
  },
  {
    "position": [1, 2, 3],
    "move": ["snake", "snake", "snake"],
    "syncDelay": 200
  },
  {
    "position": [3, 1, 2],
    "move": ["window360", "window360", "window360"],
    "syncDelay": 100
  }
]

def mock_data() :
    arr = []
    for _ in range(20) :
        arr.append(
            {
                "x": random.randint(-20000, 20000),
                "y": random.randint(-20000, 20000),
                "z": random.randint(-20000, 20000)
            }
        )
    return arr

headers = { 'Content-Type': 'application/json' }

predictionCount = 0
def send_prediction() :
  global predictionCount
  if predictionCount == len(mockPredictions) :
      predictionCount = 0
  try:
      requests.post(POST_PREDICTION_API_ENDPOINT, json.dumps(mockPredictions[predictionCount]), headers)
      predictionCount += 1
      print("Sent Prediction")
  except: 
      print("lmao fail send")
    
def send_sensor() :
    try:
        requests.post(POST_SENSOR_API_ENDPOINT + '?collectionName=Sensor1', json.dumps({"accelerometer": mock_data(), "gyroscope": mock_data()}), headers)
        print("Sent Sensor 1 Data")
    except: 
        print("Failed to send Sensor 1 Data")
    try:
        requests.post(POST_SENSOR_API_ENDPOINT + '?collectionName=Sensor2', json.dumps({"accelerometer": mock_data(), "gyroscope": mock_data()}), headers)
        print("Sent Sensor 2 Data")
    except: 
        print("Failed to send Sensor 2 Data")
    try:
        requests.post(POST_SENSOR_API_ENDPOINT + '?collectionName=Sensor3', json.dumps({"accelerometer": mock_data(), "gyroscope": mock_data()}), headers)
        print("Sent Sensor 3 Data")
    except: 
        print("Failed to send Sensor 3 Data")

def send_emg() :
    try:
        requests.post(POST_EMG_API_ENDPOINT, json.dumps({"emg": random.randint(0, 500)}), headers)
        print("Sent EMG")
    except:
        print("Failed to send EMG Data")

# predictionInterval=setInterval(10, send_prediction)
# sensorInterval=setInterval(1, send_sensor)
# emgInterval=setInterval(1, send_emg)