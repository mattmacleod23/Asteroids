from sounds import *
from utils import *
import random
from time import time


# Create class for shattered ship
class BonusDebris:
    sound = snd_extra

    def __init__(self, x, y, l=saucer_debris_size, **kwargs):
        self.angle = random.randrange(0, 360) * math.pi / 180
        self.dir = random.randrange(0, 360) * math.pi / 180
        self.rtspd = random.uniform(-0.25, 0.25)
        self.x = x
        self.y = y
        self.lenght = l
        self.size = l
        self.speed = random.randint(2, 3)
        self.color = white
        self.life = 323

        # Make random asteroid sprites
        full_circle = random.uniform(18, 36)
        dist = random.uniform(self.size / 2, self.size)
        self.vertices = []
        while full_circle < 360:
            self.vertices.append([dist, full_circle])
            dist = random.uniform(self.size / 4, self.size)
            full_circle += random.uniform(23, 36)

    @classmethod
    def play_sound(cls):
        pygame.mixer.Sound.play(cls.sound, 3)

    def updateDebris(self, saucer_debris):
        for v in range(len(self.vertices)):
            if v == len(self.vertices) - 1:
                next_v = self.vertices[0]
            else:
                next_v = self.vertices[v + 1]
            this_v = self.vertices[v]
            pygame.draw.line(gameDisplay, self.color, (self.x + this_v[0] * math.cos(this_v[1] * math.pi / 180),
                              self.y + this_v[0] * math.sin(this_v[1] * math.pi / 180)),
                             (self.x + next_v[0] * math.cos(next_v[1] * math.pi / 180),
                              self.y + next_v[0] * math.sin(next_v[1] * math.pi / 180)))
        self.angle += self.rtspd
        self.x += self.speed * math.cos(self.dir)
        self.y += self.speed * math.sin(self.dir)

        wrapper_check(self)

        self.life -= 1
        if not self.life:
            saucer_debris.remove(self)


class MatrixDebris(BonusDebris):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = green

    def collect(self, player):
        if player.matrix_till > time():
            player.matrix_till += matrix_duration
        else:
            player.matrix_till = time() + matrix_duration


class RapidFireDebris(BonusDebris):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = red

    def collect(self, player):
        if player.rapid_fire_till > time():
            player.rapid_fire_till += matrix_duration
        else:
            player.rapid_fire_till = time() + matrix_duration


class ShieldDebris(BonusDebris):
    def __init__(self, *args, value=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = blue
        self.value = value

    def collect(self, player):
        player.shields += self.value


class MissleDebris(BonusDebris):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = orange

    def collect(self, player):
        player.missles += 5


class SaucerDebrisFactory:
    debris_types = [MatrixDebris, RapidFireDebris, ShieldDebris]

    def __call__(self, *args, **kwargs):
        if random.randint(0, 15) == 1:
            return MissleDebris(*args, **kwargs)
        i = random.randint(0, len(self.debris_types) - 1)
        return self.debris_types[i](*args, **kwargs)

