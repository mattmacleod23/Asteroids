from display import gameDisplay
from utils import *
from sounds import *
from constants import *


x = round(display_width / 1400, 2) * 64
bullet_life = round(x)


class Bullet:
    def __init__(self, x, y, direction, size=3, color=red):
        self.x = x
        self.y = y
        self.dir = direction
        self.life = bullet_life
        self.size = size
        self.color = color
        self.damage = 10

    def draw(self):
        pygame.draw.circle(gameDisplay, self.color, (int(self.x), int(self.y)), self.size)

    def updateBullet(self):
        self.x += bullet_speed * math.cos(self.dir * math.pi / 180)
        self.y += bullet_speed * math.sin(self.dir * math.pi / 180)
        self.draw()
        wrapper_check(self)

        self.life -= 1

    def figure_damage(self, saucer):
        return self.damage

    def handle_collision(self, saucer):
        self.life = 0

    def should_kill(self, saucer):
        if isColliding(self.x, self.y, saucer.x, saucer.y, (saucer.size / 2) + self.size):
            self.handle_collision(saucer)
            play_sound(snd_bangL)
            if saucer.should_die(self):
                return True

    def can_remove(self):
        return self.life <= 0


class Missle(Bullet):
    dbg_data = [("dir", round, (2,)), ("saucer_destination", round, (2,))]

    def __init__(self, *args, color=orange, saucer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = saucer
        self.current_correction = .05
        self.color = color
        self.saucer_destination = 0

    def draw(self):
        pygame.draw.circle(gameDisplay, self.color, (int(self.x), int(self.y)), self.size)
        draw_debug_info(self)

    def find_max_correction(self, saucer):
        dist = distance(self, saucer)
        if dist < 1100:
            max_correction = max((700 - dist) / 1000, .82323)
            self.current_correction += (max_correction * 1.0032323)
            if dist < 100:
                self.current_correction += .023
            return max(self.current_correction, 8.23)

        if self.life % 2:
            return .02323
        else:
            return 0

    def correct_direction(self):
        dist = distance(self, self.target)
        target_next_position = next_position_in(self.target, self.target.speed * (dist / 1500) * 60)
        target_next_position.draw()
        saucer_destination_angle = angle_to(self, target_next_position)
        self.saucer_destination = saucer_destination_angle
        max_correction = self.find_max_correction(target_next_position)

        angle_diff = abs(saucer_destination_angle - self.dir)

        change = min(angle_diff, max_correction)

        adding_angle = self.dir + change
        sub_angle = self.dir - change

        adding_angle_diff = abs((adding_angle % 360) - (saucer_destination_angle % 360))
        sub_angle_diff = abs((sub_angle % 360) - (saucer_destination_angle % 360))

        if adding_angle_diff > sub_angle_diff:
            self.dir = sub_angle
        else:
            self.dir = adding_angle

    def updateBullet(self):
        super().updateBullet()
        if self.target:
            if self.life % 3 == 1:
                self.correct_direction()


nuke_life = 23


class Nuke(Bullet):
    dbg_data = ["kill_distance", "blow_up_life"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = light_green
        self.size = 6
        self.blow_up_life = nuke_life
        self.is_blowing_up = False
        self.blow_up_speed = 12
        self.blow_up_distance = 140
        self.kill_distance = 0

    def blow_up(self):
        self.is_blowing_up = True

    def handle_explosion(self, saucers, player):
        self.blow_up_life -= 1
        self.size += 20.23

    def updateBullet(self):
        if not self.is_blowing_up:
            super().updateBullet()
        else:
            self.draw()

    def draw(self):
        if self.is_blowing_up:
            size = int(self.size)
            for i in range(0, int(self.size * 3.523)):
                x_offset = random.randint(size * -1, size)
                y_offset = random.randint(size * -1, size)
                x = self.x + x_offset
                y = self.y + y_offset
                l = random.randint(-17, 17)
                l2 = random.randint(-17, 17)
                if real_distance(self, point(x, y)) < size:
                    c = (random.randint(135, 255), random.randint(0, 196), random.randint(0, 10))
                    pygame.draw.line(gameDisplay, c, (int(x), int(y)), (int(x) - l, int(y - l2)), 6)

        else:
            super().draw()
        draw_debug_info(self)

    def can_remove(self):
        if self.blow_up_life <= 0:
            return True
        else:
            return False


class collectorBullet(Bullet):
    def updateBullet(self):
        self.x += bullet_speed * math.cos(self.dir * math.pi / 180)
        self.y += bullet_speed * math.sin(self.dir * math.pi / 180)

        if self.life % 6 == 1:
            self.size += 1

        pygame.draw.circle(gameDisplay, self.color, (int(self.x), int(self.y)), self.size)
        wrapper_check(self)

        self.life -= 1

