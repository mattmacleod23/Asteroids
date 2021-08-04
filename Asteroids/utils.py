import pygame
import math
from constants import *
from display import gameDisplay
import random
import weakref


class TextHandler:
    texts = {}

    def __call__(self, size):
        if size not in self.texts:
            screen_text = pygame.font.SysFont("Calibri", size)
            self.texts[size] = screen_text
            return screen_text
        else:
            return self.texts[size]


class Displayable:
    displayables = []

    def register_displayable(self):
        self.displayables.append(weakref.ref(self))

    def update_display(self):
        pygame.display.update()


text_handler = TextHandler()


# Create function to draw texts
def drawText(msg, color, x, y, s, center=True):
    screen_text = text_handler(s).render(msg, True, color)

    if center:
        rect = screen_text.get_rect()
        rect.center = (x, y)
    else:
        rect = (x, y)
    gameDisplay.blit(screen_text, rect)


# Create funtion to chek for collision
def isColliding(x, y, xTo, yTo, size, r_distance=False):
    if not r_distance:
        if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
            return True
        return False

    else:
        p1 = point(x, y)
        p2 = point(xTo, yTo)
        if real_distance(p1, p2) <= size:
            return True
        return False


def colliding(a, b, size=None):
    if size is None:
        size = max(a.size, b.size)
    return isColliding(a.x, a.y, b.x, b.y, size)


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


def real_distance(a, b):
    return math.sqrt(((a.x - b.x)**2)+((a.y - b.y)**2))


def angle_to(obj, obj2):
    return math.degrees(
        math.atan2(-obj.y + obj2.y, -obj.x + obj2.x))


def angle_difference(dir, obj, obj2):
    right_dir = angle_to(obj, obj2) % 360
    dir = dir % 360
    return min([abs(((right_dir - dir) - 360) % 360), abs(((dir - right_dir) - 360) % 360)])


class point:
    def __init__(self, x, y, size=1):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, color=red):
        pygame.draw.circle(gameDisplay, color, (int(self.x), int(self.y)), 10)


def next_position_in(obj, speed, obj_dir_attr="dir", dir=None):
    if not dir:
        dir = getattr(obj, obj_dir_attr)
    x = obj.x
    y = obj.y
    x += speed * math.cos(dir * math.pi / 180)
    y += speed * math.sin(dir * math.pi / 180)
    return point(x, y)


class safelist(list):
    def remove(self, x, force=False):
        try:
            if hasattr(x, "can_remove") and not force:
                if not x.can_remove():
                    return
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


def draw_debug_info(obj):
    if hasattr(obj, "dbg_data") and args.debug:
        offset = getattr(obj, "size", 5) + 5
        y_off = offset
        for attr in obj.dbg_data:
            if attr == "id":
                drawText(str(id(obj)), white, obj.x + offset, obj.y + y_off, 20)
                continue

            if type(attr) is str:
                a, val = (str(attr), str(getattr(obj, attr)))
            else:
                a, func, arguments = attr
                if args is None:
                    val = func(getattr(obj, a))
                else:
                    val = func(getattr(obj, a, *arguments))

            s = "{}: {}".format(a, val)

            drawText(s, white, obj.x + offset, obj.y + y_off, 20)
            y_off += 20

