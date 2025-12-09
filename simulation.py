import pygame

import constants
import game

def run_game(display_board):
    tetris = game.Tetris(height=constants.HEIGHT, width=constants.WIDTH)
    while tetris.state != "gameover":
        if tetris.tetromino is None:
            tetris.new_tetromino()
        fitness = tetris.get_next_states_fitness()
        tetris.execute_opt_move(fitness)
        tetris.go_space()

        if display_board:
            display(tetris)
        else:
            if tetris.clearedlines and tetris.clearedlines % 100 == 0:
                print("{} Lines cleared".format(tetris.clearedlines))
        
    return tetris.clearedlines

def display(tetris):
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode(constants.SIZE)
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
        
    # Draws text
    font = pygame.font.SysFont('Calibri', 25, True, False)
    linestext = font.render("Lines cleared: " + str(tetris.clearedlines), True, constants.BLACK)
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))
    text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

    screen.blit(linestext, [0, 0])
    if tetris.state == "gameover":
        screen.blit(text_game_over, [20, 200])
        screen.blit(text_game_over1, [25, 265])

    pygame.display.flip()

def simulate(sim_length):
    scores = []
    # Initialize the game engine
    pygame.init()

    for game_nr in range(sim_length):
        score = run_game(display_board=True)
        scores.append(score)
        print("Game " + str(game_nr+1) + " Score: " + str(score))
    print("Average score: " + str(sum(scores)/len(scores)))
    print("Max score: " + str(max(scores)))
    print("Min score: " + str(min(scores)))
    pygame.quit()
simulate(10)
