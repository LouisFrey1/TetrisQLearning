
import argparse
import torch
import pygame
import os.path
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
    parser.add_argument("--display_board", type=bool, default=False, help="Whether to display the game board while training")
    parser.add_argument("--sim_length", type=int, default=100, help="Number of games to simulate for testing")

    args = parser.parse_args()
    return args


def test(opt):
    if os.path.isfile("{}/{}".format(opt.saved_path, opt.file_name))==False:
        print("No trained model with this name found")
        return -1
    torch.serialization.add_safe_globals([torch.nn.modules.container.Sequential])
    torch.serialization.safe_globals([DeepQNetwork])
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    if torch.cuda.is_available():
        model = torch.load("{}/{}}".format(opt.saved_path, opt.file_name))
    else:
        model = torch.load("{}/{}".format(opt.saved_path, opt.file_name), weights_only=False, map_location=lambda storage, loc: storage)
    model.eval()
    env = Tetris(width=opt.width, height=opt.height)
    if torch.cuda.is_available():
        model.cuda()
    while True:
        env.new_tetromino()
        if opt.display_board:
            display(env)

        next_steps, lookahead_steps = env.get_next_states()

        for action_key in lookahead_steps.keys():
            lookahead_state_list = lookahead_steps[action_key]
            lookahead_states = torch.stack(lookahead_state_list)
            if torch.cuda.is_available():
                lookahead_states = lookahead_states.cuda()
            next_steps[action_key] = torch.max(model(lookahead_states)[:, 0]).item()
        action = max(next_steps, key=next_steps.get)
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
    pygame.display.flip()
    
if __name__ == "__main__":
    opt = get_args()
    scores = []
    for i in range(opt.sim_length):
        score = test(opt)
        if score == -1:
            break
        scores.append(score)
        print("Simulation: {}/{}: Score {}".format(i+1, opt.sim_length, score))  
    print("Average Score over {} simulations: {}".format(opt.sim_length, sum(scores)/opt.sim_length))