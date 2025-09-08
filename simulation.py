import pygame
import constants
import game
import random
import matplotlib.pyplot as plt
import time
import q_learning

def run_game():
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode(constants.SIZE)
    clock = pygame.time.Clock()
    tetris = game.Tetris(20, 10)

    # Loop until the user clicks the close button.
    done = False
    pressing_down = False
    counter = 0

    while tetris.state != "gameover" and not done:
        if tetris.figure is None:
            tetris.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0
        if counter % (constants.FPS) == 0 or pressing_down:
            tetris.go_down()
        #if counter % (constants.MOVE_FPS) == 0:
        #    rand_move = random.choice(["up", "left", "right", "space"])
        #    tetris.commands[rand_move]()

        #if counter % (constants.FPS) == 0 or pressing_down:
        #    if tetris.figure.freezetimer is None:
        #        tetris.figure.freezetimer = tetris.go_down()
        #    else: 
        #        tetris.go_down2()
        #    if tetris.figure.freezetimer is not None and tetris.figure.spacetimer is None:
        #        tetris.figure.spacetimer = tetris.figure.freezetimer
        # Enables moving when the block has reached the bottom for 1 second. Resets if the block can fall again
        #if tetris.figure.freezetimer is not None:
        #    if time.time() > tetris.figure.freezetimer + 1:
        #        tetris.go_space2()
        # Prevents infinite spinning, drops block 4 seconds after reaching the bottom once, even if the block can fall again
        #if tetris.figure.spacetimer is not None:
        #    if time.time() > tetris.figure.spacetimer + 4:
        #        tetris.go_space2()
        #if tetris.level > constants.MAX_LVL:
        #    done = True
        
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
 
        screen.fill(constants.WHITE)

        # Draws field
        for i in range(tetris.height):
            for j in range(tetris.width):
                pygame.draw.rect(screen, constants.GRAY, [tetris.x + tetris.zoom * j, tetris.y + tetris.zoom * i, tetris.zoom, tetris.zoom], 1)
                if tetris.field[i][j] > 0:
                    pygame.draw.rect(screen, constants.GRAY,
                                    [tetris.x + tetris.zoom * j + 1, tetris.y + tetris.zoom * i + 1, tetris.zoom - 2, tetris.zoom - 1])

        # Draws current block
        if tetris.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.figure.image():
                        pygame.draw.rect(screen, constants.colors[tetris.figure.color],
                                        [tetris.x + tetris.zoom * (j + tetris.figure.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.figure.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2])
                        
        # Draws next block
        if tetris.next_figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.next_figure.image():
                        pygame.draw.rect(screen, constants.colors[tetris.next_figure.color],
                                        [constants.SIZE[0]-150 + tetris.zoom * (j + tetris.next_figure.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.next_figure.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2])
                        pygame.draw.rect(screen, constants.GRAY, 
                                        [constants.SIZE[0]-150 + tetris.zoom * (j + tetris.next_figure.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.next_figure.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2], 1)

        font = pygame.font.SysFont('Calibri', 25, True, False)
        scoretext = font.render("Score: " + str(tetris.score), True, constants.BLACK)
        linestext = font.render("Lines: " + str(tetris.clearedlines), True, constants.BLACK)
        leveltext = font.render("Level: " + str(tetris.level), True, constants.BLACK)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        screen.blit(scoretext, [0, 0])
        screen.blit(linestext, [0, 30])
        screen.blit(leveltext, [constants.SIZE[0]-80, 0])
        if tetris.state == "gameover":
            screen.blit(text_game_over, [20, 200])
            screen.blit(text_game_over1, [25, 265])
            print(len(q_learning.q_table))

        pygame.display.flip()
        clock.tick(constants.FPS)    
    return tetris.score

def simulate(sim_length):
    games = list((range(0, sim_length)))
    game_labels = []
    scores = []
    # Initialize the game engine
    pygame.init()

    for game_nr in range(sim_length):
        score = run_game()
        scores.append(score)
        game_labels.append("Game " + str(game_nr+1))
        print("Game " + str(game_nr+1) + ": " + str(score))
    pygame.quit()
    #plt.bar(games, scores, label=game_labels, color="red")
    #plt.xlabel("Games")
    #plt.ylabel("Score")
    #plt.show()
simulate(1)
