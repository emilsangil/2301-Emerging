import pygame
import os
#  Const for the window width and height for the game
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