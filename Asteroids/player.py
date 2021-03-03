from display import gameDisplay
from utils import *
from sounds import *
import math
from bullet import Bullet
from time import time


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hspeed = 0
        self.vspeed = 0
        self.dir = -90
        self.rtspd = 0
        self.thrust = False
        self.is_rapid_firing = False
        self.rapid_fire_rounds = 9
        self.rapid_fire_till = 0  # todo: make this based on the amount of rounds?
        self.matrix_till = 0   # todo: make this based on ticks?  Make this and on/off with M key?
        self.shields = starting_shields
        self.missles = 0
        self.target = None
        self.selected_weapon = BULLETS
        self.invi_dur = 120

    def is_hit_size(self, bullet):
        if self.shields:
            return shields_size + (bullet.size / 2)
        else:
            return player_size + (bullet.size / 2)

    @property
    def has_rapid_fire(self):
        if time() < self.rapid_fire_till:
            return True
        else:
            return False

    def updatePlayer(self, saucers):
        # Move player
        speed = math.sqrt(self.hspeed**2 + self.vspeed**2)
        if self.thrust:
            if speed + fd_fric < player_max_speed:
                self.hspeed += fd_fric * math.cos(self.dir * math.pi / 180)
                self.vspeed += fd_fric * math.sin(self.dir * math.pi / 180)
            else:
                self.hspeed = player_max_speed * math.cos(self.dir * math.pi / 180)
                self.vspeed = player_max_speed * math.sin(self.dir * math.pi / 180)
        else:
            if speed - bd_fric > 0:
                change_in_hspeed = (bd_fric * math.cos(self.vspeed / self.hspeed))
                change_in_vspeed = (bd_fric * math.sin(self.vspeed / self.hspeed))
                if self.hspeed != 0:
                    if change_in_hspeed / abs(change_in_hspeed) == self.hspeed / abs(self.hspeed):
                        self.hspeed -= change_in_hspeed
                    else:
                        self.hspeed += change_in_hspeed
                if self.vspeed != 0:
                    if change_in_vspeed / abs(change_in_vspeed) == self.vspeed / abs(self.vspeed):
                        self.vspeed -= change_in_vspeed
                    else:
                        self.vspeed += change_in_vspeed
            else:
                self.hspeed = 0
                self.vspeed = 0
        self.x += self.hspeed
        self.y += self.vspeed

        wrapper_check(self)

        # Rotate player
        self.dir += self.rtspd
        self.select_missle_target(saucers)

    def select_missle_target(self, saucers):
        if len(saucers):
            angle_differences = [angle_difference(self.dir, self, s) for s in saucers]
            min_ndx = angle_differences.index(min(angle_differences))
            saucer = saucers[min_ndx]
            saucer.color = red
            self.target = saucer
            for s in saucers:
                if s is not saucer:
                    s.color = orange

    def rapidfire(self, bullets):
        self.is_rapid_firing = True

        if self.rapid_fire_rounds % 2:
            self.rapid_fire_rounds -= 1
            return

        if self.rapid_fire_rounds > 0:
            pos_diff = (self.rapid_fire_rounds % 3) * 1.523
            if pos_diff < int(self.rapid_fire_rounds / 2):
                pos_diff = pos_diff * -1
            bullets.append(Bullet(self.x, self.y, self.dir + pos_diff))
            pygame.mixer.Sound.play(snd_fire)
        else:
            self.is_rapid_firing = False
            self.rapid_fire_rounds = 9

        self.rapid_fire_rounds -= 1

    def handle_rapidfire(self, bullets):
        if self.is_rapid_firing:
            self.rapidfire(bullets)

    def drawPlayer(self):
        a = math.radians(self.dir)
        x = self.x
        y = self.y
        s = player_size
        t = self.thrust

        # Draw player
        pygame.draw.line(gameDisplay, white,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(gameDisplay, white,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(gameDisplay, white,
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)))
        if t:
            pygame.draw.line(gameDisplay, white,
                             (x - s * math.cos(a),
                              y - s * math.sin(a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(a + math.pi / 6),
                              y - (s * math.sqrt(5) / 4) * math.sin(a + math.pi / 6)))
            pygame.draw.line(gameDisplay, white,
                             (x - s * math.cos(-a),
                              y + s * math.sin(-a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(-a + math.pi / 6),
                              y + (s * math.sqrt(5) / 4) * math.sin(-a + math.pi / 6)))

        if self.shields:
            pygame.draw.circle(gameDisplay, blue, (int(x), int(y)), shields_size, 1)
            drawText(str(self.shields), blue, int(x + (shields_size / 2) + 12), int(y + (shields_size / 2) + 12), 22)

    def killPlayer(self):
        # Reset the player
        self.x = display_width / 2
        self.y = display_height / 2
        self.thrust = False
        self.dir = -90
        self.hspeed = 0
        self.vspeed = 0
        self.shields = starting_shields

    def handle_collection(self, debris, debris_list):
        debris.collect(self)
        debris_list.remove(debris)
        debris.play_sound()

