import argparse
import os
import shutil
from random import random, randint, sample

import numpy as np
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter

from DeepQNetwork import DeepQNetwork
from game import Tetris
from collections import deque
import pygame
import constants


def get_args():
    parser = argparse.ArgumentParser(
        """Implementation of Deep Q Network to play Tetris""")
    parser.add_argument("--width", type=int, default=10, help="The common width for all images")
    parser.add_argument("--height", type=int, default=20, help="The common height for all images")
    parser.add_argument("--batch_size", type=int, default=512, help="The number of images per batch")
    parser.add_argument("--lr", type=float, default=0.01, help="Learning rate")
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--initial_epsilon", type=float, default=1)
    parser.add_argument("--final_epsilon", type=float, default=1e-3)
    parser.add_argument("--num_decay_epochs", type=float, default=2000)
    parser.add_argument("--num_epochs", type=int, default=4000)
    parser.add_argument("--save_interval", type=int, default=2000)
    parser.add_argument("--replay_memory_size", type=int, default=30000,
                        help="Number of epoches between testing phases")
    parser.add_argument("--saved_path", type=str, default="trained_models")

    args = parser.parse_args()
    return args


def train(opt, displayBoard=False):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    writer = SummaryWriter()
    env = Tetris(height=opt.height, width=opt.width)
    model = DeepQNetwork()
    optimizer = torch.optim.Adam(model.parameters(), lr=opt.lr)
    criterion = nn.MSELoss()
    state = env.reset()
    if torch.cuda.is_available():
        model.cuda()
        state = state.cuda()

    replay_memory = deque(maxlen=opt.replay_memory_size)
    epoch = 0
    while epoch < opt.num_epochs:
        env.new_tetromino()
        # Draws field
        if displayBoard:
            display(env)
        next_steps = env.get_next_states()
        # Exploration or exploitation
        epsilon = opt.final_epsilon + (max(opt.num_decay_epochs - epoch, 0) * (
                opt.initial_epsilon - opt.final_epsilon) / opt.num_decay_epochs)
        u = random()
        random_action = u <= epsilon
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        if torch.cuda.is_available():
            next_states = next_states.cuda()
        model.eval()
        with torch.no_grad():
            predictions = model(next_states)[:, 0]
        model.train()
        if random_action:
            index = randint(0, len(next_steps) - 1)
        else:
            index = torch.argmax(predictions).item()

        next_state = next_states[index, :]
        action = next_actions[index]

        reward, done = env.step(action)

        if torch.cuda.is_available():
            next_state = next_state.cuda()
        replay_memory.append([state, reward, next_state, done])
        if done or env.clearedlines >= 5000:
            final_cleared_lines = env.clearedlines
            state = env.reset()
            if torch.cuda.is_available():
                state = state.cuda()
        else:
            state = next_state
            continue
        if len(replay_memory) < opt.replay_memory_size / 10:
            continue
        epoch += 1
        batch = sample(replay_memory, min(len(replay_memory), opt.batch_size))
        state_batch, reward_batch, next_state_batch, done_batch = zip(*batch)
        state_batch = torch.stack(tuple(state for state in state_batch))
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32)[:, None])
        next_state_batch = torch.stack(tuple(state for state in next_state_batch))

        if torch.cuda.is_available():
            state_batch = state_batch.cuda()
            reward_batch = reward_batch.cuda()
            next_state_batch = next_state_batch.cuda()

        q_values = model(state_batch)
        model.eval()
        with torch.no_grad():
            next_prediction_batch = model(next_state_batch)
        model.train()

        y_batch = torch.cat(
            tuple(reward if done else reward + opt.gamma * prediction for reward, done, prediction in
                  zip(reward_batch, done_batch, next_prediction_batch)))[:, None]

        optimizer.zero_grad()
        loss = criterion(q_values, y_batch)
        loss.backward()
        optimizer.step()

        print("Epoch: {}/{}, Cleared lines: {}".format(
            epoch,
            opt.num_epochs,
            final_cleared_lines))
        writer.add_scalar('Train/Cleared lines', final_cleared_lines, epoch - 1)

        #if epoch > 0 and epoch % opt.save_interval == 0:
        #    torch.save(model, "{}/tetris_{}".format(opt.saved_path, epoch))

    if not os.path.exists(opt.saved_path):
        os.makedirs(opt.saved_path)
    torch.save(model, "{}/tetris_final".format(opt.saved_path))


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
    pygame.time.wait(10)

if __name__ == "__main__":
    opt = get_args()
    train(opt, displayBoard=False)