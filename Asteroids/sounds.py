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


def play_sound(*a, **kwargs):
    pygame.mixer.Sound.play(*a, **kwargs)
