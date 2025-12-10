import random
import constants

class Tetromino:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(constants.tetrominos) - 1)
        self.rotation = 0
        self.droppedlines = 0
        self.freezetimer = None
        self.actionlist = {}

    def image(self):
        return constants.tetrominos[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(constants.tetrominos[self.type])

