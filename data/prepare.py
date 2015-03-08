import os
import pygame as pg
from . import tools
#from .components import players

SCREEN_SIZE = (1280, 720)
OCEAN_SIZE = (3840, 2160)

pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
SCREEN = pg.display.set_mode(SCREEN_SIZE) #, pg.NOFRAME) #pg.FULLSCREEN) #, pg.HWSURFACE)



FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))


