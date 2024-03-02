## MODULES ##
import time
from threading import Thread


## RepeatedTimer class to handle playback ##
class RepeatedTimer(Thread):
    def __init__(self, speed, function):
        super().__init__()

        self.speed = speed
        self.function = function
        self.pause = False
        self.daemon = True


    def run(self):
        while not self.pause:
            time.sleep(60 / (self.speed * 16) -
                       (time.monotonic() % (60 / (self.speed * 16))))  # fix the distortion in time.sleep
            if not self.pause:
                self.function()


    def stop(self):
        self.pause = True
