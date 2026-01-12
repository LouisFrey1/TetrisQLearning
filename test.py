
import argparse
import torch
import pygame
import os.path
import random
import constants
from game import Tetris
from DeepQNetwork import DeepQNetwork

def get_args():
    parser = argparse.ArgumentParser(
        """Implementation of Deep Q Network to play Tetris""")

    parser.add_argument("--width", type=int, default=10, help="The common width for all images")
    parser.add_argument("--height", type=int, default=20, help="The common height for all images")
    parser.add_argument("--saved_path", type=str, default="trained_models")
    parser.add_argument("--file_name", type=str, default="tetris_final")
    parser.add_argument("--display_board", default=False, help="Whether to display the tetris board during the testing process")

    args = parser.parse_args()
    return args


def test(opt):
    if os.path.isfile("{}/{}".format(opt.saved_path, opt.file_name)) == False:
        print("Model file not found!")
        return -1
    torch.manual_seed(123)
    model = torch.load("{}/{}".format(opt.saved_path, opt.file_name), weights_only=False, map_location=lambda storage, loc: storage)
    model.eval()
    env = Tetris(width=opt.width, height=opt.height)
    while True:
        env.new_tetromino()
        if opt.display_board:
            display(env)

        next_steps = env.get_next_states()
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        predictions = model(next_states)[:, 0]
        index = torch.argmax(predictions).item()
        action = next_actions[index]
        _, done = env.step(action)

        if done:
            break
    return env.clearedlines
        
def display(tetris):
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode(constants.SIZE)
    screen.fill(constants.WHITE)
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
    pygame.display.flip()
    pygame.time.wait(100)    
    
if __name__ == "__main__":
    opt = get_args()
    sim_length = 100
    scores = []
    random.seed(123)
    for i in range(sim_length):        
        score = test(opt)
        if score == -1:
            break
        scores.append(score)
        print("Simulation: {}/{}: Score {}".format(i+1, sim_length, score))  
    print("Average Score over {} simulations: {}".format(sim_length, sum(scores)/sim_length))