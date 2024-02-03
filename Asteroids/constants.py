import pygame
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-sw", "--width", required=False, type=int, default=2500)
parser.add_argument("-sh", "--height", required=False, type=int, default=1600)
parser.add_argument("-ss", "--starting_shields", type=int, default=4)
parser.add_argument("-sm", "--starting_missles", type=int, default=0)
parser.add_argument("-sn", "--starting_nukes", type=int, default=0)
parser.add_argument("-ms", "--max_saucers", type=int, default=4)
parser.add_argument("-d", "--debug", help="Runs slower so its easier to debug shit", default=0, type=int)
parser.add_argument("-fm", "--finesse_multiplier", type=float, default=1)

args, _ = parser.parse_known_args()

# Initialize constants
white = (255, 255, 255)
red = (255, 0, 0)
blue = (3, 65, 252)
green = (124, 252, 0)
black = (0, 0, 0)
orange = (255, 131, 0)
yellow = (255, 216, 110)
light_green = (185, 250, 208)
purple = (182, 3, 252)

display_width = args.width
display_height = args.height

x = round(display_width / 1400, 2) * 64
bullet_life = round(x)

player_size = 10
saucer_debris_size = 23
fd_fric = 0.5
bd_fric = 0.1
player_max_speed = 20
player_max_rtspd = 10
bullet_speed = 15
saucer_speed = 5
small_saucer_accuracy = 10
matrix_duration = 10
shields_size = 20
saucer_shield_size = 1.323  # ratio
starting_shields = 4
max_saucers = args.max_saucers
battleship_interval = 8
bullet_capacity = 20
saucers_per_stage = 8
BULLETS = 1
RAPID_FIRE = 2
MISSLES = 3
NUKES = 4
weapons = {BULLETS: None, RAPID_FIRE: "rapid_fire_count", MISSLES: "missles", NUKES: "nukes"}

MISSLES_BTN = pygame.K_m
RAPIDFIRE_BTN = pygame.K_DOWN


