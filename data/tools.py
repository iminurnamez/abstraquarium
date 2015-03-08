import os
import json
import pygame as pg


class Control(object):
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.show_fps = True
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.fullscreen = False
        self.dt = 0.0

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.dt)
        pg.display.set_caption("{}".format(self.clock.get_fps()))

    def flip_state(self):
        previous,self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(persist)
        self.state.previous = previous

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_fullscreen(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            self.state.get_event(event)
    
    def toggle_fullscreen(self, key):
        if key == pg.K_f:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                self.screen = pg.display.set_mode(self.screen.get_rect().size, pg.FULLSCREEN)
            else:
                self.screen = pg.display.set_mode(self.screen.get_rect().size)
    
    def main(self):
        while not self.done:
            self.dt = self.clock.tick(self.state.fps)
            self.event_loop()
            self.update()
            pg.display.update()
            

class _State(object):
    def __init__(self):
        self.fps = 30
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}

    def get_event(self, event):
        pass

    def startup(self, persistent):
        self.persist = persistent

    def cleanup(self):
        self.done = False
        return self.persist

    def update(self, surface, keys):
        pass
        
        
class _KwargMixin(object):
    """
    Useful for classes that require a lot of keyword arguments for
    customization.
    """
    def process_kwargs(self, name, defaults, kwargs):
        """
        Arguments are a name string (displayed in case of invalid keyword);
        a dictionary of default values for all valid keywords;
        and the kwarg dict.
        """
        settings = copy.deepcopy(defaults)
        for kwarg in kwargs:
            if kwarg in settings:
                if isinstance(kwargs[kwarg], dict):
                    settings[kwarg].update(kwargs[kwarg])
                else:
                    settings[kwarg] = kwargs[kwarg]
            else:
                message = "{} has no keyword: {}"
                raise AttributeError(message.format(name, kwarg))
        for setting in settings:
            setattr(self, setting, settings[setting])
            

def load_all_gfx(directory,colorkey=(0,0,0),accept=(".png",".jpg",".bmp")):
    graphics = {}
    for pic in os.listdir(directory):
        name,ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics

def load_all_music(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    songs = {}
    for song in os.listdir(directory):
        name,ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs
            
def load_all_sfx(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    effects = {}
    for fx in os.listdir(directory):
        name,ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects

def load_all_fonts(directory, accept=(".ttf")):
    return load_all_music(directory, accept)
    
def strip_from_sheet(sheet, start, size, columns, rows=1):
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0]+size[0]*i, start[1]+size[1]*j)
            frames.append(sheet.subsurface(pg.Rect(location, size)))
    return frames
    

