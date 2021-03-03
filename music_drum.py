import pygame as pg
import glob
import time
import os
from cv2 import cv2


class Music_drum():
    def __init__(self):

        pg.mixer.init()
        #pg.init()
        pg.mixer.set_num_channels(5)
        self.notes = {0: "Crash",
                      1: "Tom",
                      2: "Ride",
                      3: "Hi-Hat",
                      4: "Snare",
                      5: "Floor Tom",
                      6: "Kick"}

        self.sounds = {}

        for key in self.notes:
            #print(os.path.join("Music_Notes", self.notes[key] + ".wav"))
            self.sounds[key] = pg.mixer.Sound(os.path.join("Drums_Notes", self.notes[key] + ".wav"))
        
        #self.pg.mixer.set_num_channels(channel)
        #print(f"pygame.mixer.get_num_channels() : " {pg.mixer.get_num_channels()})
        self.lastIndex = -1

    def play_sound(self, index):

        if index != -1 and self.lastIndex != index:
            print(index, self.notes[index])
            pg.mixer.find_channel(True).play(self.sounds[index])

        self.lastIndex = index