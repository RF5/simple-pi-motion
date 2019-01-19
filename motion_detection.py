import numpy as np
import picamera
import picamera.array
import datetime
import time

# class Recorder(object):
#     def __init__(self, camera):
#         self.busy = False
#         self.camera = camera

#     def record(self):
#         if self.busy:
#             return
#         self.busy = True
#         print("Starting Recording")
#         self.camera.resolution = (640, 480)
#         self.camera.start_recording('my_video.h264', splitter_port=2)
#         self.camera.wait_recording(10, splitter_port=2)
#         self.camera.stop_recording(splitter_port=2)
#         print("Finished Recording")
#         self.busy = False

class Recorder:
    def __init__(self, camera):
        self.camera = camera
        self.detected = False
        self.working = False
        self.i = 0

    def motion_detected(self):
        if not self.working:
            self.detected = True

    def tick(self):
        if self.detected:
            print("Started working on capturing")
            self.working = True
            self.detected = False
            self.i += 1

            self.camera.start_preview()

            self.camera.start_recording('/home/pi/video.h264')
            time.sleep(6)
            self.camera.stop_recording()

            self.camera.stop_preview()

            print("Finished capturing")

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
    def __init__(self, callback=None, debug=False):
        self.debug = debug
        self.callback = callback

    def start(self):
        stime = time.time()
        with picamera.PiCamera() as camera:
            camera.resolution = (1280, 720)
            camera.framerate = 10
            camera.rotation = 180
            recorder = Recorder(camera)

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

            #camera.wait_recording(20)
            #camera.stop_recording()

if __name__ == "__main__":
    spi = PiMotion()
    spi.start()