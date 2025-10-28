import tetromino
import constants
import numpy as np
import copy
import torch

class Tetris:
    def __init__(self, height, width):
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.tetromino = None
        self.next_tetromino = tetromino.Tetromino(3, 0)
        self.height = height
        self.width = width
        self.field = []
        self.clearedlines = 0
        self.gamestate = "start"
        for _ in range(height):
            new_line = []
            for _ in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def reset(self):
        self.tetromino = None
        self.next_tetromino = tetromino.Tetromino(3, 0)
        self.field = []
        self.clearedlines = 0
        self.gamestate = "start"
        for _ in range(self.height):
            new_line = []
            for _ in range(self.width):
                new_line.append(0)
            self.field.append(new_line)
        return torch.FloatTensor([0, 0, 0, 0]) 

    def new_tetromino(self):
        self.tetromino = self.next_tetromino
        self.next_tetromino = tetromino.Tetromino(3, 0)
        if self.intersects():
            self.gamestate = "gameover"

    def pause(self):
        if self.gamestate == "start":
            self.gamestate = "pause"
        elif self.gamestate == "pause":
            self.gamestate = "start"
        

    def intersects(self):
        intersection = False
        for square in self.tetromino.image():
            i = square // 4
            j = square % 4
            if i + self.tetromino.y > self.height - 1 or \
                    j + self.tetromino.x > self.width - 1 or \
                    i + self.tetromino.y < 0 or \
                    j + self.tetromino.x < 0 or \
                    self.field[i + self.tetromino.y][j + self.tetromino.x] > 0:
                intersection = True
        return intersection

    def break_lines(self):
        i = self.height - 1
        while i >= 0:
            full = True
            for j in range(self.width):
                if self.field[i][j] == 0:
                    full = False
                    break
            if full:
                # remove the full row and insert an empty one at the top
                del self.field[i]
                self.field.insert(0, [0] * self.width)
                self.clearedlines += 1
            else:
                i -= 1

    def go_space(self):
        if self.gamestate == "start":
            while not self.intersects():
                self.tetromino.y += 1
            self.tetromino.y -= 1
            self.freeze()

    def go_down(self):
        if self.gamestate == "start":
            self.tetromino.y += 1
            if self.intersects():
                self.tetromino.y -= 1
                self.freeze()

    def go_up(self):
        if self.gamestate == "start":
            old_y = self.tetromino.y
            self.tetromino.y -= 1
            if self.intersects():
                self.tetromino.y = old_y

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.tetromino.image():
                    self.field[i + self.tetromino.y][j + self.tetromino.x] = self.tetromino.type + 1
        self.break_lines()
        self.new_tetromino()

    def go_side(self, dx):
        if self.gamestate == "start":
            old_x = self.tetromino.x
            self.tetromino.x += dx
            if self.intersects():
                self.tetromino.x = old_x

    def rotate(self):
        if self.gamestate == "start":
            old_rotation = self.tetromino.rotation
            self.tetromino.rotate()
            # Try to move tile left and right once to enable rotating at the edge
            if self.intersects():
                self.tetromino.rotation = old_rotation
        
    # Adds current block to field
    def get_field(self):
        total_field = np.array(self.field)
        x = self.tetromino.x
        y = self.tetromino.y
        for i in self.tetromino.image():
            total_field[y+i//4][x+i%4] = 1
        return total_field
        

    def get_holes(self):
        holes = 0
        for j in range(self.width):
            i = 0
            while i < self.height and self.field[i][j] == 0:
                i += 1
            while i < self.height:
                if self.field[i][j] == 0:
                    holes += 1
                i += 1
        return holes

    def get_bumpiness(self):
        column_heights = np.zeros(self.width)
        for j in range(self.width):
            for i in range(self.height):
                if self.field[i][j] > 0:
                    column_heights[j] = self.height - i
                    break
        total_height = np.sum(column_heights)
        bumpiness = np.abs(column_heights[:-1] - column_heights[1:])
        total_bumpiness = np.sum(bumpiness)
        return total_bumpiness, total_height
    
    def get_state(self):
        holes = self.get_holes()
        bumpiness, height = self.get_bumpiness()
        return torch.FloatTensor([height, self.clearedlines, holes, bumpiness])
    
    def get_next_states(self):
        states = {}
        lookahead_states = {}  
        num_rotations = len(constants.tetrominos[self.tetromino.type])
        for i in range(num_rotations):
            valid_xs = self.width - self.tetromino.get_length(i) + 1
            for x in range(valid_xs):
                if x + self.tetromino.get_end() > self.width:
                    break
                simulated_game = copy.deepcopy(self)
                simulated_game.tetromino.rotation = i
                for _ in range(5):
                    simulated_game.go_side(-1)
                simulated_game.go_side(x)
                simulated_game.go_space()
                states[(x, i)] = simulated_game.get_state()
                lookahead_states[(x, i)] = simulated_game.get_next_states_lookahead()
        return states, lookahead_states
    
    def get_next_states_lookahead(self):
        states = []
        num_rotations = len(constants.tetrominos[self.tetromino.type])
        for i in range(num_rotations):
            valid_xs = self.width - self.tetromino.get_length(i) + 1
            for x in range(valid_xs):
                if x + self.tetromino.get_end() > self.width:
                    break
                simulated_game = copy.deepcopy(self)
                simulated_game.tetromino.rotation = i
                for _ in range(5):
                    simulated_game.go_side(-1)
                simulated_game.go_side(x)
                simulated_game.go_space()
                states.append(simulated_game.get_state())
        return states
    

    def step(self, action):
        lines_cleared_old = self.clearedlines
        (x, rotation) = action
        for _ in range(rotation):
            self.rotate()
        for _ in range(5):
            self.go_side(-1)
        self.go_side(x)
        self.go_space()
        reward = self.clearedlines - lines_cleared_old
        reward = int(reward > 0) # clearing multiple lines at once still gives reward of 1
        return reward, self.gamestate == "gameover"
    




        
