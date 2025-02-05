from dataclasses import dataclass
from time import time

@dataclass
class AnimationMetadata:
    start_val : object
    end_val : object
    start_time : int
    duration : int
    ease_func : object # Function
    ready_to_start : bool # For synchronization purposes
    finished : bool # For optimisation purposes

class AnimationProperty:
    def __init__(self) -> None:
        super(AnimationProperty, self).__setattr__("animatables", dict())

    def create_anim(self, prop, duration, ease_func):
        value = self.__getattribute__(prop)
        self.animatables[prop] = AnimationMetadata(value, value, 0, duration, ease_func, False, True)

    def __setattr__(self, name: str, value) -> None:
        if name in self.animatables.keys():
            self.animatables[name].start_val = self.__getattribute__(name)
            self.animatables[name].end_val = value
            self.animatables[name].finished = False
            self.animatables[name].ready_to_start = True
        else:
            super(AnimationProperty, self).__setattr__(name, value)

    def update(self):
        for anim in self.animatables.keys():
            if self.animatables[anim].ready_to_start:
                self.animatables[anim].start_time = time()
                self.animatables[anim].ready_to_start = False
                continue
            if not self.animatables[anim].finished and self.animatables[anim].start_time + self.animatables[anim].duration > time():
                coef = (time() - self.animatables[anim].start_time) / self.animatables[anim].duration
                super(AnimationProperty, self).__setattr__(anim, self.animatables[anim].ease_func(self.animatables[anim].start_val, self.animatables[anim].end_val, coef))
            else:
                super(AnimationProperty, self).__setattr__(anim, self.animatables[anim].end_val)
                self.animatables[anim].finished = True

    @staticmethod
    def ease_linear(start, stop, delta):
        return (1 - delta) * start + delta * stop
    
    @staticmethod
    def ease_sqrt(start, stop, delta):
        delta **= 0.3
        return AnimationProperty.ease_linear(start, stop, delta)
