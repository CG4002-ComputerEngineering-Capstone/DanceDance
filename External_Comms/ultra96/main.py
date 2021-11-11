import threading
from queue import Queue
import sys

from ultra96_server import Ultra96Server
from eval_client import EvalClient
from ml_handler import MlHandler
from config import IS_EVAL, SERVER_HOST, SERVER_PORT, EVAL_HOST, EVAL_PORT, NUM_DANCERS


class MainThread():
    def __init__(self):
        self.prediction = {
            'curr_position': '1 2 3',
            'position_shift': {key: 'N' for key in range(1, NUM_DANCERS+1)}, # starting position is 1 2 3
            'new_position': None,
            'dance_move': {key: None for key in range(1, NUM_DANCERS+1)},
            'dance_moves_list': {key: [] for key in range(1, NUM_DANCERS+1)},
            'start_timestamps': {key: None for key in range(1, NUM_DANCERS+1)}
        }
        self.predictionListPtr = [-1]
        self.predictionListPtrLock = threading.Lock()
        self.dataQueues = [Queue() for x in range(NUM_DANCERS)]
        self.dancerIsConnected = [False for key in range(1, NUM_DANCERS+1)]
        self.readyForEval = threading.Event()
        self.submittedToEval = threading.Event()
        self.clockSyncFlags = [threading.Event() for x in range(NUM_DANCERS)]
        self.predictionLock = threading.Lock()
        self.clearDataQueueFlags = [threading.Event() for x in range(NUM_DANCERS)]
        self.hasRecvPositionalChange = [False for x in range(NUM_DANCERS)]
        self.shutdown = threading.Event()

        self.dance_server = Ultra96Server(SERVER_HOST, SERVER_PORT, self.dataQueues, self.prediction, self.readyForEval, self.clockSyncFlags, self.clearDataQueueFlags, self.predictionLock, self.dancerIsConnected, self.hasRecvPositionalChange, self.shutdown, self.predictionListPtr, self.predictionListPtrLock)
        self.ml_handler = MlHandler(self.dataQueues, self.prediction, self.readyForEval, self.predictionLock, self.clockSyncFlags, self.clearDataQueueFlags, self.submittedToEval, self.dancerIsConnected, self.hasRecvPositionalChange, self.shutdown, self.predictionListPtr, self.predictionListPtrLock)
        self.eval_client = EvalClient(EVAL_HOST, EVAL_PORT, self.prediction, self.readyForEval, self.predictionLock, self.submittedToEval, self.dancerIsConnected, self.shutdown)
        

    def run(self):
        self.dance_server.start()
        self.ml_handler.start()
        self.eval_client.start()


if __name__ == '__main__':
    if NUM_DANCERS != 3 and IS_EVAL == 1:
        print(f'Need 3 dancers to connect to Eval server, please check NUM_DANCERS and IS_EVAL in config.py')
        sys.exit()
    mainthread = MainThread()
    mainthread.run()
    