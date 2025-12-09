import pygame
import argparse

import constants
import game

def get_args():
    parser = argparse.ArgumentParser("""Implementation of Deep Q Network to play Tetris""")
    parser.add_argument("--width", type=int, default=10, help="The common width for all images")
    parser.add_argument("--height", type=int, default=20, help="The common height for all images")
    parser.add_argument("--display_board", type=bool, default=True, help="Whether to display the game board while training")
    parser.add_argument("--sim_length", type=int, default=100, help="Number of games to simulate")
    args = parser.parse_args()
    return args

def run_game(opt):
    tetris = game.Tetris(height=constants.HEIGHT, width=constants.WIDTH)
    if opt.display_board:
        pygame.init()
        pygame.display.set_caption("Tetris")
        screen = pygame.display.set_mode(constants.SIZE)
    tetris.new_tetromino()
    while tetris.state != "gameover":
        fitness = tetris.get_next_states_fitness()
        tetris.execute_opt_move(fitness)

        if opt.display_board:
            display(tetris, screen)
        else:
            if tetris.clearedlines and tetris.clearedlines % 100 == 0:
                print("{} Lines cleared".format(tetris.clearedlines))
        tetris.go_space()
        
    return tetris.clearedlines

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
        
    # Draws text
    font = pygame.font.SysFont('Calibri', 25, True, False)
    linestext = font.render("Lines cleared: " + str(tetris.clearedlines), True, constants.BLACK)
    screen.blit(linestext, [0, 0])

    pygame.display.flip()

if __name__ == "__main__":
    opt = get_args()
    scores = []
    for game_nr in range(opt.sim_length):
        score = run_game(opt)
        scores.append(score)
        print("Game " + str(game_nr+1) + " Score: " + str(score))
    print("Average score: " + str(sum(scores)/len(scores)))
    print("Max score: " + str(max(scores)))
    print("Min score: " + str(min(scores)))
    pygame.quit()
