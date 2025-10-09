import tetromino
import constants
import numpy as np
import copy

class Tetris:
    def __init__(self, height, width):
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.tetromino = None
        self.next_tetromino = tetromino.Tetromino(3, 0)
        self.respawn = True
        self.height = height
        self.width = width
        self.field = []
        self.clearedlines = 0
        self.state = "start"
        for _ in range(height):
            new_line = []
            for _ in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_tetromino(self):
        self.tetromino = self.next_tetromino
        self.next_tetromino = tetromino.Tetromino(3, 0)
        if self.intersects():
            self.state = "gameover"
        if self.respawn:
            fitness = self.get_next_states_fitness()
            self.execute_opt_move(fitness)

    def pause(self):
        if self.state == "start":
            self.state = "pause"
        elif self.state == "pause":
            self.state = "start"
        

    def intersects(self):
        intersection = False
        for square in self.tetromino.image():
            i = square // 4
            j = square % 4
            if i + self.tetromino.y > self.height - 1 or \
                    j + self.tetromino.x > self.width - 1 or \
                    j + self.tetromino.x < 0 or \
                    self.field[i + self.tetromino.y][j + self.tetromino.x] > 0:
                intersection = True
        return intersection

    def break_lines(self):
        lines = 0
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
                self.field[0] = [0 for _ in range(self.width)]
        if lines > 0:
            self.clearedlines += lines
            

    def go_space(self):
        if self.state == "start":
            while not self.intersects():
                self.tetromino.y += 1
            self.tetromino.y -= 1
            self.freeze()

    def go_down(self):
        if self.state == "start":
            self.tetromino.y += 1
            if self.intersects():
                self.tetromino.y -= 1
                self.freeze()

    def go_up(self):
        if self.state == "start":
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
        if self.state == "start":
            old_x = self.tetromino.x
            self.tetromino.x += dx
            if self.intersects():
                self.tetromino.x = old_x

    def rotate(self):
        if self.state == "start":
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
        return holes, bumpiness, height
    
    def get_next_states_fitness(self):
        fitness = {}
        num_rotations = len(constants.tetrominos[self.tetromino.type])
        for i in range(num_rotations):
            valid_xs = self.width - self.tetromino.get_length(i) + 1
            for x in range(valid_xs):
                if x + self.tetromino.get_end() > self.width:
                    break
                simulated_game = copy.deepcopy(self)
                simulated_game.respawn = False
                simulated_game.tetromino.rotation = i
                for _ in range(5):
                    simulated_game.go_side(-1)
                simulated_game.go_side(x)
                simulated_game.go_space()
                if simulated_game.state == "gameover":
                    fitness[(x, i)] = -float('inf')
                else:
                    fitness[(x, i)] = simulated_game.get_lookahead_states_fitness()
        return fitness
    
    def get_lookahead_states_fitness(self):
        fitness = {}
        num_rotations = len(constants.tetrominos[self.tetromino.type])
        for i in range(num_rotations):
            valid_xs = self.width - self.tetromino.get_length(i) + 1
            for x in range(valid_xs):
                if x + self.tetromino.get_end() > self.width:
                    break
                simulated_game = copy.deepcopy(self)
                simulated_game.respawn = False
                simulated_game.tetromino = copy.deepcopy(self.tetromino)
                simulated_game.tetromino.rotation = i
                for _ in range(5):
                    simulated_game.go_side(-1)
                simulated_game.go_side(x)
                simulated_game.go_space()
                if simulated_game.state == "gameover":
                    fitness[(x, i)] = -float('inf')
                else:
                    cleared_lines = simulated_game.clearedlines - self.clearedlines
                    holes, bumpiness, height = simulated_game.get_state()
                    state = tuple([height, cleared_lines, holes, bumpiness])
                    fitness[(x, i)] = self.get_fitness(state)
        return max(fitness.values())
    
    def execute_opt_move(self, fitness):
        (x, rotation) = max(fitness, key=fitness.get)
        for _ in range(rotation):
            self.rotate()
        for _ in range(5):
            self.go_side(-1)
        self.go_side(x)

    def get_fitness(self, state):
        return constants.HEIGHT_WEIGHT*state[0] + constants.LINES_WEIGHT*state[1] + constants.HOLES_WEIGHT*state[2] + constants.BUMPINESS_WEIGHT*state[3]
                
                





        
