import time
import threading
from queue import Queue

from ultra96_server import Ultra96Server
from eval_client import EvalClient
from ml_handler import MlHandler
from config import SERVER_HOST, SERVER_PORT, EVAL_HOST, EVAL_PORT, NUM_DANCERS


class MainThread():
    def __init__(self):
        self.prediction = {
            'positions': '#1 2 3', 
            'dance_move': {key: None for key in range(1, NUM_DANCERS+1)}, 
            'syncdelay': '1.87'
        }
        self.dataQueues = [Queue() for x in range(NUM_DANCERS)]
        self.readyForEval = threading.Event()
        self.predictionLock = threading.Lock()

        self.dance_server = Ultra96Server(SERVER_HOST, SERVER_PORT, self.dataQueues, self.prediction, self.readyForEval)
        self.ml_handler = MlHandler(self.dataQueues, self.prediction, self.readyForEval, self.predictionLock)
        self.eval_client = EvalClient(EVAL_HOST, EVAL_PORT, self.prediction, self.readyForEval, self.predictionLock)
        

    def run(self):
        self.dance_server.start()
        self.ml_handler.start()
        self.eval_client.start()


if __name__ == '__main__':
    mainthread = MainThread()
    mainthread.run()
    