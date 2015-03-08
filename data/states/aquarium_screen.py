from random import randint, choice
from itertools import cycle
import pygame as pg
from .. import tools, prepare
from ..components.fish import FishOne, FishTwo, FishThree, FishFour, FishFive

class Water(object):
    def __init__(self):
        names = ["ocean{}".format(x) for x in range(1, 11)]
        images = [prepare.GFX[name] for name in names]
        self.images = cycle(images)
        self.image = next(self.images)
        self.anim_time = 150
        self.elapsed = 0.0
        
    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.anim_time:
            self.elapsed -= self.anim_time
            self.image = next(self.images)
    
    def draw(self, surface):
        surface.blit(self.image, (0, 0))

    
class Aquarium(tools._State):
    def __init__(self):
        super(Aquarium, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        self.water = Water()
        self.ocean = self.screen_rect.inflate(1000, 1000)
        self.fish_classes = [FishOne, FishTwo, FishThree, FishFour, FishFive]
        self.fishes = []
        for _ in range(50):
            self.add_fish()
        self.bubbles = []
        pg.mixer.music.load(prepare.MUSIC["LavaLoop"])
        pg.mixer.music.play(-1)
        self.elapsed = 0.0
        
    def add_fish(self):
        pos = (randint(self.ocean.left, self.ocean.right),
                   randint(self.ocean.top, self.ocean.bottom))
        z_pos = randint(0, 100)
        klass = choice(self.fish_classes)
        self.fishes.append(klass(pos, z_pos))
        
    def startup(self, persistent):
        self.persist = persistent
        pg.mixer.music.load(prepare.SONGS["lava_loop"])
        pg.mixer.musc.play()
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.done = True
            self.quit = True
            
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass
        
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.done = True
                self.quit = True
            
    def update(self, surface, keys, dt):
        self.water.update(dt)
        for fish in self.fishes:
            fish.update(dt, self)
        for bubble in self.bubbles:
            bubble.update(dt)
        self.bubbles = [x for x in self.bubbles if not x.done]
        
        self.draw(surface)
        
    def draw(self, surface):
        self.water.draw(surface)
        all_critters = self.fishes + self.bubbles
        all_critters.sort(key=lambda x: x.z_pos, reverse=True)
        for critter in all_critters:
            if critter.rect.colliderect(self.screen_rect):
                critter.draw(surface)