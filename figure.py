import random
import constants
import numpy as np



class Figure:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(constants.figures) - 1)
        self.color = self.type
        self.rotation = 0
        self.droppedlines = 0
        self.freezetimer = None
        self.spacetimer = None
        self.actionlist = {}

    
    
    def image(self):
        return constants.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(constants.figures[self.type])

    def get_start(self):
        temp = np.array(self.image())
        temp = temp % 4
        return np.min(temp)

    def get_end(self):
        temp = np.array(self.image())
        temp = temp % 4
        return np.max(temp)

    def get_length(self):
        temp = np.array(self.image())
        temp = temp % 4
        length = np.max(temp) - np.min(temp) + 1
        return length
