import numpy as np
import picamera
import picamera.array

class Recorder(object):
    def __init__(self, camera):
        self.busy = False
        self.camera = camera

    def record(self):
        if self.busy:
            return
        self.busy = True
        print("Starting Recording")
        self.camera.resolution = (640, 480)
        self.camera.start_recording('my_video.h264', splitter_port=2)
        self.camera.wait_recording(10, splitter_port=2)
        self.camera.stop_recording(splitter_port=2)
        print("Finished Recording")
        self.busy = False

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, recorder):
        super().__init__(camera)
        self.recorder = recorder

    def analyse(self, a):
        a = np.sqrt(
                np.square(a['x'].astype(np.float)) +
                np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 40).sum() > 2:
            print('Motion detected!')
            self.recorder.record()

class PiMotion(object):
    def __init__(self, callback=None, debug=False):
        self.debug = debug
        self.callback = callback

    def start(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (1280, 720)
            recorder = Recorder(camera)

            motion = DetectMotion(camera, recorder)

            camera.start_recording('/dev/null', format='h264', motion_output=motion)
            camera.wait_recording(20)
            camera.stop_recording()