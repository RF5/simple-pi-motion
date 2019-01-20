import numpy as np
import picamera
import picamera.array
import time
import json, os
from subprocess import run
from telegram_util import TelegramManager

record_length = 6 #seconds
debug = True
min_interval = 20 #seconds
camera_framerate = 10 #fps
camera_rotation = 180 #degrees
upload_resolution = (320, 240) #pixels
stop_after = 30#seconds, set to None to run forever
n_blocks_threshold = 10
blockdiff_threshold = 40

class Recorder:
    def __init__(self, camera, bot):
        self.camera = camera
        self.detected = False
        self.working = False
        self.bot = bot
        self.stime = time.time()

    def motion_detected(self):
        if not self.working:
            self.detected = True

    def tick(self):
        if time.time() - self.stime < min_interval:
            return
        if self.detected:
            os.remove('output.mp4')
            if debug: print("Started working on capturing")
            self.working = True
            self.detected = False

            self.camera.start_recording('output.h264', splitter_port=2, resize=upload_resolution)
            time.sleep(record_length)
            self.camera.stop_recording(splitter_port=2)

            if debug: print("Finished capturing")
            run("MP4Box -add output.h264 output.mp4", shell=True).returncode
            time.sleep(1)
            self.bot.send_video()
            self.stime = time.time()
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
        # If there're more than n_blocks_threshold vectors with a magnitude greater
        # than blockdiff_threshold, then say we've detected motion
        if (a > blockdiff_threshold).sum() > n_blocks_threshold:
            if debug: print('Motion detected!')
            if self.first:
                self.first = False
                return
            self.recorder.motion_detected()

class PiMotion(object):
    def __init__(self):
        self.bot = TelegramManager(json.loads(open('./bot_info.json', 'r').read())['token'])

    def start(self):
        stime = time.time()
        with picamera.PiCamera() as camera:
            camera.resolution = (1280, 720)
            camera.framerate = camera_framerate
            camera.rotation = camera_rotation
            recorder = Recorder(camera, self.bot)
            time.sleep(2)

            motion = DetectMotion(camera, recorder)
            try:
                print("STARTED monitoring")
                camera.start_recording('/dev/null', format='h264', motion_output=motion)

                if stop_after is not None:
                    while time.time() - stime < stop_after:
                        recorder.tick()
                        time.sleep(1)
                else:
                    while True:
                        recorder.tick()
                        time.sleep(1) 
            finally:
                camera.stop_recording()
                print("ENDED monitoring")

if __name__ == "__main__":
    spi = PiMotion()
    spi.start()