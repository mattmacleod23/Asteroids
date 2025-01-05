# Import modules
from argparse import ArgumentParser
from powerups import *
from player import *
from bullet import *
from saucer import *
from asteroid import *
from time import time
import psutil
import os



# set priority
p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)
#affinity_mask = {0, 1}
#os.sched_setaffinity(0, affinity_mask)


pygame.init()

pygame.display.set_caption("Roid Rage")
timer = pygame.time.Clock()

# seeking missle
# purple laser
# shotgun blast
# multiple saucers
# health
# collector shots to pick up matrix
# battleship
# rapid shoot stream ability
# shields
# boss with health
# calling for backup
# make the powerups blink before eol
# make side movements
# make lists iterable safe so loops dont get confused if something is removed during a loop
# freeze everything
# make a saucer that shoots at a quicker interval
# make a saucer that shoots some kind of nuke like thing or "frag" type thing





# Game menu
difficulty_levels = {
    "Easy": 0.07,
    "Normal": 1.0,
    "Hard": 1.3
}


def menu(selected_difficulty):
    gameState = "Menu"
    difficulties = ["Easy", "Normal", "Hard"]
    selected_index = difficulties.index(selected_difficulty)

    gameDisplay.fill(black)
    drawText("ROID RAGE", white, display_width / 2, display_height / 2, 100)
    drawText("Press SPACE to START", white, display_width / 2, display_height / 2 + 100, 50)

    for i, difficulty in enumerate(difficulties):
        color = white
        if i == selected_index:
            pygame.draw.rect(gameDisplay, white,
                             (display_width / 2 - 150, display_height / 2 + 200 + i * 50 - 25, 300, 50), 2)
        drawText(f"{difficulty}", color, display_width / 2, display_height / 2 + 200 + i * 50, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameState = "Exit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(difficulties)
            elif event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(difficulties)
            elif event.key == pygame.K_SPACE:
                gameState = "Playing"

    selected_difficulty = difficulties[selected_index]
    pygame.display.update()
    timer.tick_busy_loop(30)

    return gameState, difficulty_levels.get(selected_difficulty), selected_difficulty


class Game:
    def __init__(self, startingState):
        self.gameState = startingState
        self.player_state = "Alive"
        self.player_blink = 0
        self.player_pieces = safelist()
        self.saucer_debris = safelist()
        self.player_dying_delay = 0
        self.hyperspace = 0
        self.delay_between_levels = 45
        self.next_level_delay = self.delay_between_levels
        self.bullets = safelist()
        self.collector_bullets = safelist()
        self.asteroids = safelist()
        self.stage = 1
        self.score = 0
        self.live = 2
        self.oneUp_multiplier = 1
        self.playOneUpSFX = 0
        self.intensity = 0
        self.min_asteroids = 4
        self.saucers_this_stage = saucers_per_stage - 3  # we start with 3
        self.new_saucer_interval = 9 * 30
        self.new_saucer_time = self.new_saucer_interval
        self.difficulty, self.selected_difficulty = 1, "Normal"
        self.saucer_factory = None
        self.debris_factory = None
        self.player = None
        self.saucers = None
        self.i = 0

    def initialize_game(self):
        while self.gameState == "Menu":
            self.gameState, self.difficulty, self.selected_difficulty = menu(self.selected_difficulty)

        gameDisplay.fill(black)
        pygame.display.update()

        self.saucer_factory = SaucerFactory(difficulty=self.difficulty)
        self.debris_factory = SaucerDebrisFactory()

        self.player = Player(display_width / 2, display_height / 2)
        Player.player = self.player

        self.saucers = safelist([self.saucer_factory() for _ in range(0, 0)])
        self.saucers.append(Battleship(dodge_bullet_range=700, health=100, finesse=20))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameState = "Exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.thrust = True

                if event.key == pygame.K_LEFT:
                    self.player.rtspd = -player_max_rtspd

                if event.key == pygame.K_RIGHT:
                    self.player.rtspd = player_max_rtspd

                if event.key == pygame.K_SPACE and self.player_dying_delay == 0 \
                        and (len(self.bullets) < bullet_capacity or self.player.selected_weapon == RAPID_FIRE):
                    self.player.fire_weapon(self.bullets)

                if event.key == pygame.K_c and self.player_dying_delay == 0 and len(self.bullets) < bullet_capacity:
                    self.collector_bullets.append(
                        collectorBullet(self.player.x, self.player.y, self.player.dir, color=blue))
                    play_sound(snd_fire)

                if event.key == pygame.K_DOWN:
                    while 1:
                        self.player.selected_weapon += 1
                        if self.player.selected_weapon > len(weapons):
                            self.player.selected_weapon = BULLETS
                            break

                        if getattr(self.player, weapons[self.player.selected_weapon]) > 0:
                            self.player.selected_weapon = self.player.selected_weapon
                            self.player.draw_selected_weapon_time = 15
                            break

                if self.gameState == "Game Over":
                    if event.key == pygame.K_r:
                        self.gameState = "Exit"
                        self.game_loop()

                if event.key == pygame.K_p:
                    if self.gameState == "Playing":
                        self.gameState = "Paused"
                    else:
                        self.gameState = "Playing"

                if event.key == pygame.K_LSHIFT:
                    self.hyperspace = 30

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.thrust = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.player.rtspd = 0

        return self.gameState, self.hyperspace

    def handle_user_inputs(self):
        self.gameState, self.hyperspace = self.handle_events()
        if self.gameState == "Paused":
            timer.tick_busy_loop(5)
            return False
        return True

    def update_player(self):
        self.player.updatePlayer(self.saucers)
        if self.player.invi_dur != 0:
            self.player.invi_dur -= 1
        elif self.hyperspace == 0:
            self.player_state = "Alive"

    def reset_display(self):
        gameDisplay.fill(black)

    def handle_hyperspace(self):
        if self.hyperspace != 0:
            self.player_state = "Died"
            self.hyperspace -= 1
            if self.hyperspace == 1:
                self.player.x = random.randrange(0, display_width)
                self.player.y = random.randrange(0, display_height)

    def check_collisions_with_asteroids(self):
        for a in self.asteroids:
            a.updateAsteroid()
            if self.player_state != "Died":
                if isColliding(self.player.x, self.player.y, a.x, a.y, a.size):
                    if self.player.shields > 1:
                        self.player.shields -= 2
                        play_sound(zap)
                    else:
                        self.player_state = "Died"
                        self.player_dying_delay = 30
                        self.player.invi_dur = 120
                        self.player.killPlayer()
                        blowUp(self.player, self.player_pieces)

                        if self.live != 0:
                            self.live -= 1
                        else:
                            self.gameState = "Game Over"

                    if a.t == "Large":
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.score += 20
                        play_sound(snd_bangL)
                    elif a.t == "Normal":
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.score += 50
                        play_sound(snd_bangM)
                    else:
                        self.score += 100
                        play_sound(snd_bangS)
                    self.asteroids.remove(a)

    def update_ship_fragments(self):
        for f in list(self.player_pieces):
            f.updateDeadPlayer()
            if f.x > display_width or f.x < 0 or f.y > display_height or f.y < 0:
                self.player_pieces.remove(f)
            if f.life <= 0:
                self.player_pieces.remove(f)

        for f in self.saucer_debris:
            f.updateDebris(self.saucer_debris)

    def check_end_of_stage(self):
        if len(self.asteroids) < self.min_asteroids and len(self.saucers) == 0 and self.saucers_this_stage <= 0:
            if self.next_level_delay > 0:
                self.next_level_delay -= 1
            else:
                self.stage += 1
                self.intensity = 0
                while len(self.asteroids) < self.min_asteroids:
                    xTo = display_width / 2
                    yTo = display_height / 2
                    while xTo - display_width / 2 < display_width / 4 and yTo - display_height / 2 < display_height / 4:
                        xTo = random.randrange(0, display_width)
                        yTo = random.randrange(0, display_height)

                        self.asteroids.append(Asteroid(xTo, yTo, "Large"))

                self.next_level_delay = self.delay_between_levels
                self.saucers_this_stage = saucers_per_stage + int((self.stage * 2) / 2)
                self.min_asteroids += 2

    def update_intensity(self):
        if self.intensity < self.stage * 450:
            self.intensity += 1

    def handle_saucers(self):
        self.new_saucer_time -= 1
        if random.randint(0, 3500) <= (self.intensity * 2) / (self.stage * 9) and self.next_level_delay == self.delay_between_levels \
                and len(self.saucers) < max_saucers and self.saucers_this_stage and self.new_saucer_time < 0:
            self.new_saucer_time = self.new_saucer_interval

            if self.saucers_this_stage > 1:
                self.saucers_this_stage -= 1
                self.saucers.append(self.saucer_factory(stage=self.stage))
            else:
                if len(self.saucers) == 0:
                    self.saucers_this_stage -= 1
                    self.saucers.append(Boss(stage=self.stage))
        else:
            for saucer in self.saucers:
                saucer.set_direction(self.stage, self.player)
                saucer.updateSaucer(self.bullets)
                saucer.drawSaucer(self.player)
                saucer.shooting()

                for b in self.bullets:
                    if b.should_kill(saucer):
                        self.score += saucer.score
                        saucer.is_alive = False
                        self.saucer_debris.append(self.debris_factory(saucer.x, saucer.y, saucer=saucer))
                        self.saucer_debris.append(self.debris_factory(saucer.x, saucer.y, saucer=saucer))
                        self.saucer_debris.append(self.debris_factory(saucer.x, saucer.y, saucer=saucer))
                        self.bullets.remove(b)

                if isColliding(saucer.x, saucer.y, self.player.x, self.player.y, saucer.size):
                    if self.player_state != "Died":
                        if self.player.shields >= 5 and type(saucer) not in (Battleship, Boss):
                            self.player.shields -= 5
                            blowUp(saucer, self.player_pieces)
                            saucer.is_alive = False
                        else:
                            blowUp(saucer, self.player_pieces)
                            self.player_state = "Died"
                            self.player_dying_delay = 30
                            self.player.invi_dur = 120
                            self.player.killPlayer()

                            if self.live != 0:
                                self.live -= 1
                            else:
                                self.gameState = "Game Over"
                        play_sound(snd_bangL)

                for b in saucer.bullets:
                    b.updateBullet()
                    for a in self.asteroids:
                        if isColliding(b.x, b.y, a.x, a.y, a.size):
                            if a.t == "Large":
                                self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                                self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                                play_sound(snd_bangL)
                            elif a.t == "Normal":
                                self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                                self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                                play_sound(snd_bangL)
                            else:
                                play_sound(snd_bangL)
                            self.asteroids.remove(a)
                            saucer.bullets.remove(b)
                            break

                    if isColliding(self.player.x, self.player.y, b.x, b.y, self.player.is_hit_size(b)):
                        if self.player_state != "Died":
                            if self.player.shields > 0:
                                self.player.shields = int(max(self.player.shields - (b.damage / 10), 0))
                                play_sound(zap)
                                saucer.bullets.remove(b, force=True)
                                continue
                            blowUp(self.player, self.player_pieces)
                            self.player.shields = 0
                            self.player_state = "Died"
                            self.player_dying_delay = 30
                            self.player.invi_dur = 120
                            self.player.killPlayer()

                            if self.live != 0:
                                self.live -= 1
                            else:
                                self.gameState = "Game Over"
                            play_sound(snd_bangL)
                            saucer.bullets.remove(b, force=True)

                    if b.life <= 0:
                        try:
                            saucer.bullets.remove(b, force=True)
                        except ValueError:
                            continue

        removable_saucers = [s for s in self.saucers if not s.is_alive]
        for s in removable_saucers:
            self.saucers.remove(s)

    def handle_collector_bullets(self):
        for cb in self.collector_bullets:
            cb.updateBullet()
            for debris in self.saucer_debris:
                if isColliding(cb.x, cb.y, debris.x, debris.y, (debris.size / 2) + (cb.size / 2)):
                    self.player.handle_collection(debris, self.saucer_debris)
            if cb.life <= 0:
                try:
                    if cb in self.collector_bullets:
                        self.collector_bullets.remove(cb)
                except ValueError:
                    continue

    def handle_saucer_debris(self):
        for d in self.saucer_debris:
            if isColliding(d.x, d.y, self.player.x, self.player.y, saucer_debris_size):
                self.player.handle_collection(d, self.saucer_debris)

    def handle_rapidfire(self):
        self.player.handle_rapidfire(self.bullets)

    def handle_bullets(self):
        for b in self.bullets:
            b.updateBullet()
            if type(b) is Nuke and b.is_blowing_up:
                b.handle_explosion(self.saucers, self.player)
            for a in self.asteroids:
                if (b.x > a.x - b.size and b.x < a.x + b.size and b.y > a.y - b.size and b.y < a.y + b.size) or \
                        (b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size):
                    if a.t == "Large":
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.score += 20
                        play_sound(snd_bangL)
                    elif a.t == "Normal":
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.score += 50
                        play_sound(snd_bangM)
                    else:
                        self.score += 100
                        play_sound(snd_bangS)
                    self.asteroids.remove(a)
                    self.bullets.remove(b)
                    break
            if b.can_remove():
                try:
                    self.bullets.remove(b)
                except ValueError:
                    continue

    def handle_extra_lives(self):
        if self.score > self.oneUp_multiplier * 23000:
            self.oneUp_multiplier += 1
            self.live += 1
            self.playOneUpSFX = 60
        if self.playOneUpSFX > 0:
            self.playOneUpSFX -= 1
            play_sound(snd_extra, 10)

    def draw_player(self):
        if self.gameState != "Game Over":
            if self.player_state == "Died":
                if self.hyperspace == 0:
                    if self.player_dying_delay == 0:
                        if self.player_blink < 5:
                            if self.player_blink == 0:
                                self.player_blink = 10
                            else:
                                self.player.drawPlayer()
                        self.player_blink -= 1
                    else:
                        self.player_dying_delay -= 1
            else:
                self.player.drawPlayer()
        else:
            drawText("Game Over", white, display_width / 2, display_height / 2, 100)
            drawText("Press \"R\" to restart!", white, display_width / 2, display_height / 2 + 100, 50)
            self.live = -1

    def draw_hud(self):
        x_pos = 100
        p_int = 265

        drawText("S{} - {}".format(self.stage, self.score), white, x_pos, 20, 40, False)
        x_pos += p_int

        matrix_time_left = max(0, round(self.player.matrix_till - time(), 1))
        drawText("MATRIX - " + str(matrix_time_left), green, x_pos, 20, 35, False)
        x_pos += p_int - 30

        on_off = "ON" if self.player.selected_weapon == RAPID_FIRE else "OFF"
        drawText("RapidF - {} - {}".format(str(self.player.rapid_fire_count), on_off), red, x_pos, 20, 35, False)
        x_pos += p_int

        on_off = "ON" if self.player.selected_weapon == MISSLES else "OFF"
        drawText("MISSLES - {} - {}".format(str(self.player.missles), on_off), orange, x_pos, 20, 35, False)
        x_pos += p_int + 10

        on_off = "ON" if self.player.selected_weapon == NUKES else "OFF"
        drawText("Nukes - {} - {}".format(str(self.player.nukes), on_off), light_green, x_pos, 20, 35, False)
        x_pos += p_int + 10

        on_off = "ON" if self.player.selected_weapon == LASER else "OFF"
        drawText("Laser - {} - {}".format(str(self.player.laser), on_off), purple, x_pos, 20, 35, False)
        x_pos += p_int + 10

        drawText("INV Time {}".format(round(self.player.invi_dur / 30, 1)), yellow, x_pos, 20, 35, False)
        drawText("Saucers Left - {}".format(self.saucers_this_stage), white, display_width - 280, 20, 35, False)

        drawText(f"Lives: {self.live + 1}", white, 75, 75, 35, False)

    def game_loop(self):
        self.initialize_game()
        while self.gameState != "Exit":
            start_time = time()
            self.i += 1

            while self.gameState == "Menu":
                self.gameState, self.difficulty, self.selected_difficulty = menu(self.selected_difficulty)
                if self.gameState != "Menu":
                    self.saucer_factory = SaucerFactory(difficulty=self.difficulty)
                    gameDisplay.fill(black)
                    pygame.display.update()

            if not self.handle_user_inputs():
                continue

            self.update_player()
            self.reset_display()
            self.handle_hyperspace()
            self.check_collisions_with_asteroids()
            self.update_ship_fragments()
            self.check_end_of_stage()
            self.update_intensity()
            self.handle_saucers()
            self.handle_collector_bullets()
            self.handle_saucer_debris()
            self.handle_rapidfire()
            self.handle_bullets()
            self.handle_extra_lives()
            self.draw_player()
            self.draw_hud()

            end_time = time()
            loop_time = end_time - start_time

            if loop_time > 0.044333333333:
                print("Slow - {}".format(loop_time))

            if not args.debug:
                if self.player.matrix_till > time():
                    timer.tick_busy_loop(18)
                else:
                    timer.tick_busy_loop(30)
            else:
                timer.tick_busy_loop(args.debug)

            t1 = time()
            Displayable.update_display()
            t2 = time()
            diff = t2 - t1

            if diff > 0.004:
                print("Slow display update {}".format(diff))


# Start game
game = Game("Menu")
game.game_loop()

# End game
pygame.quit()
quit()
