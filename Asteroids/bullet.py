from display import gameDisplay
from utils import *


class Bullet:
    def __init__(self, x, y, direction, size=3, color=red):
        self.x = x
        self.y = y
        self.dir = direction
        self.life = 57
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


class Missle(Bullet):
    def __init__(self, *args, color=orange, saucer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = saucer
        self.current_correction = .05
        self.color = color

    def draw(self):
        pygame.draw.circle(gameDisplay, self.color, (int(self.x), int(self.y)), self.size)

    def find_max_correction(self, saucer):
        dist = distance(self, saucer)
        if dist < 700:
            max_correction = max((700 - dist) / 1000, .5023)
            self.current_correction += (max_correction * 1.0023)
            return max(self.current_correction, 6)

        if self.life % 2:
            return .023
        else:
            return 0

    def correct_direction(self):
        dist = distance(self, self.target)
        target_next_position = next_position_in(self.target, saucer_speed * (dist / 1500) * 60)
        target_next_position.draw()
        saucer_destination_angle = angle_to(self, target_next_position)
        max_correction = self.find_max_correction(target_next_position)

        angle_diff = abs(saucer_destination_angle - self.dir) % 180

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


class collectorBullet(Bullet):
    def updateBullet(self):
        self.x += bullet_speed * math.cos(self.dir * math.pi / 180)
        self.y += bullet_speed * math.sin(self.dir * math.pi / 180)

        if self.life % 6 != 1:
            self.size += 1

        pygame.draw.circle(gameDisplay, self.color, (int(self.x), int(self.y)), self.size)
        wrapper_check(self)

        self.life -= 1

