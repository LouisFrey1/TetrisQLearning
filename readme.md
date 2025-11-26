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
```

## Base Game
Start game: 
```bash
py simulation.py
```

This branch contains the base game of tetris for the user to play themselves. Use the left and right arrow keys to move the tetromino, the up arrow key to rotate and the spacebar to drop the tetromino. To pause the game, press "p"; to leave press ESC.

## Hardcoded
Start game:
```bash
py simulation.py
```

In the simplest version, the best possible action is decided by simulating all possible actions for the current tetromino (all rotations r and placements p), and calculating 4 values:
- Total height of all columns (a)
- Number of lines cleared (b)
- Number of holes: Empty spaces with tiles above it (c)
- Bumpiness: Total difference in height between each pair of adjacent columns (d)
These values are weighted using the numbers found in https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player to calculate a fitness value for each possible action. The action with the heighest fitness value is always taken.

fitness = -0.510066 \cdot a + 0.760666 \cdot b - 0.35663 \cdot c - 0.184483 \cdot d

If a move results in a game over, it is assigned a fitness of negative infinity.

Due to its simplicity, this model only considers dropping the tetrominos from the top, and is not capable of moving around obstacles, which makes holes a lot more difficult to deal with. Futhermore, this model does not consider the lookahead piece. This might be the reason why the model in the source can run infinitely, while this one cannot.

This model produces decent results, but does not run infinitely. When the blocks are stacked very high, this solution often prioritizes a low bumpiness instead of reducing the height, usually waiting for a I-Tetromino, while ignoring the threat of game over. When there is no way to immediately clear a line, this model doesn't prepare to clear it in the near future; instead it focuses on not creating holes. Furthermore, it seems too comfortable letting the blocks stack up over the halfway point, allowing holes to form in the process and allowing for a quicker defeat.

After running 100 games, the hardcoded model achieved an average of 391.01 lines cleared, with scores ranging between 55 lines cleared and 1674 lines cleared. As these results show, there is a lot of room for improvement.

## Hardcoded With Lookahead
Start game: 
```bash
py simulation.py
```
This solution extends the hardcoded version by adding the lookahead piece into the calculation of the best possible move. The fitness of a move is now calculated using the state after 2 moves, instead of just one. This allows the model to think ahead and pull off more complicated maneuvers.

![Tetris Screenshot](images/Screenshot3.png)

For example, this placement of the T-Tetromino would receive a poor fitness from the previous model, since it creates a hole and does not clear any lines. When paired with the lookahead piece however, the updated model can see that the line can be cleared using the next tetronimo, erasing the hole.

After reaching 100.000 lines cleared, it is safe to assume that this solution allows the game to run infinitely.

![Tetris Screenshot](images/Screenshot4.png)


The only downside of this solution is the much slower performance. While the previous model only had to simulate p \cdot r (#possible positions \cdot #possible rotations) possible actions, this version has to simulate p_1 \cdot r_1 \cdot p_2 \cdot r_2 possible actions. If p_1=p_2=p=8 and r_1=r_2=r=4, this results in 1024 simulations instead of 32. Clearing 100 lines took this model 28.89 seconds, while the previous one achieved the same in only 4.53 seconds.

## Deep Q-Learning
Train model: 
```bash
py train.py (--lr <learning rate> --gamma <gamma> --num_epochs <number of epochs> --file_name <filename> --display_board <True/False>) --save_interval <save_interval>
```
The trained model is saved at trained_models/<filename> (tetris_final by default). An additional model is saved at trained_models/"tetris_<epoch>" every <save_interval> epochs (Disabled by default).
To view the training progress and compare to other models, use 
```bash
tensorboard --logdir=runs
```
Test model: 
```bash
py test.py (--file_name <filename> --display_board <True/False>)
```
Activate display_board to show the board during training/testing. False by default.

The function get_args() in train.py and test.py shows additional optional parameters.

In this branch, I created a Deep Q-Learning Network, that takes a 4-dimensional vector containing the state (height, lines cleared, bumpiness, number of holes) as input and returns a fitness value for the given state, using a hidden layer with 64 units. The weights are initialized using the xavier uniform function.

Training:

* Initialize field, network, optimizer and replay memory.
* Fill 10% of the replay memory with data before starting the first epoch.
* Each epoch consists of a complete game of Tetris; until game over is reached or 5000 lines are cleared (in case the model is able to run infinitely).
* An action is represented as (position on x-axis, #rotations).
* A dictionary mapping the possible actions to the resulting states is generated by simulating all possibilities (similar to the Hardcoded branch).
* I utilize a linearly decaying exploration probability \epsilon, that decides whether to take the predicted action or a random action. After 2000 epochs, the \epsilon value settles at 0.001.
* If the random action is not taken, the deep Q-Network is used to calculate the action that maximizes the fitness of the next state.
* After an action is chosen, the previous state, the current state and the reward is added to the replay memory.
* There are multiple options for the reward function: 1 + #lines cleared^2; 1 + #lines cleared; 1, if at least 1 line was cleared.
* The first 2 options promote a more risky playstyle, that involves leaving a column at the edge, while waiting to clear as many lines as possible with a single tetromino, while the last option prioritizes clearing lines whenever possible.
* After each epoch, a minibatch (512 samples) is taken from the replay memory and used to update the weights of the model.

Single (lr 0.01):
Average Score over 100 simulations: 225.89
Multi (lr 0.01):
Average Score over 100 simulations: 155.27
Quadratic:
Average Score over 100 simulations: 142.84
Linear:
Average Score over 100 simulations: 190.41
Single (lr 0.001):
Average Score over 100 simulations: 135.47
10000 epochs:
Average Score over 100 simulations: 78.75
Harder (Single):
Average Score over 100 simulations: 135.21
Harder (Multi):
Average Score over 100 simulations: 178.31

## DeepQLearningLookahead

## DeepQLearningLookaheadStates

## DeepQLearningDifficult

https://www.ideals.illinois.edu/items/118525 suggests, that increasing the frequency of more difficult blocks (Z and N) increases the quality of the model significantly. 

## Sources

https://github.com/vietnh1009/Tetris-deep-Q-learning-pytorch/
https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player
https://gist.github.com/timurbakibayev/1f683d34487362b0f36280989c80960c
https://www.ideals.illinois.edu/items/118525

## License

This project is licensed under the MIT License.
