from utils import *
from display import gameDisplay
from sounds import *
import random
from bullet import Bullet
from player import Player
import math


# Create class
saucer_types = ["Small", "Large", "Boss"]
# Create class saucer


class Saucer:
    dbg_data = ["speed"]

    def __init__(self, **kwargs):
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
        self.angle_difference = 0
        self.speed = kwargs.get("speed", 5)
        self.shields = 0
        self.shield_recharge_interval = kwargs.get("shield_recharge_interval", 30 * 2)
        self.next_shield_recharge = self.shield_recharge_interval
        play_sound(new_saucer)

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
        self.x += self.speed * math.cos(self.dir * math.pi / 180)
        self.y += self.speed * math.sin(self.dir * math.pi / 180)

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

    def set_smart_bdir(self, player, speed=1):
        dist = real_distance(self, player)
        target_next_position = next_position_in(player, ((player.speed / speed) * (dist / 1500)) * 60, obj_dir_attr="dest_dir")
        target_next_position.draw()
        self.bdir = angle_to(self, target_next_position)

    def createSaucer(self):
        pass

    def drawSaucer(self, player):
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

        if player.missles:
            offset = ((self.size / 2) + 6.623)
            drawText(str(round(self.angle_difference)), red, self.x - offset, self.y - offset, 20)

        if self.shields:
            pygame.draw.circle(gameDisplay, blue, (int(self.x), int(self.y)), self.size * 1.323, 1)
            drawText(str(self.shields), blue, int(self.x + (self.size / 2) + 12), int(self.y + (shields_size / 2) + 12), 22)

        if args.debug:
            draw_debug_info(self)


class SmallSaucer(Saucer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 1000
        self.size = 12

    def shooting(self):
        super().shooting()


class MediumSaucer(Saucer):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.score = 420
        self.size = 15


class LargeSaucer(Saucer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 200
        self.size = 20

    def shooting(self):
        super().shooting()


class Battleship(Saucer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 2500
        self.size = 50
        self.health = 50

    def should_die(self, bullet):
        self.health -= bullet.figure_damage(self)
        if self.health <= 0:
            return True
        else:
            return False

    def drawSaucer(self, player):
        super().drawSaucer(player)
        offset = ((self.size / 2) + 2.3)
        drawText(str(self.health), green, self.x + offset, self.y + offset, 20)


blast_wind_up = 45
blaster_size = 25
blaster_speed = 3  # ratio


class Boss(Battleship):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 5000
        self.size = 120
        self.health = 200 + max((kwargs.get("stage", 5) - 5) * 100, 0)
        self.max_shields = kwargs.get("max_shields", 20)
        self.shields = self.max_shields
        self.blaster_interval = 30 * kwargs.get("next_blaster_in", 6.5)
        self.next_blaster_in = self.blaster_interval
        self.blast_in = blast_wind_up

    def shooting(self):
        if self.cd == 0:
            self.cd = random.randint(6, 10)
            if random.randint(0, 1):
                cannon = 60
            else:
                cannon = -60
            self.bullets.append(Bullet(self.x + cannon, self.y, self.bdir, size=self.bullet_size))
        else:
            self.cd -= 1

        self.next_blaster_in -= 1

        if self.next_blaster_in <= 0 and not random.randint(0, 7) and self.blast_in == blast_wind_up:
            self.blast_in -= 1
            self.next_blaster_in = self.blaster_interval
            play_sound(blast_charge, maxtime=int(blast_wind_up / 30) * 1823)

        if self.blast_in < blast_wind_up:
            self.blast_in -= 1

        if self.blast_in == 0:
            self.set_smart_bdir(Player.player, speed=blaster_speed)
            self.bullets.append(Bullet(self.x, self.y, self.bdir, size=blaster_size,
                                       color=purple, speed=bullet_speed * blaster_speed,
                                       life=bullet_life / blaster_speed, growth_rate=.423, damage=3))
            play_sound(blast)
            self.blast_in = blast_wind_up

    def should_die(self, bullet):
        if self.shields:
            self.shields -= int(bullet.damage / 10)
            play_sound(zap)
        else:
            return super().should_die(bullet)

    def updateSaucer(self):
        super().updateSaucer()
        self.next_shield_recharge -= 1
        if self.shields and self.shields < self.max_shields:
            if self.next_shield_recharge <= 0:
                self.shields += 1
                self.next_shield_recharge = self.shield_recharge_interval


class SaucerFactory:
    def __init__(self):
        self.saucer_num = 0

    def __call__(self, stage=1):
        if stage > 1:
            speed = 5
        else:
            change = int(random.randint(stage - 2, stage + 4) / 2)
            speed = 5 + change

        self.saucer_num += 1

        if self.saucer_num % battleship_interval == 0:
            return Battleship(speed=speed)

        if not random.randint(0, 3):
            return LargeSaucer(speed=speed)
        else:
            if not random.randint(0, 3):
                return SmallSaucer(speed=speed)
            else:
                return MediumSaucer(speed=speed)

