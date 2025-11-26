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

    # Generates a new tetromino and checks for game over
    def new_tetromino(self):
        self.tetromino = self.next_tetromino
        self.next_tetromino = tetromino.Tetromino(3, 0)
        if self.intersects():
            self.gamestate = "gameover"        

    # Checks if the current tetromino intersects with the field or borders
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

    # Removes full lines from the field
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

    # Drops the tetromino to the bottom
    def go_space(self):
        if self.gamestate == "start":
            while not self.intersects():
                self.tetromino.y += 1
            self.tetromino.y -= 1
            self.freeze()

    # Freezes the tetromino in place, checks for full lines and generates a new tetromino
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.tetromino.image():
                    self.field[i + self.tetromino.y][j + self.tetromino.x] = self.tetromino.type + 1
        self.break_lines()
        self.new_tetromino()

    # Moves the tetromino left or right
    def go_side(self, dx):
        if self.gamestate == "start":
            old_x = self.tetromino.x
            self.tetromino.x += dx
            if self.intersects():
                self.tetromino.x = old_x

    # Rotates the tetromino 90 degrees clockwise
    def rotate(self):
        if self.gamestate == "start":
            old_rotation = self.tetromino.rotation
            self.tetromino.rotate()
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
        
    # Calculates the number of empty spaces (holes) below filled spaces in the field
    def get_holes(self):
        holes = 0
        for j in range(self.width):
            i = 0
            # Find the first filled cell in the column
            while i < self.height and self.field[i][j] == 0:
                i += 1
            
            # Count empty cells below the first filled cell
            while i < self.height:
                if self.field[i][j] == 0:
                    holes += 1
                i += 1
        return holes

    # Calculate the height difference between adjacent columns and the total height
    def get_bumpiness(self):
        # Calculate the heights of each column
        column_heights = np.zeros(self.width)
        for j in range(self.width):
            for i in range(self.height):
                if self.field[i][j] > 0:
                    column_heights[j] = self.height - i
                    break
        total_height = np.sum(column_heights)

        # Calculate the height difference between adjacent columns
        bumpiness = np.abs(column_heights[:-1] - column_heights[1:])
        total_bumpiness = np.sum(bumpiness)
        return total_bumpiness, total_height
    
    # Returns the current state as a tensor of features
    def get_state(self):
        holes = self.get_holes()
        bumpiness, height = self.get_bumpiness()
        return torch.FloatTensor([height, self.clearedlines, holes, bumpiness])
    
    # Simulates all possible next states for the current tetromino
    def get_next_states(self):
        states = {}
        num_rotations = len(constants.tetrominos[self.tetromino.type])
        # Simulate all possible rotations
        for i in range(num_rotations):
            valid_xs = self.width - self.tetromino.get_length(i) + 1
            # Simulate all possible horizontal positions
            for x in range(valid_xs):
                if x + self.tetromino.get_end() > self.width:
                    break
                simulated_game = copy.deepcopy(self)
                simulated_game.tetromino.rotation = i
                for _ in range(5):
                    simulated_game.go_side(-1)
                simulated_game.go_side(x)
                simulated_game.go_space()
                # Save the resulting state for this rotation and position
                states[(x, i)] = simulated_game.get_state()
        return states
    
    # Executes the given action and returns the reward
    def step(self, action):
        lines_cleared_old = self.clearedlines
        (x, rotation) = action
        # Execute the action
        for _ in range(rotation):
            self.rotate()
        for _ in range(5):
            self.go_side(-1)
        self.go_side(x)
        self.go_space()
        reward = 1 + (self.clearedlines - lines_cleared_old)
        #reward = 1 + (self.clearedlines - lines_cleared_old)^2
        #reward = int((self.clearedlines - lines_cleared_old) > 0) # clearing multiple lines at once still gives reward of 1
        return reward, self.gamestate == "gameover"
    




        
