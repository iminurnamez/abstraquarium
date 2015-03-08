import pygame as pg

pg.init()
pg.mixer.init()


class PlayButton(object):
    def __init__(self, 
names = [
    "water_splash-0{}.ogg".format(i) for i in range(7)]
volumes = [.5, .5, .5, .5, .5, .5]    
for name, volume in zip(names, volumes):
    sound = pg.mixer.Sound(name)
    print sound
    sound.set_volume(volume)
    sound.play()
    pg.time.delay(100)