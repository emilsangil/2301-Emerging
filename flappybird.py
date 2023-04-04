import pygame
import neat
import time
import os
import random
pygame.font.init()

# Const for the window width and height for the game
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

# Const for the bird image and transform them 2x its size
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]

# Const for the pipe image and transform them 2x its size
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))

# Const for the base image and transform it 2x its size
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))

# Const for the background image and transform it 2x its size
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bg.png")))

# Font for the Score
SCORE_FONT = pygame.font.SysFont("comicsans", 50)

GEN = -1



class Bird:
    #  Images of the bird
    IMGS = BIRD_IMGS
    #  For the tilt of the bird
    MAX_ROTATION = 25
    #  Rotation of the bird each frame
    ROT_VEL = 20
    #  How long will we show the flap of the bird
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # Starting position of the bird
        self.x = x
        self.y = y
        # How much the bird is tilted
        self.tilt = 0
        # Physics of the bird going up and down
        self.tick_count = 0
        # Starting velocity
        self.vel = 0
        # Height of the bird
        self.height = self.y
        # Bird image count
        self.img_count = 0
        # Starting Image of the bird
        self.img = self.IMGS[0]

    def jump(self):
        # to go up you need negative velocity
        self.vel = -10.5
        # resets to 0 so we will know when we change direction or velocity
        self.tick_count = 0
        # Keep track of where is the bird
        self.height = self.y

    def move(self):
        # Add 1 frame
        self.tick_count += 1
        # Displacement tells how many pixels were moving up or down this frame
        # Kinematic equation for distance traveled with constant acceleration
        # d = initial velocity * (time elapsed + acceleration * time elapsed)^2
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        # Moving down 16 pixels or more just make it 16 pixels
        if d >= 16:
            d = 16

        # If moving upward make it move a little bit further
        if d < 0:
            d -= 2

        # Change the position of the bird depending on the displacement
        self.y += d

        # Checking if moving up
        if d < 0 or self.y < self.height + 50:
            # Tilt the bird by MAX_ROTATION upward
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # Checking if moving down
        else:
            # Tilt the bird downward
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, window):
        # Keep track of the image count
        self.img_count += 1

        # Check if img count to make an animation for flapping the wings of the bird
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # Rotate around the image around the center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        # Draw it on the window
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    #  space between our pipes
    GAP = 200
    # How fast the pipes moving around
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        # Keep track of top and pipe of the pipe
        self.top = 0
        self.bottom = 0
        # Getting the image of the top pipe by flipping the image
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        # Getting the image of the bottom pipe
        self.PIPE_BOTTOM = PIPE_IMG

        # Checks if the bird passed the pipe
        self.passed = False
        self.set_height()
    
    def set_height(self):
        # Generate random number where the pipe will be on the screen
        self.height = random.randrange(50, 450)
        # For the top pipe placed where we want it
        self.top = self.height - self.PIPE_TOP.get_height()
        # Sets the bottom pipe
        self.bottom = self.height + self.GAP
    
    def move(self):
        # Moving the pipe to the left
        self.x -= self.VEL
    
    def draw(self, window):
        # Draw the top pipe
        window.blit(self.PIPE_TOP, (self.x, self.top))
        # Draw the bottom pipe
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # bird mask(list of pixels)
        bird_mask = bird.get_mask()
        # top pipe mask(list of pixels)
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        # bottom pipe mask(list of pixels)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        # how far away the top left corner
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        # how far away the bottom left corner
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Point of overlap between the bird and bottom pipe
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        # Point of overlap between the bird and top pipe
        t_point = bird_mask.overlap(top_mask, top_offset)

        # Checks if there is a collision between the bird and pipe
        if t_point or b_point:
            return True
        return False

class Base:
    # Speed of the movement of the base
    VEL = 5
    # width of the base
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        # Start of the first image
        self.x1 = 0
        # Start of the second image
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Movement of the first image of the base
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        # Movement of the second image of the base
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, window):
        # draw the first image of the base
        window.blit(self.IMG, (self.x1, self.y))
        # draw the second image of the base
        window.blit(self.IMG, (self.x2, self.y))


def draw_window(window, birds, pipes, base, score, gen):
    # Draw at the top left
    window.blit(BG_IMG, (0,0))
    # Draw the two pipes
    for pipe in pipes:
        pipe.draw(window)

    # Score render
    text = SCORE_FONT.render("Score: " + str(score), 1, (255,255,255))
    # Draw the score
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    # Generation render
    text = SCORE_FONT.render("GEN: " + str(gen), 1, (255,255,255))
    # Draw the Generation
    window.blit(text, (10, 10))
    
    # Draw the base
    base.draw(window)
    # Draw the bird
    for bird in birds:
        bird.draw(window)

    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        # Setting neral network for our genome
        net = neat.nn.FeedForwardNetwork.create(g, config)
        # Append the neural network
        nets.append(net)
        # Append the bird
        birds.append(Bird(230, 350))
        # initialize the fitness
        g.fitness = 0
        # Append the genome
        ge.append(g)

    # # Creating the bird
    # bird = Bird(230,350)
    # Creating the base
    base = Base(700)
    # Creating the pipes
    pipes = [Pipe(600)]
    # Setting up the window
    window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))

    # Setting the clock
    clock = pygame.time.Clock()

    # points
    score = 0

    # keep track game is running
    run = True
    # Checks if game is running
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            # QUIT GAME
            if event.type == pygame.QUIT:
                run = False
                # Quits the game
                pygame.quit()
                # exit the window
                quit()

        # pipe index
        pipe_ind = 0
        # Check if there are birds
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()


        add_pipe = False

        rem = []

        for pipe in pipes:
            for x, bird in enumerate(birds):
                # Check if there is collision and remove bird, neural and genome
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # Check if the bird passed the pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # Check if pipe is not on the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            # movement of the pipe
            pipe.move()
        
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
        
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            # Check if the bird hits the floor
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # movement of the base
        base.move()
        # draw the game window
        draw_window(window, birds, pipes, base, score, GEN)



def run(config_path):
    # define all the sub heading in the configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)

    # Gives output 
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # fitness for the bird
    winner = population.run(main,50)

if __name__ == '__main__':
    # Gets the local directory path
    local_dir = os.path.dirname(__file__)
    # Gets the path to the configuration
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)