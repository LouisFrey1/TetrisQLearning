
import argparse
import torch
from game import Tetris
from DeepQNetwork import DeepQNetwork

def get_args():
    parser = argparse.ArgumentParser(
        """Implementation of Deep Q Network to play Tetris""")

    parser.add_argument("--width", type=int, default=10, help="The common width for all images")
    parser.add_argument("--height", type=int, default=20, help="The common height for all images")
    parser.add_argument("--block_size", type=int, default=30, help="Size of a block")
    parser.add_argument("--fps", type=int, default=300, help="frames per second")
    parser.add_argument("--saved_path", type=str, default="trained_models")
    parser.add_argument("--output", type=str, default="output.mp4")

    args = parser.parse_args()
    return args


def test(opt):
    torch.serialization.add_safe_globals([torch.nn.modules.container.Sequential])
    torch.serialization.safe_globals([DeepQNetwork])
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    if torch.cuda.is_available():
        model = torch.load("{}/tetris_final.pt".format(opt.saved_path))
    else:
        model = torch.load("{}/tetris_final.pt".format(opt.saved_path), weights_only=False, map_location=lambda storage, loc: storage)
    model.eval()
    env = Tetris(width=opt.width, height=opt.height)
    if torch.cuda.is_available():
        model.cuda()
    while True:
        env.new_tetromino()
        next_steps = env.get_next_states()
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        if torch.cuda.is_available():
            next_states = next_states.cuda()
        predictions = model(next_states)[:, 0]
        index = torch.argmax(predictions).item()
        action = next_actions[index]
        _, done = env.step(action)

        if done:
            break
        


if __name__ == "__main__":
    opt = get_args()
    test(opt)