# Import modules
from argparse import ArgumentParser
from powerups import *
from player import *
from bullet import *
from saucer import *
from asteroid import *

parser = ArgumentParser()
parser.add_argument("-d", "--debug", help="Runs slower so its easier to debug shit", default=False)
args, _ = parser.parse_known_args()


pygame.init()

pygame.display.set_caption("Roid Rage")
timer = pygame.time.Clock()

# seeking missle
# purple lazer
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


def gameLoop(startingState):
    # Init variables
    gameState = startingState
    player_state = "Alive"
    player_blink = 0
    player_pieces = safelist()
    saucer_debris = safelist()
    player_dying_delay = 0
    hyperspace = 0
    next_level_delay = 0
    bullet_capacity = 14
    bullets = safelist()
    collector_bullets = safelist()
    asteroids = safelist()
    stage = 6
    score = 0
    live = 2
    oneUp_multiplier = 1
    playOneUpSFX = 0
    intensity = 0
    delay_between_levels = 45

    debris_factory = SaucerDebrisFactory()
    saucer_factory = SaucerFactory()

    saucers = safelist([saucer_factory() for _ in range(0, 2)])
    saucers.append(Battleship())
    player = Player(display_width / 2, display_height / 2)

    # Main loop
    while gameState != "Exit":
        # Game menu
        while gameState == "Menu":
            gameDisplay.fill(black)
            drawText("ROID RAGE", white, display_width / 2, display_height / 2, 100)
            drawText("Press any key to START", white, display_width / 2, display_height / 2 + 100, 50)
            drawText("FUCK YOU", white, display_width / 2, display_height / 2 + 200, 50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameState = "Exit"
                if event.type == pygame.KEYDOWN:
                    gameState = "Playing"
            pygame.display.update()
            timer.tick(5)

        # User inputs
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
                        and (len(bullets) < bullet_capacity or player.has_rapid_fire):
                    if player.has_rapid_fire and player.selected_weapon == BULLETS:
                        player.rapidfire(bullets)
                    else:
                        if player.missles and player.selected_weapon == MISSLES:
                            bullets.append(Missle(player.x, player.y, player.dir, saucer=player.target))
                            player.selected_weapon = MISSLES
                            player.missles -= 1
                            if player.missles == 0:
                                player.selected_weapon = BULLETS
                        else:
                            bullets.append(Bullet(player.x, player.y, player.dir))
                        play_sound(snd_fire)

                if event.key == pygame.K_c and player_dying_delay == 0 and len(bullets) < bullet_capacity:
                    collector_bullets.append(collectorBullet(player.x, player.y, player.dir, color=blue))
                    play_sound(snd_fire)

                if event.key == pygame.K_DOWN and player.missles > 0:
                    if player.selected_weapon == BULLETS:
                        player.selected_weapon = MISSLES
                    else:
                        player.selected_weapon = BULLETS

                if gameState == "Game Over":
                    if event.key == pygame.K_r:
                        gameState = "Exit"
                        gameLoop("Playing")

                if event.key == pygame.K_LSHIFT:
                    hyperspace = 30
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.thrust = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.rtspd = 0

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
        for f in player_pieces:
            f.updateDeadPlayer()
            if f.x > display_width or f.x < 0 or f.y > display_height or f.y < 0:
                player_pieces.remove(f)

        for f in saucer_debris:
            f.updateDebris(saucer_debris)

        # Check for end of stage
        if len(asteroids) == 0 and len(saucers) == 0:
            if next_level_delay < delay_between_levels:
                next_level_delay += 1
            else:
                stage += 1
                intensity = 0
                # Spawn asteroid away of center
                for i in range(stage):
                    xTo = display_width / 2
                    yTo = display_height / 2
                    while xTo - display_width / 2 < display_width / 4 and yTo - display_height / 2 < display_height / 4:
                        xTo = random.randrange(0, display_width)
                        yTo = random.randrange(0, display_height)
                    asteroids.append(Asteroid(xTo, yTo, "Large"))
                next_level_delay = 0

        # Update intensity
        if intensity < stage * 450:
            intensity += 1

        # Saucer
        if random.randint(0, 6000) <= (intensity * 2) / (stage * 9) and next_level_delay == 0 \
                and len(saucers) < max_saucers:
            if score < 40000:
                saucers.append(saucer_factory(stage=stage))
            else:
                saucers.append(saucer_factory(stage=stage))

        else:
            for saucer in saucers:
                saucer.set_direction(stage, player)
                saucer.updateSaucer()
                saucer.drawSaucer()
                saucer.shooting()

                # Check for collision w/ asteroid
                for a in asteroids:
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
                        asteroids.remove(a)

                # Check for collision w/ bullet
                for b in bullets:
                    if isColliding(b.x, b.y, saucer.x, saucer.y, (saucer.size / 2) + b.size):
                        if saucer.should_die(b):
                            score += saucer.score
                            saucer.is_alive = False
                            saucer_debris.append(debris_factory(b.x, b.y))
                            saucer_debris.append(debris_factory(b.x, b.y))
                            saucer_debris.append(debris_factory(b.x, b.y))

                        play_sound(snd_bangL)
                        bullets.remove(b)

                # Check collision w/ player
                if isColliding(saucer.x, saucer.y, player.x, player.y, saucer.size):
                    if player_state != "Died":
                        # Create ship fragments
                        if player.shields >= 5 and type(saucer) is not Battleship:
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
                            if player.shields:
                                player.shields -= 1
                                play_sound(zap)
                                saucer.bullets.remove(b)
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
                            saucer.bullets.remove(b)

                    if b.life <= 0:
                        saucer.bullets.remove(b)

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

            # Check for bullets collide w/ asteroid
            for a in asteroids:
                if b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size:
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
            if b.life <= 0:
                try:
                    bullets.remove(b)
                except ValueError:
                    continue

        # Extra live
        if score > oneUp_multiplier * 10000:
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

        # draw score and power up levels
        drawText(str(score), white, 60, 20, 40, False)

        matrix_time_left = max(0, round(player.matrix_till - time(), 1))
        drawText("MATRIX - " + str(matrix_time_left), green, 260, 20, 35, False)

        rapid_time_left = max(0, round(player.rapid_fire_till - time(), 1))
        drawText("RapidF - " + str(rapid_time_left), red, 470, 20, 35, False)

        on_off = "ON" if player.selected_weapon == MISSLES else "OFF"
        drawText("MISSLES - {} - {}".format(str(player.missles), on_off), orange, 670, 20, 35, False)

        drawText("INV Time {}".format(round(player.invi_dur / 30, 1)), yellow, 1020, 20, 35, False)

        # Draw Lives
        for l in range(live + 1):
            p = Player(75 + l * 25, 75)
            p.shields = 0
            p.drawPlayer()

        pygame.display.update()

        if not args.debug:
            if player.matrix_till > time():
                timer.tick(18)
            else:
                timer.tick(30)
        else:
            timer.tick(10)


# Start game
gameLoop("Menu")

# End game
pygame.quit()
quit()
