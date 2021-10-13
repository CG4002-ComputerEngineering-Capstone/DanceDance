import threading
from concurrent.futures import ThreadPoolExecutor
import time
import pickle
import numpy as np


from config import NUM_DANCERS, PREDICTION_LIST_SIZE
from dashboard import send_move
from predictor import Predictor
# from skorch_trainer import getPrediction


class EnsembleModel:
    def __init__(self, file_location):
        # Loads the pre-saved model
        self.model = pickle.load(open(file_location, 'rb'))
        self.DANCE_TO_NUM_MAP = {0: 'dab', 1: 'jamesbond', 2: 'mermaid'}


    def predict(self, arr):
        out = self.model.predict(arr)
        return self.DANCE_TO_NUM_MAP[out[0]]

class MlHandler(threading.Thread):
    def __init__(self, dataQueues, prediction, readyForEval, predictionLock):
        threading.Thread.__init__(self)
        self.predictor = Predictor()
        # self.ml_model = EnsembleModel('ensemble.pkl')
        self.predictorLock = threading.Lock()
        self.dataQueues = dataQueues
        self.prediction = prediction
        self.readyForEval = readyForEval
        self.predictionLock = predictionLock
        
    
    def reset_prediction_list(self):
        return {'dab': 0, 'jamesbond': 0, 'mermaid': 0}

    def indiv_predictor(self, dancerId, dataQueue, predictionLock):
        prediction_list = {'dab': 0, 'jamesbond': 0, 'mermaid': 0}
        while 1:
            print(f'predictor {dancerId} waiting.....')
            vector = dataQueue.get()
            print('==========================================================')
            print(type(vector))
            # print(vector)
            print(f'ml_handler {dancerId} received vector')
            print('==========================================================')

            # pass preprocessed data into predictor (using predictorLock to prevent conflicts)
            try:
                self.predictorLock.acquire()
                label = self.predictor.predict(vector)
                # label = self.ml_model.predict(np.asarray(vector).reshape(-1,480))
                self.predictorLock.release()
                print(f'Predicted label: {label}')
                # label = 'dab'
                prediction_list[label] += 1
            except Exception as e:
                print('ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                print('predict failed')
                print(e)
                print('ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
            

            if sum(prediction_list.values()) != PREDICTION_LIST_SIZE:
                print(f'have not reached {PREDICTION_LIST_SIZE} predictions')
                continue
            else:
                print(f'finished {PREDICTION_LIST_SIZE} predictions')
                try:
                    label = max(prediction_list, key = prediction_list.get) 
                    print(f'predictions: {prediction_list}')
                    print(f'final label: {label}')
                except Exception as e:
                    print('ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                    print(e)
                    print('ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                    # sys.exit()
                prediction_list = self.reset_prediction_list()

            print('acquiring predictionLock')
            self.predictionLock.acquire()
            print('Acquired predictionLock!')
            # pass label to prediction object
            # print(self.prediction)
            # print(self.prediction['dance_move'])
            # print(self.prediction['dance_move'][dancerId])
            
            # REMOVE LATER
            # send predicted dance move of this dancer to dashboard
            print(f'sending dance move "{label}" to dashboard')
            send_move(dancerId, label)
            self.prediction['dance_move'][dancerId] = label
            self.readyForEval.set()
            predictionLock.release()
            # REMOVE LATER

            # if self.prediction['dance_move'][dancerId] is None or self.prediction['dance_move'][dancerId] != label:
            #     self.prediction['dance_move'][dancerId] = label
            #     # send predicted dance move of this dancer to dashboard
            #     print(f'sending dance move "{label}" to dashboard')
            #     send_move(dancerId, label)

            # # if all dancers have danced and system successfully got a prediction
            # if all(x is not None for x in self.prediction['dance_move'].values()):
            #     self.readyForEval.set()
            #     # TODO remove below when running eval client
            #     self.prediction['dance_move'][dancerId] = None
            

    def run(self):
        print('mlhandler start')
        with ThreadPoolExecutor() as executor:
            for i in range(NUM_DANCERS):
                executor.submit(self.indiv_predictor, i+1, self.dataQueues[i], self.predictionLock)
