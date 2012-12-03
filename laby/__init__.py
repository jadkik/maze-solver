import pygame
from .game import Game

def main(filename):
    pygame.init()
    g = Game(filename)
    g.loop()
