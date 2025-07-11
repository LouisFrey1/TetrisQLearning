import random
import constants

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

