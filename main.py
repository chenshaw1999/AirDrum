# From Python
# It requires OpenCV installed for Python
import sys
import os
import argparse

#from myGame import MyGame
from music_drum import Music_drum
import numpy as np
from cv2 import cv2
from threading import Thread
import time

Drum_location = {
    "Crash": {"X" : 215, "Y" : 20, "distance" : 50},
    "Tom": {"X" : 310, "Y" : 170, "distance" : 40},
    "Ride": {"X" : 450, "Y" : 110, "distance" : 70},
    "Hi-Hat": {"X" : 180, "Y" : 160, "distance" : 38},
    "Snare": {"X" : 200, "Y" : 295, "distance" : 45},
    "F_Tom": {"X" : 440, "Y" : 285, "distance" : 48}
}

Kick_location = {"X" : 337, "Y" : 417, "distance" : 43}

def calculate_dist(source_X, source_Y, destination_X, destination_Y):
    return np.linalg.norm(np.array([source_X, source_Y]) - np.array([destination_X, destination_Y]))

def in_which_drum(position_X, position_Y):
    for i, key in enumerate(Drum_location):
        drum = Drum_location[key]

        if(calculate_dist(drum['X'], drum['Y'], position_X, position_Y) < drum['distance']):
            # print(key)
            return i

    return -1

def if_kick(position_X, position_Y):
    if(calculate_dist(0, Kick_location['Y'], 0, position_Y) < Kick_location['distance']):
            # print(key)
        return 6

    return -1    

horizontal_line = 480 // 4 * 3
vertical_lines = [640 // 8 * i - 1 for i in range(1, 9)]
Kit_Img = cv2.imread("Drums_Notes/kit.png")


def draw_line(myMusic, datum):

    image_to_display = np.array(datum.cvOutputData)[:, ::-1]
    image_to_display = image_to_display * 0.7 + Kit_Img * 0.3
    image_to_display = image_to_display.astype(np.uint8)

    cv2.imshow("HCI_hw5", cv2.resize(image_to_display, (960, 720)))


def find_location(myMusic, datum, position):

    position_X = 640 - int(datum.poseKeypoints[0][position][0])
    position_Y = int(datum.poseKeypoints[0][position][1])

    if position == 10: # for foot
        myMusic.play_sound(if_kick(position_X, position_Y))
    else:
        myMusic.play_sound(in_which_drum(position_X, position_Y))


class VideoStreamWidget(object):
    def __init__(self, params, src=0):
        self.capture = cv2.VideoCapture(src)
        
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()

        self.right_hand_music = Music_drum()
        self.left_hand_music = Music_drum()
        self.foot_music = Music_drum()

        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

        # Start the thread to read frames from the video stream

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            #time.sleep(.01)

    def show_frame(self):
        # Display frames in main program
        #cv2.imshow('frame', self.frame)
        self.compute_openpose(self.frame)
        #print(self.frame.shape)
        #print(self.frame.__class__)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

    def compute_openpose(self, frame):
        # Process Image
        datum = op.Datum()
        #print(f"now computing... {frame.shape}")
        datum.cvInputData = frame
        self.opWrapper.emplaceAndPop(op.VectorDatum([datum]))

        # Display Image
        draw_line(self.left_hand_music, datum)
        find_location(self.right_hand_music, datum, 4)        
        find_location(self.left_hand_music, datum, 7)
        find_location(self.foot_music, datum, 10) 

        

if __name__ == "__main__":
    # try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if sys.platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../../python/openpose/Release')
            os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + \
                '/../../x64/Release;' + dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../../python')
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["logging_level"] = 4
    params["output_resolution"] = "-1x-1"
    params["net_resolution"] = "128x128"
    params["alpha_pose"] = 0.5
    params["scale_gap"] = 0.3
    params["scale_number"] = 1
    params["render_threshold"] = 0.05
    params["render_pose"] = 1
    params["num_gpu_start"] = 0
    params["disable_blending"] = False
    params["heatmaps_add_parts"] = False
    params["heatmaps_add_PAFs"] = False
    # enable compute z coordinate when this set to 1
    params["tracking"] = 5
    params["number_people_max"] = 1      # if > 1, tracking must set to -1
    params["model_folder"] = "../../../../models/"
    params["keypoint_scale"] = 0
    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1:
            next_item = args[1][i+1]
        else:
            next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-', '')
            if key not in params:
                params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-', '')
            if key not in params:
                params[key] = next_item


    video_stream_widget = VideoStreamWidget(params = params)
    time.sleep(1)
    while(True):
        video_stream_widget.show_frame()

