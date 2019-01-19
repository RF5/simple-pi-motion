import numpy as np
import picamera
import picamera.array
import datetime
import time
from telegram_util import TelegramManager
import json
from subprocess import run
import os

record_length = 6

class Recorder:
    def __init__(self, camera, bot):
        self.camera = camera
        self.detected = False
        self.working = False
        self.i = 0
        self.bot = bot

    def motion_detected(self):
        if not self.working:
            self.detected = True

    def tick(self):
        if self.detected:
            os.remove('output.mp4')
            print("Started working on capturing")
            self.working = True
            self.detected = False
            self.i += 1

            self.camera.start_recording('output.h264', splitter_port=2, resize=(320, 240))
            time.sleep(record_length)
            self.camera.stop_recording(splitter_port=2)

            print("Finished capturing")
            run("MP4Box -add output.h264 output.mp4", shell=True).returncode
            time.sleep(1)
            self.bot.send_video()
            self.working = False

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, recorder):
        super().__init__(camera)
        self.recorder = recorder
        self.first = True

    def analyse(self, a):
        a = np.sqrt(
                np.square(a['x'].astype(np.float)) +
                np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 40).sum() > 10:#2:
            print('Motion detected!')
            if self.first:
                self.first = False
                return
            self.recorder.motion_detected()

class PiMotion(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.bot = TelegramManager(json.loads(open('./bot_info.json', 'r').read())['token'])

    def start(self):
        stime = time.time()
        with picamera.PiCamera() as camera:
            camera.resolution = (1280, 720)
            camera.framerate = 10
            camera.rotation = 180
            recorder = Recorder(camera, self.bot)

            time.sleep(2)
            motion = DetectMotion(camera, recorder)
            try:
                print("STARTED RECCCC")
                camera.start_recording('/dev/null', format='h264', motion_output=motion)

                while time.time() - stime < 30:
                    recorder.tick()
                    time.sleep(1)
            finally:
                camera.stop_recording()
                print("ENDED RECC")

if __name__ == "__main__":
    spi = PiMotion()
    spi.start()