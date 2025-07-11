import figure
import constants
import q_learning
import time
import numpy as np


class Tetris:
    def __init__(self, height, width):
        self.level = 1
        self.score = 0
        self.oldscore = 0
        self.state = "start"
        self.field = []
        self.height = 0
        self.width = 0
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.figure = None
    
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.clearedlines = 0
        self.state = "start"
        self.commands = {
            "up": self.rotate,
            "left": self.go_left,
            "right": self.go_right,
            "space": self.go_space
        }
        for _ in range(height):
            new_line = []
            for _ in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = figure.Figure(3, 0)
        self.oldscore = self.score
        

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def break_lines(self):
        lines = 0
        perfect = True
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
            elif zeros < self.width and perfect:
                perfect = False
        if lines > 0:
            self.clearedlines += lines
            for i in range(5):
                if self.level <= constants.score_table[i][0] and not perfect:
                    self.score += constants.score_table[i][lines]
                    break
                if self.level <= constants.score_table[i][0] and perfect:
                    self.score += constants.score_table[i][lines]*10
                    break
            if self.clearedlines >= 10*self.level:
                self.level += 1
            

    def go_space(self):
        if self.state == "start":
            self.figure.actionlist[self.get_state()] = 3 #space
            while not self.intersects():
                self.figure.y += 1
                self.figure.droppedlines += 2
            self.figure.y -= 1
            self.freeze()

    # no effect on q table, no score points
    def go_space2(self):
        if self.state == "start":
            while not self.intersects():
                self.figure.y += 1
            self.figure.y -= 1
            self.freeze()

    def go_down(self):
        if self.state == "start":
            self.figure.y += 1
            self.figure.droppedlines += 1
            if self.intersects():
                self.figure.y -= 1
                #self.freeze()
                return time.time()
        return None
    
    # used when block has already reached bottom, in case the block is moved in a way that it can fall again. Resets freezetimer
    def go_down2(self):
        if self.state == "start":
            self.figure.y += 1
            if self.intersects():
                self.figure.y -= 1
            else:
                self.figure.freezetimer = None
        

    def go_up(self):
        if self.state == "start":
            old_y = self.figure.y
            self.figure.y -= 1
            if self.intersects():
                self.figure.y = old_y

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    #self.field[i + self.figure.y][j + self.figure.x] = self.figure.color + 1
                    self.field[i + self.figure.y][j + self.figure.x] = len(constants.colors)
        self.score += self.figure.droppedlines * ((self.level // 2) + 1)
        self.break_lines()
        q_learning.q_update(self.figure.actionlist, self.state, self.score-self.oldscore)
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        if self.state == "start":
            old_x = self.figure.x
            self.figure.x += dx
            if self.intersects():
                self.figure.x = old_x

    def go_left(self):
        self.figure.actionlist[self.get_state()] = 1 #left
        self.go_side(-1)

    def go_right(self):
        self.figure.actionlist[self.get_state()] = 2 #right
        self.go_side(1)

    def rotate(self):
        if self.state == "start":
            old_rotation = self.figure.rotation
            self.figure.rotate()
            # Try to move tile left and right once to enable rotating at the edge
            if self.intersects():
                self.go_up()
                if self.intersects():
                    self.go_left()
                    if self.intersects():
                        self.go_right()
                        if self.intersects() and self.figure.type != 0:
                            self.figure.rotation = old_rotation
                    # I-Block needs to be moved left twice when rotated at the right edge
                    if self.intersects() and self.figure.type == 0:
                        self.go_side(-2)
                        if self.intersects():
                            self.figure.rotation = old_rotation
        # Rotation successful
        if self.figure.rotation != old_rotation:
            self.figure.actionlist[self.get_state()] = 0 #rotate
        

    def get_state(self):
        column_heights = [0,0,0,0,0,0,0,0,0,0]
        bumpiness = [0,0,0,0,0,0,0,0,0]
        #column_holes = [0,0,0,0,0,0,0,0,0,0]
        for j in range(self.width):
            for i in range(self.height):
                if column_heights[j] == 0 and self.field[i][j] == len(constants.colors):
                    column_heights[j] = self.height - i
                #elif column_heights[j] != 0 and self.field[i][j] == 0:
                #    column_holes[j] += 1
        #total_holes = sum(column_holes)
        for i in range(len(bumpiness)):
            bumpiness[i] = abs(column_heights[i+1]-column_heights[i])
        return (tuple(bumpiness), self.figure.x, self.figure.y, self.figure.type, self.figure.rotation)
        #return (tuple(column_heights), tuple(column_holes), total_holes, self.figure.x, self.figure.y, self.figure.type, self.figure.rotation)


    def get_field(self):
        column_heights = [0,0,0,0,0,0,0,0,0,0]
        bumpiness = [0,0,0,0,0,0,0,0,0]
        column_holes = [0,0,0,0,0,0,0,0,0,0]
        for j in range(self.width):
            for i in range(self.height):
                if column_heights[j] == 0 and self.field[i][j] == len(constants.colors):
                    column_heights[j] = self.height - i
                elif column_heights[j] != 0 and self.field[i][j] == 0:
                    column_holes[j] += 1
        total_holes = sum(column_holes)
        for i in range(len(bumpiness)):
            bumpiness[i] = abs(column_heights[i+1]-column_heights[i])
        return tuple(bumpiness), total_holes

    def calculate_reward(self):
        return