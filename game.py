import tetromino
import time


class Tetris:
    def __init__(self, height, width):
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.score = 0
        self.height = height
        self.width = width
        self.field = []
        self.clearedlines = 0
        self.gamestate = "start"
        self.tetromino = None
        self.next_tetromino = tetromino.Tetromino(3, 0)

        for _ in range(height):
            new_line = []
            for _ in range(width):
                new_line.append(0)
            self.field.append(new_line)

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
        clearedlines_old = self.clearedlines
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
        self.score += 1 + (self.clearedlines - clearedlines_old) ** 2 
            
            

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
                return time.time()
        return None
    
    # used when block has already reached bottom, in case the block is moved in a way that it can fall again. Resets freezetimer
    def go_down2(self):
        if self.gamestate == "start":
            self.tetromino.y += 1
            if self.intersects():
                self.tetromino.y -= 1
            else:
                self.tetromino.freezetimer = None
        

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

    def go_left(self):
        self.go_side(-1)

    def go_right(self):
        self.go_side(1)

    def rotate(self):
        if self.gamestate == "start":
            old_rotation = self.tetromino.rotation
            self.tetromino.rotate()
            # Try to move tile left and right once to enable rotating at the edge
            if self.intersects():
                self.go_up()
                if self.intersects():
                    self.go_left()
                    if self.intersects():
                        self.go_right()
                        if self.intersects() and self.tetromino.type != 0:
                            self.tetromino.rotation = old_rotation
                    # I-Block needs to be moved left twice when rotated at the right edge
                    if self.intersects() and self.tetromino.type == 0:
                        self.go_side(-2)
                        if self.intersects():
                            self.tetromino.rotation = old_rotation