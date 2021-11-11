import json
import requests


# POST_SYNC_DELAY_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostSyncDelay"
# POST_POSITION_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostPosition" # replace dancerId param when using
# POST_MOVE_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostMove" # replace dancerId param when using
POST_SENSOR_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostSensor"
POST_EMG_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostEMG"


headers = { 'Content-Type': 'application/json' }

def send_sensor(dancerId, sensorData) :
    try:
        accelData = []
        gyroData = []
        for sample in sensorData:
          if len(sample) == 6:
            accelData.append({
                "x": sample[1],
                "y": sample[2],
                "z": sample[3],
            })
            gyroData.append({
                "x": sample[4],
                "y": sample[5],
            })
          else:
            accelData.append({
                "x": sample[0],
                "y": sample[1],
                "z": sample[2],
            })
            gyroData.append({
                "x": sample[3],
                "y": sample[4],
            })
        requests.post(POST_SENSOR_API_ENDPOINT + f'?dancerId={dancerId}', json.dumps({"accelerometer": accelData, "gyroscope": gyroData}), headers)
        print(f"\nSent Sensor {dancerId} Data\n")
    except Exception as e: 
      print(f"\nFailed to send Sensor {dancerId} Data\n")
      print(e)

def send_emg(emg) :
    try:
        data = {'emg': emg}
        requests.post(POST_EMG_API_ENDPOINT, json.dumps(data), headers)
        print("Sent EMG")
    except Exception as e:
      print("Failed to send EMG Data")
      print(e)

