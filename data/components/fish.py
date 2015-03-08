from math import radians, pi, cos
from random import randint, uniform, choice
from itertools import cycle
import pygame as pg
from .. import tools, prepare
from ..components.angles import get_angle, project, get_distance, get_edge_pos
from ..components.animation import Animation
from ..components.labels import Label


def ghost_image(image, color):
    shaded = image.copy()
    shaded.fill(color, special_flags=pg.BLEND_RGBA_MULT)
    return shaded

def shaded_image(image, color):
    copied = image.copy()
    ghost = ghost_image(image, color)
    copied.blit(ghost, (0,0))
    return copied
    
    
class Fish(object):
    screen_rect = pg.display.get_surface().get_rect()
    tank_rect = screen_rect.inflate(1000, 1000)
    scale_mod = .01
    
    splash_sounds = [prepare.SFX["water_splash-0{}".format(i)] for i in range(1, 7)]
    font = prepare.FONTS["weblysleekuisb"]
    
    def __init__(self, center_pos, z_pos, mouth_y):
        self.x, self.y = center_pos
        self.image_cycle = cycle(self.images)
        self.image = next(self.image_cycle)
        self.rect = self.image.get_rect(center=center_pos)
        self.z_pos = z_pos
        self.elapsed = 0.0
        self.anim_time = 80
        self.mouth_pos = mouth_y / float(self.rect.height)
        self.bubble_timer = 0.0
        self.bubble_time_range = (500, 5000)
        self.bubble_pause = randint(*self.bubble_time_range)
        self.max_belly = self.belly = 1000
        self.move_animations = pg.sprite.Group()
        self.depth_animations = pg.sprite.Group()
        self.turn_animations = pg.sprite.Group()
        self.speed = .12
        self.travel_angle = 0.0
        self.turn = 0
        self.behavior = Roaming()
        self.next_img()
        
    def next_img(self):        
        self.elapsed -= self.anim_time
        self.image = next(self.image_cycle)
        if 1.5*pi > self.travel_angle > .5*pi:
            self.image = pg.transform.flip(self.image, True, False)
        
    def make_bubble(self):
        self.bubble_timer = 0.0
        self.bubble_pause = randint(*self.bubble_time_range)
        x = self.rect.right
        if 1.5*pi > self.travel_angle > .5*pi:
            x = self.rect.left
        mouth_pos = (x, self.rect.top + (self.rect.height * self.mouth_pos))
        return Bubble(mouth_pos, self.z_pos)
           
    def update(self, dt, tank):
        self.elapsed += dt
        if self.elapsed >= self.anim_time:
            self.next_img()
        self.bubble_timer += dt
        if self.bubble_timer >= self.bubble_pause:
            bubble = self.make_bubble()
            if bubble.rect.colliderect(self.screen_rect):
                tank.bubbles.append(bubble)
        self.behavior.update(self, dt)
        if self.behavior.done:
            self.behavior = self.behaviors[self.behavior.next]    
        self.move_animations.update(dt)
        self.depth_animations.update(dt)
        self.turn_animations.update(dt)
        new_size = self.get_new_size(self.get_scale())
        self.scale(new_size)
        
    def get_scale(self):
        return max(.01, 1 - (self.z_pos * self.scale_mod))
    
    def get_new_size(self, scale):
        w, h = self.size
        return (int(w * scale), int(h * scale))
        
    def scale(self, new_size):       
        self.scaled_image = pg.transform.smoothscale(self.image, new_size)
        self.rect = self.scaled_image.get_rect(center=(self.x, self.y))    
        back_shade = 255 - int(self.z_pos * 2)
        deep_shade =  max(0, self.y // 10)
        shade = max(0, back_shade - deep_shade)
        color = (shade, shade, shade)
        self.scaled_image = ghost_image(self.scaled_image, color)  
        width, height = self.rect.size
        value = (180 * cos(2 * pi * (self.turn / 180.))) + 180
        width *= value / 360.0
        width = int(round(max(1, abs(width)), 0))
        self.scaled_image = pg.transform.smoothscale(self.scaled_image, (width, int(height)))
        self.rect = self.scaled_image.get_rect(center=(self.x, self.y))
        
    def draw(self, surface):
        surface.blit(self.scaled_image, self.rect)
        

class FishOne(Fish):
    size = (192, 142) 
    sheet = prepare.GFX["fishstrip1"]
    images = tools.strip_from_sheet(sheet, (0, 0), size, 10)
    def __init__(self, center, z_pos):
        super(FishOne, self).__init__(center, z_pos, 92)
        
class FishTwo(Fish):
    size = (191, 131) 
    sheet = prepare.GFX["fishstrip2"]
    images = tools.strip_from_sheet(sheet, (0, 0), size, 10)
    def __init__(self, center, z_pos):
        super(FishTwo, self).__init__(center, z_pos, 78)
        
class FishThree(Fish):
    size = (190, 148)
    sheet = prepare.GFX["fishstrip3"]
    images = tools.strip_from_sheet(sheet, (0, 0), size, 10)
    def __init__(self, center, z_pos):
        super(FishThree, self).__init__(center, z_pos, 99)
        
class FishFour(Fish):
    size = (187, 189)
    sheet = prepare.GFX["fishstrip4"]
    images = tools.strip_from_sheet(sheet, (0, 0), size, 10)
    def __init__(self, center, z_pos):
        super(FishFour, self).__init__(center, z_pos, 117)
        
class FishFive(Fish):
    size = (198, 130)
    sheet = prepare.GFX["fishstrip5"]
    images = tools.strip_from_sheet(sheet, (0, 0), size, 10)
    def __init__(self, center, z_pos):
        super(FishFive, self).__init__(center, z_pos, 75)
        
class FishBehavior(object):
    def __init__(self):
        self.next = None
        self.done = False
        
    def update(self,fish, dt):
        pass

        
class Roaming(FishBehavior):
    transitions = ["linear"]
                         #"out_quint",
                         #"in_out_quint",
                         #"linear",
                         #"in_sine",
                         #"out_sine"
                         #]
    def __init__(self):
        super(Roaming, self).__init__()
        
    def update(self, fish, dt):
        if not fish.move_animations:
            if fish.belly < fish.max_belly * .75:
                self.next = "SEEK_FOOD"
                self.done = True
            else:
                self.set_goal(fish)
                
    def set_goal(self, fish):        
        half_w = fish.rect.width // 2
        half_h = fish.rect.height // 2
        goal = (randint(half_w, fish.tank_rect.right - half_w),
                   randint(half_h, fish.tank_rect.bottom - half_h))
        
        z_goal = randint(0, 100)       
        z_diff = abs(z_goal - fish.z_pos)
        real_z_diff = z_goal - fish.z_pos 
        distance = get_distance(fish.rect.center, goal)
        turn = (real_z_diff / float(distance)) * 300
        turn_goal = max(0, min(turn, 60))  
        speed = fish.speed * (max(.01, 1 - (fish.z_pos * fish.scale_mod)))
        duration_ = distance // speed
        duration_ += (z_diff * 20) // speed 
        fish.travel_angle = get_angle(fish.rect.center, goal)
        trans = choice(self.transitions)
        ani = Animation(x=goal[0], y=goal[1], duration=duration_, 
                                 round_values=True, transition=trans)
        ani2 = Animation(z_pos=z_goal, duration=duration_, 
                                 round_values=True, transition=trans)
        ani3 = Animation(turn=turn_goal, duration=1000,
                                  transition=trans)        
        ani.start(fish)
        ani2.start(fish)
        ani3.start(fish)
        choice(fish.splash_sounds).play()
        fish.move_animations.add(ani)
        fish.depth_animations.add(ani2)
        fish.turn_animations.add(ani3)        


class Bubble(object):
    bases = tools.strip_from_sheet(prepare.GFX["bubblestrip"], (0, 0), (12, 12), 5)
    scale_mod = .01
    size = (12, 12)    
    def __init__(self, center_point, z_pos):
        self.pos = center_point
        self.traveled = 0.0
        self.last_depth = 0
        self.z_pos = z_pos
        self.speed = 3 - max(.01, z_pos * self.scale_mod * 2)
        scale = max(.01, 1 - (self.z_pos * self.scale_mod))
        w, h = self.size
        new_size = (int(w * scale), int(h * scale))
        self.images = cycle([pg.transform.scale(img, new_size) for img in self.bases])
        self.image = next(self.images)
        back_shade = 255 - int(self.z_pos * 2)
        deep_shade =  max(0, self.pos[1] // 10)
        shade = max(0, back_shade - deep_shade)
        color = (shade, shade, shade)
        self.image = shaded_image(self.image, color)
        self.rect = self.image.get_rect(center=self.pos)
        self.freq = 80
        self.elapsed = 0.0
        self.done = False
        
    def update(self, dt):
        self.elapsed += dt

        self.pos = self.pos[0], self.pos[1] - self.speed
        self.rect.center = self.pos
        if self.elapsed >= self.freq:
            self.elapsed -= self.freq
            self.image = next(self.images)
            back_shade = 255 - int(self.z_pos * 2)
            deep_shade =  max(0, self.pos[1] // 10)
            shade = max(0, back_shade - deep_shade)
            color = (shade, shade, shade)
            self.image = shaded_image(self.image, color)
            self.rect = self.image.get_rect(center = self.pos)
        
        if self.rect.bottom < -10:
            self.done = True
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)