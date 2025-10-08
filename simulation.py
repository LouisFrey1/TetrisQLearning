import pygame
import constants
import game

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
        if tetris.tetromino is None:
            tetris.new_tetromino()
        counter += 1
        if counter > 100000:
            counter = 0
        #if counter % (constants.FPS // 4) == 0 or pressing_down:
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
 
        screen.fill(constants.WHITE)

        # Draws field
        for i in range(tetris.height):
            for j in range(tetris.width):
                pygame.draw.rect(screen, constants.GRAY, [tetris.x + tetris.zoom * j, tetris.y + tetris.zoom * i, tetris.zoom, tetris.zoom], 1)
                if tetris.field[i][j] > 0:
                    pygame.draw.rect(screen, constants.GRAY,
                                    [tetris.x + tetris.zoom * j + 1, tetris.y + tetris.zoom * i + 1, tetris.zoom - 2, tetris.zoom - 1])

        # Draws current block
        if tetris.tetromino is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.tetromino.image():
                        pygame.draw.rect(screen, constants.colors[tetris.tetromino.color],
                                        [tetris.x + tetris.zoom * (j + tetris.tetromino.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.tetromino.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2])
                        
        # Draws next block
        if tetris.next_tetromino is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.next_tetromino.image():
                        pygame.draw.rect(screen, constants.colors[tetris.next_tetromino.color],
                                        [constants.SIZE[0]-150 + tetris.zoom * (j + tetris.next_tetromino.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.next_tetromino.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2])
                        pygame.draw.rect(screen, constants.GRAY, 
                                        [constants.SIZE[0]-150 + tetris.zoom * (j + tetris.next_tetromino.x) + 1,
                                        tetris.y + tetris.zoom * (i + tetris.next_tetromino.y) + 1,
                                        tetris.zoom - 2, tetris.zoom - 2], 1)

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
        clock.tick(constants.FPS)    
    return tetris.clearedlines

def simulate(sim_length):
    scores = []
    # Initialize the game engine
    pygame.init()

    for game_nr in range(sim_length):
        score = run_game()
        scores.append(score)
        print("Game " + str(game_nr+1) + " finished with " + str(score) + " lines cleared.")

    print("Average score: " + str(sum(scores)/len(scores)))
    print("Max score: " + str(max(scores)))
    print("Min score: " + str(min(scores)))
    pygame.quit()
simulate(100)
