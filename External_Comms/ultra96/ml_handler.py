import threading
from concurrent.futures import ThreadPoolExecutor
import time
import pickle

from requests import NullHandler
import queue

from config import DELAY_AFTER_SUBMISSION, NUM_DANCERS, PREDICTION_LIST_SIZES
from dashboard import send_move, send_alert
from predictor import Predictor

class MlHandler(threading.Thread):
    def __init__(self, dataQueues, prediction, readyForEval, predictionLock, clockSyncFlags, clearDataQueueFlags, submittedToEval, dancerIsConnected, hasRecvPositionalChange, shutdown, predictionListPtr, predictionListPtrLock):
        threading.Thread.__init__(self)
        self.predictor = Predictor()
        self.predictorLock = threading.Lock()
        self.dataQueues = dataQueues
        self.prediction = prediction
        self.readyForEval = readyForEval
        self.predictionLock = predictionLock
        self.clockSyncFlags = clockSyncFlags
        self.NUM_TO_DANCE_MAP = {0: 'dab', 1: 'jamesbond', 2: 'mermaid', 
                                3: 'scarecrow', 4:'pushback',  5: 'cowboy', 
                                6: 'window360', 7: 'snake', 8: 'logout'}
        self.clearDataQueueFlags = clearDataQueueFlags
        self.submittedToEval = submittedToEval
        self.dancerIsConnected = dancerIsConnected
        self.hasRecvPositionalChange = hasRecvPositionalChange
        self.shutdown = shutdown
        self.predictionListPtr = predictionListPtr
        self.predictionListPtrLock = predictionListPtrLock

    def get_avg_dance_move(self, dance_moves):
        freq = {}
        for dance_move in dance_moves.values():
            if dance_move in freq.keys():
                freq[dance_move] += 1
                
            else:
                freq[dance_move] = 1
        return max(freq, key=freq.get)
        
    
    def reset_prediction_list(self):
        return {'dab': 0, 'jamesbond': 0, 'mermaid': 0,
                'scarecrow': 0, 'pushback': 0, 'cowboy': 0,
                'window360': 0, 'snake': 0, 'logout': 0}

    def indiv_predictor(self, dancerId, dataQueue, clockSyncFlag, clearDataQueueFlag):
        prediction_list = {'dab': 0, 'jamesbond': 0, 'mermaid': 0,
                        'scarecrow': 0, 'pushback': 0, 'cowboy': 0,
                        'window360': 0, 'snake': 0, 'logout': 0}
        hasRecvStartOfDanceMove = False
        print(f'[{dancerId}] predictor {dancerId} waiting.....')
        
        while not self.shutdown.is_set():
            if not self.dancerIsConnected:
                prediction_list = self.reset_prediction_list()
                self.prediction['dance_moves_list'][dancerId] = []
            try:
                vector = dataQueue.get(timeout=2.0)
            except queue.Empty:
                continue
            
            # print(f'[{dancerId}] ml_handler {dancerId} received vector')

            # if packet is start of dance move:
            if len(vector) == 1: # start of dance move timestamp
                timestamp = vector[0]
                if not hasRecvStartOfDanceMove:
                    self.predictionLock.acquire()
                    self.prediction['start_timestamps'][dancerId] = timestamp
                    self.predictionLock.release()
                    hasRecvStartOfDanceMove = True
                    prediction_list = self.reset_prediction_list()
                    self.prediction['dance_moves_list'][dancerId] = []
                continue
            

            # pass preprocessed data into predictor (using predictorLock to prevent conflicts)
            try:
                self.predictorLock.acquire()
                label = self.predictor.predict(vector)
                self.predictorLock.release()
                
                print(f'[{dancerId}] Predicted label: {label}')
                
                if label == 'idle':
                    print('Prediction was inconclusive, waiting for more data to try again')
                    continue

                prediction_list[label] += 1
                self.prediction['dance_moves_list'][dancerId].append(label)
                
            except Exception as e:
                print(f'[{dancerId}] ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                print(f'[{dancerId}] predict failed')
                print(e)
                print(f'[{dancerId}] ERROR ERROR ERROR ERROR ERROR ERROR ERROR')

            
            # if have not made 3 predictions for current move, continue to wait for more data
            self.predictionListPtrLock.acquire()
            curr_prediction_list_size = PREDICTION_LIST_SIZES[self.predictionListPtr[0]]
            self.predictionListPtrLock.release()
            if sum(prediction_list.values()) < curr_prediction_list_size:
                continue
            else:
                # when gathered enough predictions for submission, ignore incoming packets until submitted to eval server
                clearDataQueueFlag.set()

                print(f'[{dancerId}] finished {sum(prediction_list.values())} predictions')
                try:
                    label = max(prediction_list, key = prediction_list.get) 
                    print(f'[{dancerId}] predictions: {prediction_list}')
                    print(f'[{dancerId}] final label: {label}')
                except Exception as e:
                    print(f'[{dancerId}] ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                    print(e)
                    print(f'[{dancerId}] ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                    # sys.exit()

            self.predictionLock.acquire()            
            
            # add predicted dance move to prediction object and send to dashboard
            if self.prediction['dance_move'][dancerId] is None:
                print(f'[{dancerId}] sending dance move "{label}" to dashboard')
                send_move(dancerId, label)
                self.prediction['dance_move'][dancerId] = label

            self.predictionLock.release()

            
            while not self.readyForEval.is_set():
                self.predictionLock.acquire()   
                # check which dancers are still connected
                connectedDancers = [idx + 1 for idx, isConnected in enumerate(self.dancerIsConnected) if isConnected]
                print(f'[{dancerId}] Connected dancers: {connectedDancers}')
                # get dance_move prediction of connected dancers
                connectedDancersPredictions = [self.prediction['dance_move'][dancer] for dancer in connectedDancers]
                
                # if all connected dancers have a prediction already, ready to send to eval server
                if all(x is not None for x in connectedDancersPredictions):
                    self.readyForEval.set()
                    print(f'[{dancerId}] Ready for eval!')

                self.predictionLock.release()
                
                # Wait for eval client to finish sending to eval server
                print(f'[{dancerId}] waiting for submission to eval server to complete')

                # if submittedToEval flag does not get set in 2 seconds, check connectedDancers again
                res = self.submittedToEval.wait(timeout=1.0) # returns True if submittedToEval event has been set in eval_client
                if res: break


            print(f'[{dancerId}] Submitted to eval server, preparing for next dance move')

            # sleep for 2 seconds to allow clearing of data queue
            print(f'[{dancerId}] clearing dataqueue...')

            # After submission, run clock sync if haven't logout
            if not self.shutdown.is_set():
                clockSyncFlag.set()

            # delay for clearing of data queue and receiving positional change packets
            time.sleep(DELAY_AFTER_SUBMISSION)

            hasRecvStartOfDanceMove = False
            self.hasRecvPositionalChange[dancerId-1] = False
            prediction_list = self.reset_prediction_list()
            # ready for next eval, can start receiving new packets
            clearDataQueueFlag.clear()
            
            if dancerId == 1:
                self.submittedToEval.clear()
                send_alert(f'Start dancing now!')
            send_move(dancerId, '-')
            print(f'[{dancerId}] dataqueue cleared, prepare to receive sensor packets...')


    def run(self):
        print('mlhandler start')
        with ThreadPoolExecutor() as executor:
            for i in range(NUM_DANCERS):
                executor.submit(self.indiv_predictor, i+1, self.dataQueues[i], self.clockSyncFlags[i], self.clearDataQueueFlags[i])
