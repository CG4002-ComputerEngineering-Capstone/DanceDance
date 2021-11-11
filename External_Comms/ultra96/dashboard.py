import json
import requests


POST_SYNC_DELAY_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostSyncDelay"
POST_POSITION_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostPosition" # replace dancerId param when using
POST_MOVE_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostMove" # replace dancerId param when using
# POST_SENSOR_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostSensor"
# POST_EMG_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostEMG"
POST_FLAG_API_ENDPOINT = "https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/PostFlag"


headers = { 'Content-Type': 'application/json' }


def send_move(dancerId, move):
  try:
      data = {'move': move}
      requests.post(POST_MOVE_API_ENDPOINT + f'?dancerId={dancerId}', json.dumps(data), headers)

      print(f"Sent Dance move for dancer {dancerId}")
  except Exception as e: 
      print("lmao fail send_move")
      print(e)


def send_position(position):
  try:
      data = {'position': list(map(int, position.split(' ')))}
      requests.post(POST_POSITION_API_ENDPOINT, json.dumps(data), headers)

      print(f"Sent positions to dashboard")
  except Exception as e: 
      print("lmao fail send_position")
      print(e)


def send_syncdelay(syncDelay):
  try:
      # syncDelay in milliseconds
      data = {'syncDelay': syncDelay}
      requests.post(POST_SYNC_DELAY_API_ENDPOINT, json.dumps(data), headers)

      print(f"Sent syncdelay")
  except Exception as e: 
      print("lmao fail send_syncdelay")
      print(e)
    
def send_alert(alert):
  try:
    data = {'flag': alert}
    requests.post(POST_FLAG_API_ENDPOINT, json.dumps(data), headers)
    print(f'Sent alert to dashboard! : {alert}')
  except Exception as e:
    print('fail send_alert')
    print(e)

