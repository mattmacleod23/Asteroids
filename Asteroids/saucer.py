from utils import *
from display import gameDisplay
from sounds import *
import random
from bullet import Bullet
import math


# Create class
saucer_types = ["Small", "Large", "Boss"]
# Create class saucer
class Saucer:
    def __init__(self):
        self.size = 15
        self.score = 10
        self.sound = snd_saucerB
        self.x = 0
        self.y = 0
        self.dirchoice = ()
        self.bullets = safelist()
        self.cd = 0
        self.bdir = 0
        self.soundDelay = 0
        self.fire_frames = 30
        self.is_alive = True
        self.accuracy = small_saucer_accuracy * 2
        self.color = orange
        self.bullet_size = 6
        pygame.mixer.Sound.play(new_saucer)

        # Set random position
        self.x = random.choice((0, display_width))
        self.y = random.randint(0, display_height)

        # Create random direction
        if self.x == 0:
            self.dir = 0
            self.dirchoice = (0, 45, -45)
        else:
            self.dir = 180
            self.dirchoice = (180, 135, -135)

        # Reset bullet cooldown
        self.cd = 40 + random.randint(7, 23)

    def shooting(self):
        if self.cd == 0:
            self.bullets.append(Bullet(self.x, self.y, self.bdir, size=self.bullet_size))
            self.cd = self.fire_frames + random.randint(-4, 4)
        else:
            self.cd -= 1

    def should_die(self, _):
        self.is_alive = False
        return True

    def play_sound(self):
        pass
        # pygame.mixer.Sound.play(self.sound)

    def updateSaucer(self):
        # Move player
        self.x += saucer_speed * math.cos(self.dir * math.pi / 180)
        self.y += saucer_speed * math.sin(self.dir * math.pi / 180)

        # Choose random direction
        if random.randrange(0, 100) == 1:
            self.dir = random.choice(self.dirchoice)

        # Wrapping
        if self.y < 0:
            self.y = display_height
        elif self.y > display_height:
            self.y = 0
        if self.x < 0:
            self.x = display_width
        elif self.x > display_width:
            self.x = 0

        self.play_sound()

    def set_direction(self, stage, player):
        acc = self.accuracy * 4 / stage
        self.bdir = math.degrees(
            math.atan2(-self.y + player.y, -self.x + player.x) + math.radians(random.uniform(acc, -acc)))

    def createSaucer(self):
        pass

    def drawSaucer(self):
        # Draw saucer
        pygame.draw.polygon(gameDisplay, self.color,
                            ((self.x + self.size, self.y),
                             (self.x + self.size / 2, self.y + self.size / 3),
                             (self.x - self.size / 2, self.y + self.size / 3),
                             (self.x - self.size, self.y),
                             (self.x - self.size / 2, self.y - self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)
        pygame.draw.line(gameDisplay, self.color,
                         (self.x - self.size, self.y),
                         (self.x + self.size, self.y))
        pygame.draw.polygon(gameDisplay, self.color,
                            ((self.x - self.size / 2, self.y - self.size / 3),
                             (self.x - self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)


class SmallSaucer(Saucer):
    def __init__(self):
        super().__init__()
        self.score = 1000
        self.size = 10

    def shooting(self):
        super().shooting()


class MediumSaucer(Saucer):
    def __init__(self):
        super().__init__()
        self.score = 420
        self.size = 15


class LargeSaucer(Saucer):
    def __init__(self):
        super().__init__()
        self.score = 200
        self.size = 20

    def shooting(self):
        super().shooting()


class Battleship(Saucer):
    def __init__(self):
        super().__init__()
        self.score = 2500
        self.size = 50
        self.health = 100

    def should_die(self, bullet):
        self.health -= bullet.figure_damage(self)
        if self.health <= 0:
            return True
        else:
            return False

    def drawSaucer(self):
        super().drawSaucer()
        offset = ((self.size / 2) + 2.3)
        drawText(str(self.health), green, self.x + offset, self.y + offset, 20)


class SaucerFactory:
    def __init__(self):
        self.saucer_num = 0

    def __call__(self, stage=1):
        self.saucer_num += 1
        if self.saucer_num % battleship_interval == 0:
            return Battleship()

        if not random.randint(0, 3):
            return LargeSaucer()
        else:
            if not random.randint(0, 3):
                return SmallSaucer()
            else:
                return MediumSaucer()
