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


no_dir_change_time = 50


class Saucer(Displayable):
    dbg_data = ["speed"]
    shields_size = 1.323

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
        self.shields = kwargs.get("shields", 0)
        self.had_shields = True if self.shields else False
        self.shield_recharge_interval = kwargs.get("shield_recharge_interval", 30 * 2)
        self.next_shield_recharge = self.shield_recharge_interval
        self.dodge_bullet_range = kwargs.get("dodge_bullet_range", 0)
        self.finesse = int(kwargs.get("finesse", 0) * args.finesse_multiplier)  # dodging ability
        self.dont_change_dir = no_dir_change_time
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
        self.register_displayable()

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

    def updateSaucer(self, bullets):
        # Move player
        self.x += self.speed * math.cos(self.dir * math.pi / 180)
        self.y += self.speed * math.sin(self.dir * math.pi / 180)

        # Choose random direction
        if random.randrange(0, 100) == 1 and self.dont_change_dir <= 0:
            self.dir = random.choice(self.dirchoice)

        if self.dont_change_dir > 0:
            self.dont_change_dir -= 1

        # Wrapping
        if self.y < 0:
            self.y = display_height
        elif self.y > display_height:
            self.y = 0
        if self.x < 0:
            self.x = display_width
        elif self.x > display_width:
            self.x = 0

        chance = min(300 - self.finesse, 300)

        if chance < 1:
            chance = 1

        if self.finesse and not random.randint(0, chance):
            self.dodge(bullets)

        self.play_sound()

    def set_direction(self, stage, player):
        acc = (self.accuracy * 4) / (stage + 4)
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

        if player.selected_weapon == MISSLES:
            offset = ((self.size / 2) + 6.623)
            drawText(str(round(self.angle_difference)), red, self.x - offset, self.y - offset, 20)

        if self.shields > 0:
            self.had_shields = True
            pygame.draw.circle(gameDisplay, blue, (int(self.x), int(self.y)), self.size * 1.323, 1)
            drawText(str(self.shields), blue, int(self.x + (shields_size / 2) + 20), int(self.y + (shields_size / 2) + 20), 22)
        else:
            self.had_shields = False

        if args.debug:
            draw_debug_info(self)

    def dodge(self, bullets):
        dodgeables = []
        time_to_impact = 0

        for b in bullets:
            dist = real_distance(self, b)
            relative_speed = math.hypot(
                self.speed * math.cos(math.radians(self.dir)) - b.speed * math.cos(math.radians(b.dir)),
                self.speed * math.sin(math.radians(self.dir)) - b.speed * math.sin(math.radians(b.dir)))
            time_to_impact = dist / relative_speed if relative_speed != 0 else float('inf')
            saucer_next_position = next_position_in(self, self.speed * time_to_impact)
            if dist < self.dodge_bullet_range:
                next_b = next_position_in(b, b.speed * time_to_impact)
                if colliding(next_b, saucer_next_position, size=self.size):
                    dodgeables.append((b, dist, next_b, saucer_next_position))

        if len(dodgeables):
            best_angle = None
            min_bullet_density = float('inf')
            for angle in range(0, 359, 7):
                collision = False
                bullet_density = 0
                for b, dist, b_next_pos, saucer_next_position in dodgeables:
                    next_pos = next_position_in(self, self.speed * time_to_impact, dir=angle)

                    if colliding(b_next_pos, next_pos, size=self.size * 1.5):
                        collision = True
                        break

                    # Calculate bullet density in the vicinity
                    bullet_density += 1 / (real_distance(next_pos, b_next_pos) + 1)

                if not collision and bullet_density < min_bullet_density:
                    min_bullet_density = bullet_density
                    best_angle = angle

            if best_angle is not None:
                self.dir = best_angle
                self.dont_change_dir = no_dir_change_time
                return

    @property
    def display_size(self):
        if self.had_shields:
            return self.size * 2.5
        else:
            return self.size * 1.7


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
        self.health = kwargs.get("health", 80)
        self.shields = kwargs.get("shields", 20)
        self.max_shields = self.shields
        self.shield_recharge_interval = kwargs.get("shield_recharge_interval", 30 * 2)

    def should_die(self, bullet):
        if self.shields > 0:
            self.shields -= int(bullet.damage / 10)
            play_sound(zap)
        else:
            self.health -= bullet.figure_damage(self)
            if self.health <= 0:
                return True
            else:
                return False

    def drawSaucer(self, player):
        super().drawSaucer(player)
        offset = ((self.size / 2) + 2.3)
        drawText(str(self.health), green, self.x + offset, self.y + offset, 20)

    def updateSaucer(self, bullets):
        super().updateSaucer(bullets)
        self.next_shield_recharge -= 1
        if self.shields and self.shields < self.max_shields:
            if self.next_shield_recharge <= 0:
                self.shields += 1
                self.next_shield_recharge = self.shield_recharge_interval


