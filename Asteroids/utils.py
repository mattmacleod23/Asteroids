import pygame
import math
from constants import *
from display import gameDisplay
import random


# Create function to draw texts
def drawText(msg, color, x, y, s, center=True):
    screen_text = pygame.font.SysFont("Calibri", s).render(msg, True, color)
    if center:
        rect = screen_text.get_rect()
        rect.center = (x, y)
    else:
        rect = (x, y)
    gameDisplay.blit(screen_text, rect)


# Create funtion to chek for collision
def isColliding(x, y, xTo, yTo, size):
    if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
        return True
    return False


def wrapper_check(obj):
    if obj.x > display_width:
        obj.x = 0
    elif obj.x < 0:
        obj.x = display_width
    elif obj.y > display_height:
        obj.y = 0
    elif obj.y < 0:
        obj.y = display_height


def distance(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


def angle_to(obj, obj2):
    return math.degrees(
        math.atan2(-obj.y + obj2.y, -obj.x + obj2.x))


def angle_difference(dir, obj, obj2):
    right_dir = angle_to(obj, obj2) % 360
    dir = dir % 360
    return min([abs(((right_dir - dir) - 360) % 360), abs(((dir - right_dir) - 360) % 360)])


class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.circle(gameDisplay, red, (int(self.x), int(self.y)), 10)


def next_position_in(obj, speed):
    x = obj.x
    y = obj.y
    x += speed * math.cos(obj.dir * math.pi / 180)
    y += speed * math.sin(obj.dir * math.pi / 180)
    return point(x, y)


class safelist(list):
    def remove(self, x):
        try:
            super().remove(x)
        except:
            pass


# Create class for shattered ship
class deadPlayer:
    def __init__(self, x, y, l):
        self.angle = random.randrange(0, 360) * math.pi / 180
        self.dir = random.randrange(0, 360) * math.pi / 180
        self.rtspd = random.uniform(-0.25, 0.25)
        self.x = x
        self.y = y
        self.lenght = l
        self.speed = random.randint(2, 8)

    def updateDeadPlayer(self):
        pygame.draw.line(gameDisplay, white,
                         (self.x + self.lenght * math.cos(self.angle) / 2,
                          self.y + self.lenght * math.sin(self.angle) / 2),
                         (self.x - self.lenght * math.cos(self.angle) / 2,
                          self.y - self.lenght * math.sin(self.angle) / 2))
        self.angle += self.rtspd
        self.x += self.speed * math.cos(self.dir)
        self.y += self.speed * math.sin(self.dir)


def blowUp(obj, player_pieces):
    player_pieces.append(deadPlayer(obj.x, obj.y, 3 / (2 * math.cos(math.atan(1 / 3)))))
    player_pieces.append(deadPlayer(obj.x, obj.y, 3 * player_size / (2 * math.cos(math.atan(1 / 3)))))
    player_pieces.append(
        deadPlayer(obj.x, obj.y, 2 * player_size / (2 * math.cos(math.atan(1 / 3)))))
    player_pieces.append(deadPlayer(obj.x, obj.y, player_size))
    player_pieces.append(deadPlayer(obj.x, obj.y, 2.23))

