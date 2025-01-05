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



def handle_events(player, bullets, collector_bullets, gameState, hyperspace, player_dying_delay):
    # Main loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameState = "Exit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.thrust = True

            if event.key == pygame.K_LEFT:
                player.rtspd = -player_max_rtspd

            if event.key == pygame.K_RIGHT:
                player.rtspd = player_max_rtspd

            if event.key == pygame.K_SPACE and player_dying_delay == 0 \
                    and (len(bullets) < bullet_capacity or player.selected_weapon == RAPID_FIRE):
                player.fire_weapon(bullets)

            if event.key == pygame.K_c and player_dying_delay == 0 and len(bullets) < bullet_capacity:
                collector_bullets.append(collectorBullet(player.x, player.y, player.dir, color=blue))
                play_sound(snd_fire)

            if event.key == pygame.K_DOWN:
                while 1:
                    player.selected_weapon += 1
                    if player.selected_weapon > len(weapons):
                        player.selected_weapon = BULLETS
                        break

                    if getattr(player, weapons[player.selected_weapon]) > 0:
                        player.selected_weapon = player.selected_weapon
                        player.draw_selected_weapon_time = 15
                        break

            if gameState == "Game Over":
                if event.key == pygame.K_r:
                    gameState = "Exit"
                    gameLoop("Playing")

            if event.key == pygame.K_p:
                if gameState == "Playing":
                    gameState = "Paused"
                else:
                    gameState = "Playing"

            if event.key == pygame.K_LSHIFT:
                hyperspace = 30

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player.thrust = False
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.rtspd = 0

    return gameState, hyperspace


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


