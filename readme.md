# Tetris Q-Learning

A project implementing Q-Learning for the game Tetris.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Sources](#sources)
- [License](#license)

## Overview

This project explores reinforcement learning by applying Q-Learning to the classic game Tetris.

## Installation

```bash
git clone https://github.com/LouisFrey1/TetrisQLearning.git
cd TetrisQLearning
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
py simulation.py
```

## Hardcoded

In the simplest version, the best possible action is decided by simulating all possible actions for the current tetromino (all rotations and placements), and calculating 4 values:
- Total height of all columns (a)
- Number of lines cleared (b)
- Number of holes: Empty spaces with tiles above it (c)
- Bumpiness: Total difference in height between each pair of adjacent columns (d)
These values are weighted using the numbers found in https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player to calculate a fitness value for each possible action. The action with the heighest fitness value is always taken.

fitness = -0.510066*a + 0.760666*b - 0.35663*c - 0.184483*d

Due to its simplicity, this model only considers dropping the tetrominos from the top, and is not capable of moving around obstacles, which makes holes a lot more difficult to deal with. This might be the reason why the source of the weights can run infinitely, while this one cannot. Futhermore, this model does not consider the next piece.

This model produces decent results, but doesn't run infinitely. When the blocks are stacked very high, this solution does not consider the possible future option of "game over", often prioritising a low bumpiness instead of reducing the height. Furthermore, it seems too comfortable letting the blocks stack up over the halfway point, allowing holes to form in the process and allowing for a quicker defeat. When looking at every tetromino placement individually, the decisions seem reasonable, but when 

After running 100 games, the hardcoded model achieved an average of 337.63 lines cleared, with the worst score being 55 lines cleared and the best score being 1649 lines cleared. As these results show, there is a lot of room for improvement.

## Sources

https://github.com/vietnh1009/Tetris-deep-Q-learning-pytorch/
https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player
https://gist.github.com/timurbakibayev/1f683d34487362b0f36280989c80960c

## License

This project is licensed under the MIT License.