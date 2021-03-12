import pygame
from constants import *

pygame.init()

snd_fire = pygame.mixer.Sound("Sounds/fire.wav")
snd_bangL = pygame.mixer.Sound("Sounds/bangLarge.wav")
snd_bangM = pygame.mixer.Sound("Sounds/bangMedium.wav")
snd_bangS = pygame.mixer.Sound("Sounds/bangSmall.wav")
snd_extra = pygame.mixer.Sound("Sounds/extra.wav")
snd_saucerB = pygame.mixer.Sound("Sounds/saucerBig.wav")
snd_saucerS = pygame.mixer.Sound("Sounds/saucerSmall.wav")
zap = pygame.mixer.Sound("Sounds/zap.wav")
new_saucer = pygame.mixer.Sound("Sounds/new_saucer.wav")
nuke_explosion = pygame.mixer.Sound("Sounds/nuke_exploding.wav")
nuke_launch = pygame.mixer.Sound("Sounds/nuke_launch.wav")
missle = pygame.mixer.Sound("Sounds/missle.wav")
missle.set_volume(.3623)
nuke_explosion.set_volume(.3623)
nuke_launch.set_volume(.5)


def play_sound(*a, **kwargs):
    pygame.mixer.Sound.play(*a, **kwargs)
