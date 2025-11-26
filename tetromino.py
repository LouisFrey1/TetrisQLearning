import random
import constants
import numpy as np



class Tetromino:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(constants.tetrominos) - 1)
        self.rotation = 0
        self.droppedlines = 0

    
    
    def image(self):
        return constants.tetrominos[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(constants.tetrominos[self.type])

    # Returns the start column of the tetromino based on its current rotation
    def get_start(self):
        return np.min(np.array(self.image()) % 4)

    # Returns the end column of the tetromino based on its current rotation
    def get_end(self):
        return np.max(np.array(self.image()) % 4)

    # Returns the length of the tetromino based on the input rotation
    def get_length(self, rotation):
        temp = np.array(constants.tetrominos[self.type][rotation]) % 4
        length = np.max(temp) - np.min(temp) + 1
        return length
