import pygame
import constants
import game
import time

def run_game():
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode(constants.SIZE)
    clock = pygame.time.Clock()
    tetris = game.Tetris(20, 10)

    # Loop until the user clicks the close button.
    done = False
    pressing_down = False
    counter = 0

    while tetris.gamestate == "start" and not done:
        if tetris.tetromino is None:
            tetris.new_tetromino()
        counter += 1
        if counter > 100000:
            counter = 0
        if counter % constants.FPS == 0 or pressing_down:
            if tetris.tetromino.freezetimer is None:
                tetris.tetromino.freezetimer = tetris.go_down()
            else: 
                tetris.go_down2()
        # Enables moving when the block has reached the bottom for 1 second. Resets if the block can fall again
        if tetris.tetromino.freezetimer is not None:
            if time.time() > tetris.tetromino.freezetimer + 1:
                tetris.go_space()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_UP:
                    tetris.rotate()
                if event.key == pygame.K_LEFT:
                    tetris.go_left()
                if event.key == pygame.K_RIGHT:
                    tetris.go_right()
                if event.key == pygame.K_SPACE:
                    tetris.go_space()
                if event.key == pygame.K_ESCAPE:
                    tetris.__init__(20, 10)
                if event.key == pygame.K_p:
                    tetris.pause()
            if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        pressing_down = False
        display(tetris, screen) 
        clock.tick(constants.FPS)
    return tetris.score, tetris.clearedlines, done

def display(tetris, screen):
    screen.fill(constants.WHITE) 
    # Draws field
    for i in range(tetris.height):
        for j in range(tetris.width):
            pygame.draw.rect(screen, constants.GRAY, [tetris.x + tetris.zoom * j, tetris.y + tetris.zoom * i, tetris.zoom, tetris.zoom], 1)
            if tetris.field[i][j] > 0:
                pygame.draw.rect(screen, constants.colors[tetris.field[i][j]-1],
                                [tetris.x + tetris.zoom * j + 1, tetris.y + tetris.zoom * i + 1, tetris.zoom - 2, tetris.zoom - 1])

    # Draws current block
    if tetris.tetromino is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in tetris.tetromino.image():
                    pygame.draw.rect(screen, constants.colors[tetris.tetromino.type],
                                    [tetris.x + tetris.zoom * (j + tetris.tetromino.x) + 1,
                                    tetris.y + tetris.zoom * (i + tetris.tetromino.y) + 1,
                                    tetris.zoom - 2, tetris.zoom - 2])

    # Draws next block
        if tetris.next_tetromino is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.next_tetromino.image():
                        pygame.draw.rect(screen, constants.colors[tetris.next_tetromino.type],
                                        [constants.SIZE[0]-150 + tetris.zoom * (j + tetris.next_tetromino.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.next_tetromino.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2])
                        pygame.draw.rect(screen, constants.GRAY, 
                                        [constants.SIZE[0]-150 + tetris.zoom * (j + tetris.next_tetromino.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.next_tetromino.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2], 1)

    font = pygame.font.SysFont('Calibri', 25, True, False)
    scoretext = font.render("Score: " + str(tetris.score), True, constants.BLACK)
    linestext = font.render("Lines: " + str(tetris.clearedlines), True, constants.BLACK)

    screen.blit(scoretext, [0, 0])
    screen.blit(linestext, [0, 30])
    pygame.display.flip()

if __name__ == "__main__":
    scores = []
    # Initialize the game engine
    pygame.init()
    while 1:
        score, lines, done = run_game()
        if done: 
            break
        print("Score: {}, Lines: {}".format(score, lines))
    pygame.quit()