def gameLoop(startingState):
    # Init variables
    gameState = startingState
    player_state = "Alive"
    player_blink = 0
    player_pieces = safelist()
    saucer_debris = safelist()
    player_dying_delay = 0
    hyperspace = 0
    delay_between_levels = 45
    next_level_delay = delay_between_levels
    bullets = safelist()
    collector_bullets = safelist()
    asteroids = safelist()
    stage = 1
    score = 0
    live = 2
    oneUp_multiplier = 1
    playOneUpSFX = 0
    intensity = 0
    min_asteroids = 4
    saucers_this_stage = saucers_per_stage - 3  # we start with 3
    new_saucer_interval = 9 * 30
    new_saucer_time = new_saucer_interval

    difficulty, selected_difficulty = 1, "Normal"

    while gameState == "Menu":
        gameState, difficulty, selected_difficulty = menu(selected_difficulty)

    # blank out the middle of the screen
    gameDisplay.fill(black)
    pygame.display.update()

    saucer_factory = SaucerFactory(difficulty=difficulty)
    debris_factory = SaucerDebrisFactory()

    player = Player(display_width / 2, display_height / 2)
    Player.player = player

    saucers = safelist([saucer_factory() for _ in range(0, 0)])
    saucers.append(Battleship(dodge_bullet_range=700, health=100, finesse=20))
    #saucers.append(Boss(stage=1))
    #saucers.append(Sniper())

    i = 0

    # Main loop
    while gameState != "Exit":
        start_time = time()
        i += 1

        while gameState == "Menu":
            gameState, difficulty, selected_difficulty = menu(selected_difficulty)
            if gameState != "Menu":
                saucer_factory = SaucerFactory(difficulty=difficulty)
                # blank out the middle of the screen
                gameDisplay.fill(black)
                pygame.display.update()

        # User inputs
        gameState, hyperspace = handle_events(player, bullets, collector_bullets,
                                              gameState, hyperspace, player_dying_delay)
        if gameState == "Paused":
            timer.tick_busy_loop(5)
            continue

        # Update player
        player.updatePlayer(saucers)

        # Checking player invincible time
        if player.invi_dur != 0:
            player.invi_dur -= 1
        elif hyperspace == 0:
            player_state = "Alive"
   
        # Reset display     
        gameDisplay.fill(black)

        # Hyperspace
        if hyperspace != 0:
            player_state = "Died"
            hyperspace -= 1
            if hyperspace == 1:
                player.x = random.randrange(0, display_width)
                player.y = random.randrange(0, display_height)

        # Check for collision w/ asteroid
        for a in asteroids:
            a.updateAsteroid()
            if player_state != "Died":
                if isColliding(player.x, player.y, a.x, a.y, a.size):
                    if player.shields > 1:
                        player.shields -= 2
                        play_sound(zap)
                    else:
                        player_state = "Died"
                        player_dying_delay = 30
                        player.invi_dur = 120
                        player.killPlayer()
                        blowUp(player, player_pieces)

                        if live != 0:
                            live -= 1
                        else:
                            gameState = "Game Over"

                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        # Play SFX
                        play_sound(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        # Play SFX
                        play_sound(snd_bangM)
                    else:
                        score += 100
                        # Play SFX
                        play_sound(snd_bangS)
                    asteroids.remove(a)

        # Update ship fragments
        for f in list(player_pieces):
            f.updateDeadPlayer()
            if f.x > display_width or f.x < 0 or f.y > display_height or f.y < 0:
                player_pieces.remove(f)
            if f.life <= 0:
                player_pieces.remove(f)

        for f in saucer_debris:
            f.updateDebris(saucer_debris)

        # Check for end of stage
        if len(asteroids) < min_asteroids and len(saucers) == 0 and saucers_this_stage <= 0:
            if next_level_delay > 0:
                next_level_delay -= 1
            else:
                stage += 1
                intensity = 0
                # Spawn asteroid away of center
                while len(asteroids) < min_asteroids:
                    xTo = display_width / 2
                    yTo = display_height / 2
                    while xTo - display_width / 2 < display_width / 4 and yTo - display_height / 2 < display_height / 4:
                        xTo = random.randrange(0, display_width)
                        yTo = random.randrange(0, display_height)

                        asteroids.append(Asteroid(xTo, yTo, "Large"))

                next_level_delay = delay_between_levels
                saucers_this_stage = saucers_per_stage + int((stage * 2) / 2)
                min_asteroids += 2

        # Update intensity
        if intensity < stage * 450:
            intensity += 1

        new_saucer_time -= 1

        # Saucer
        if random.randint(0, 3500) <= (intensity * 2) / (stage * 9) and next_level_delay == delay_between_levels \
                and len(saucers) < max_saucers and saucers_this_stage and new_saucer_time < 0:
            new_saucer_time = new_saucer_interval

            if saucers_this_stage > 1:
                saucers_this_stage -= 1
                saucers.append(saucer_factory(stage=stage))
            else:
                if len(saucers) == 0:
                    saucers_this_stage -= 1
                    saucers.append(Boss(stage=stage))

        else:
            for saucer in saucers:
                saucer.set_direction(stage, player)
                saucer.updateSaucer(bullets)
                saucer.drawSaucer(player)
                saucer.shooting()

                # Check for collision w/ asteroid
                """for a in asteroids:
                    if isColliding(saucer.x, saucer.y, a.x, a.y, a.size + saucer.size):
                        # Set saucer state
                        saucer.is_alive = False
                        blowUp(saucer, player_pieces)

                        # Split asteroid
                        if a.t == "Large":
                            asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            # Play SFX
                            play_sound(snd_bangL)
                        elif a.t == "Normal":
                            asteroids.append(Asteroid(a.x, a.y, "Small"))
                            asteroids.append(Asteroid(a.x, a.y, "Small"))
                            # Play SFX
                            play_sound(snd_bangM)
                        else:
                            # Play SFX
                            play_sound(snd_bangS)
                        asteroids.remove(a)"""

                # Check for collision w/ bullet
                for b in bullets:
                    if b.should_kill(saucer):
                        score += saucer.score
                        saucer.is_alive = False
                        saucer_debris.append(debris_factory(saucer.x, saucer.y, saucer=saucer))
                        saucer_debris.append(debris_factory(saucer.x, saucer.y, saucer=saucer))
                        saucer_debris.append(debris_factory(saucer.x, saucer.y, saucer=saucer))
                        bullets.remove(b)

                # Check collision w/ player
                if isColliding(saucer.x, saucer.y, player.x, player.y, saucer.size):
                    if player_state != "Died":
                        # Create ship fragments
                        if player.shields >= 5 and type(saucer) not in (Battleship, Boss):
                            player.shields -= 5
                            blowUp(saucer, player_pieces)
                            saucer.is_alive = False
                        else:
                            blowUp(saucer, player_pieces)

                            # Kill player
                            player_state = "Died"
                            player_dying_delay = 30
                            player.invi_dur = 120
                            player.killPlayer()

                            if live != 0:
                                live -= 1
                            else:
                                gameState = "Game Over"

                            # Play SFX
                        play_sound(snd_bangL)

                # Saucer's bullets
                for b in saucer.bullets:
                    # Update bullets
                    b.updateBullet()

                    # Check for collision w/ asteroids
                    for a in asteroids:
                        if isColliding(b.x, b.y, a.x, a.y, a.size):
                            # Split asteroid
                            if a.t == "Large":
                                asteroids.append(Asteroid(a.x, a.y, "Normal"))
                                asteroids.append(Asteroid(a.x, a.y, "Normal"))
                                # Play SFX
                                play_sound(snd_bangL)
                            elif a.t == "Normal":
                                asteroids.append(Asteroid(a.x, a.y, "Small"))
                                asteroids.append(Asteroid(a.x, a.y, "Small"))
                                # Play SFX
                                play_sound(snd_bangL)
                            else:
                                # Play SFX
                                play_sound(snd_bangL)

                            # Remove asteroid and bullet
                            asteroids.remove(a)
                            saucer.bullets.remove(b)
                            break

                    # Check for collision w/ player
                    if isColliding(player.x, player.y, b.x, b.y, player.is_hit_size(b)):
                        if player_state != "Died":
                            if player.shields > 0:
                                player.shields = int(max(player.shields - (b.damage / 10), 0))
                                play_sound(zap)
                                saucer.bullets.remove(b, force=True)
                                continue

                            # Create ship fragments
                            blowUp(player, player_pieces)
                            player.shields = 0

                            # Kill player
                            player_state = "Died"
                            player_dying_delay = 30
                            player.invi_dur = 120
                            player.killPlayer()

                            if live != 0:
                                live -= 1
                            else:
                                gameState = "Game Over"

                            play_sound(snd_bangL)
                            saucer.bullets.remove(b, force=True)

                    if b.life <= 0:
                        try:
                            saucer.bullets.remove(b, force=True)
                        except ValueError:
                            continue

        removable_saucers = [s for s in saucers if not s.is_alive]

        for s in removable_saucers:
            saucers.remove(s)

        for cb in collector_bullets:
            cb.updateBullet()

            for debris in saucer_debris:
                if isColliding(cb.x, cb.y, debris.x, debris.y, (debris.size / 2) + (cb.size / 2)):
                    player.handle_collection(debris, saucer_debris)

            if cb.life <= 0:
                try:
                    if cb in collector_bullets:
                        collector_bullets.remove(cb)
                except ValueError:
                    continue

        for d in saucer_debris:
            if isColliding(d.x, d.y, player.x, player.y, saucer_debris_size):
                player.handle_collection(d, saucer_debris)

        player.handle_rapidfire(bullets)

        # Bullets
        for b in bullets:
            # Update bullets
            b.updateBullet()

            if type(b) is Nuke and b.is_blowing_up:
                b.handle_explosion(saucers, player)

            # Check for bullets collide w/ asteroid
            for a in asteroids:
                if (b.x > a.x - b.size and b.x < a.x + b.size and b.y > a.y - b.size and b.y < a.y + b.size) or \
                        (b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size):
                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        # Play SFX
                        play_sound(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        # Play SFX
                        play_sound(snd_bangM)
                    else:
                        score += 100
                        # Play SFX
                        play_sound(snd_bangS)
                    asteroids.remove(a)
                    bullets.remove(b)
                    break

            # Destroying bullets
            if b.can_remove():
                try:
                    bullets.remove(b)
                except ValueError:
                    continue

        # Extra live
        if score > oneUp_multiplier * 23000:
            oneUp_multiplier += 1
            live += 1
            playOneUpSFX = 60
        # Play sfx
        if playOneUpSFX > 0:
            playOneUpSFX -= 1
            play_sound(snd_extra, 10)

        # Draw player
        if gameState != "Game Over":
            if player_state == "Died":
                if hyperspace == 0:
                    if player_dying_delay == 0:
                        if player_blink < 5:
                            if player_blink == 0:
                                player_blink = 10
                            else:
                                player.drawPlayer()
                        player_blink -= 1
                    else:
                        player_dying_delay -= 1
            else:
                player.drawPlayer()
        else:
            drawText("Game Over", white, display_width / 2, display_height / 2, 100)
            drawText("Press \"R\" to restart!", white, display_width / 2, display_height / 2 + 100, 50)
            live = -1

        x_pos = 100
        p_int = 265

        drawText("S{} - {}".format(stage, score), white, x_pos, 20, 40, False)
        x_pos += p_int

        matrix_time_left = max(0, round(player.matrix_till - time(), 1))
        drawText("MATRIX - " + str(matrix_time_left), green, x_pos, 20, 35, False)
        x_pos += p_int -  30

        on_off = "ON" if player.selected_weapon == RAPID_FIRE else "OFF"
        drawText("RapidF - {} - {}".format(str(player.rapid_fire_count), on_off), red, x_pos, 20, 35, False)
        x_pos += p_int

        on_off = "ON" if player.selected_weapon == MISSLES else "OFF"
        drawText("MISSLES - {} - {}".format(str(player.missles), on_off), orange, x_pos, 20, 35, False)
        x_pos += p_int + 10

        on_off = "ON" if player.selected_weapon == NUKES else "OFF"
        drawText("Nukes - {} - {}".format(str(player.nukes), on_off), light_green, x_pos, 20, 35, False)
        x_pos += p_int + 10

        on_off = "ON" if player.selected_weapon == LASER else "OFF"
        drawText("Laser - {} - {}".format(str(player.laser), on_off), purple, x_pos, 20, 35, False)
        x_pos += p_int + 10

        drawText("INV Time {}".format(round(player.invi_dur / 30, 1)), yellow, x_pos, 20, 35, False)
        drawText("Saucers Left - {}".format(saucers_this_stage), white, display_width - 280, 20, 35, False)

        drawText(f"Lives: {live + 1}", white, 75, 75, 35, False)

        end_time = time()

        loop_time = end_time - start_time

        if loop_time > 0.044333333333:
            print("Slow - {}".format(loop_time))

        if not args.debug:
            if player.matrix_till > time():
                timer.tick_busy_loop(18)
            else:
                timer.tick_busy_loop(30)
        else:
            timer.tick_busy_loop(args.debug)

        t1 = time()
        Displayable.update_display()
        # pygame.display.flip()
        t2 = time()
        diff = t2 - t1

        if diff > 0.004:
            print("Slow display update {}".format(diff))


# Start game
gameLoop("Menu")

# End game
pygame.quit()
quit()