blast_wind_up = 47
blaster_size = 23
blaster_speed = 2.523  # ratio


class Boss(Battleship):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        stage = kwargs.get("stage", 5)
        self.score = 5000
        self.size = 120
        self.health = 200 + max(stage * 50, 0)
        self.max_shields = kwargs.get("max_shields", 10 * stage)
        self.shields = self.max_shields
        self.blaster_interval = 30 * kwargs.get("next_blaster_in", 6.5)
        self.next_blaster_in = self.blaster_interval
        self.blast_in = blast_wind_up
        self.smart_aim_chance = kwargs.get("smart_aim_chance", 10)

    def shooting(self):
        if self.cd == 0:
            self.cd = random.randint(6, 10)
            if random.randint(0, 1):
                cannon = 60
            else:
                cannon = -60

            if not random.randint(0, self.smart_aim_chance):
                self.set_smart_bdir(Player.player)

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
        if self.shields > 0:
            self.shields -= int(bullet.damage / 10)
            play_sound(zap)
        else:
            return super().should_die(bullet)


class Sniper(Battleship):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 1500
        self.size = 30
        self.accuracy = 0.95  # Higher accuracy for sniper
        self.shields = kwargs.get("shields", 10)
        self.shield_recharge_interval = 30 * 2
        self.bullet_speed = 1.23

    def set_smart_bdir(self, player, bullet_speed):
        # Calculate the distance between the sniper and the player
        dist = real_distance(self, player)

        # Calculate the time it will take for the bullet to reach the player
        time_to_reach = dist / bullet_speed

        # Calculate the future position of the player
        future_x = player.x + player.hspeed * time_to_reach
        future_y = player.y + player.vspeed * time_to_reach

        # Calculate the angle to the future position
        self.bdir = math.degrees(math.atan2(future_y - self.y, future_x - self.x))

    def shooting(self):
        if self.cd == 0:
            self.set_smart_bdir(Player.player, bullet_speed * self.bullet_speed)
            self.bullets.append(Bullet(self.x, self.y, self.bdir, size=self.bullet_size, speed=bullet_speed * self.bullet_speed))
            self.cd = self.fire_frames + random.randint(-4, 4)
        else:
            self.cd -= 1


class SaucerFactory:
    def __init__(self, difficulty=1):
        self.saucer_num = 0
        self.difficulty = difficulty

    def __call__(self, stage=1):
        if stage < 1:
            speed = 5 * self.difficulty
        else:
            change = int(random.randint(stage, stage + 6) / 2 * self.difficulty)
            speed = 5 + change

        self.saucer_num += 1

        if stage > 3 and self.saucer_num % 12 == 0:
            return Sniper(speed=speed, finesse=(stage * 2 * self.difficulty))

        if self.saucer_num % battleship_interval == 0:
            finesse = int(min((stage * 5) + 10 * self.difficulty, 100))
            return Battleship(speed=speed, finesse=finesse, dodge_bullet_range=700)

        if not random.randint(0, 3):
            return LargeSaucer(speed=speed, finesse=0 if stage < 3 else (stage * 2 * self.difficulty))
        else:
            if not random.randint(0, 3):
                return SmallSaucer(speed=speed, finesse=stage + 2)
            else:
                return MediumSaucer(speed=speed)

