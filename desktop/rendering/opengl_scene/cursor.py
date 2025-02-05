from PyQt6.QtCore import QPoint


class CursorLogic:
    static_clicks_counter : int = 0
    current_location : QPoint = None
    last_location : QPoint = None
    last_location_pressed : QPoint = None
    is_mouse_pressed : bool = False
    was_mouse_pressed : bool = False # During previous frame
    cursor_movement_epsilon : int = 5 # pixels

    def __init__(self, widget_cur_pos) -> None:
        self.current_location = widget_cur_pos
        self.last_location = self.current_location
        self.last_location_pressed = self.current_location

    def update(self, widget_cur_pos, is_mouse_pressed):
        # Update history
        if self.been_pressed():
            if not self.is_dragging():
                self.static_clicks_counter += 1
            else:
                self.static_clicks_counter = 0
            self.last_location_pressed = self.current_location
        self.last_location = self.current_location
        self.was_mouse_pressed = self.is_mouse_pressed

        # Get new state
        self.current_location = widget_cur_pos
        self.is_mouse_pressed = is_mouse_pressed

    def delta(self):
        return self.current_location - self.last_location
    
    def is_dragging(self):
        return (self.last_location_pressed - self.current_location).manhattanLength() > self.cursor_movement_epsilon

    def been_pressed(self):
        return not self.was_mouse_pressed and self.is_mouse_pressed
    
    def been_released(self):
        return self.was_mouse_pressed and not self.is_mouse_pressed