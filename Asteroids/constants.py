import pygame
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-sw", "--width", required=False, type=int, default=2500)
parser.add_argument("-sh", "--height", required=False, type=int, default=1400)
parser.add_argument("-ss", "--starting_shields", type=int, default=4)
parser.add_argument("-sm", "--starting_missles", type=int, default=0)
args, _ = parser.parse_known_args()

# Initialize constants
white = (255, 255, 255)
red = (255, 0, 0)
blue = (3, 65, 252)
green = (124, 252, 0)
black = (0, 0, 0)
orange = (255, 131, 0)
yellow = (255, 216, 110)

display_width = args.width
display_height = args.height

player_size = 10
saucer_debris_size = 15
fd_fric = 0.5
bd_fric = 0.1
player_max_speed = 20
player_max_rtspd = 10
bullet_speed = 15
saucer_speed = 5
small_saucer_accuracy = 10
matrix_duration = 10
shields_size = 20
starting_shields = 4
max_saucers = 4
battleship_interval = 8

BULLETS = 1
RAPID_FIRE = 2
MISSLES = 3
NUKE = 4

MISSLES_BTN = pygame.K_m
RAPIDFIRE_BTN = pygame.K_DOWN


