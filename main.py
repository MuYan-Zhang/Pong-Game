from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock

class PongWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_close, self)
        self._keyboard.bind(on_key_down = self._on_key_down)
        self._keyboard.bind(on_key_up = self._on_key_up)

        # Left and right bars
        with self.canvas:
            self.playerL = Rectangle(pos=(50, 0.5), size = (15, 100))
            self.playerR = Rectangle(pos=(800, 0.5), size = (15, 100))

        # Tracks currently pressed keys, allows multiple keys to be registered at once
        self.pressed_keys = set()

        Clock.schedule_interval(self.move_bars, 0) # Want to execute "move_bars" every frame

    def _on_keyboard_close(self):
        self._keyboard.unbind(on_key_down = self._on_key_down)
        self._keyboard.unbind(on_key_up = self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.pressed_keys.add(text)

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.pressed_keys:
            self.pressed_keys.remove(text)
        
    def move_bars(self, dt):
        currentL_x = self.playerL.pos[0]; currentL_y = self.playerL.pos[1]
        currentR_x = self.playerR.pos[0]; currentR_y = self.playerR.pos[1]

        # Ensures uniform pixels/sec for different screen frame rates
        step_size = 200 * dt

        if 'w' in self.pressed_keys:
            currentL_y += step_size
        if 's' in self.pressed_keys:
            currentL_y -= step_size
        if 'i' in self.pressed_keys:
            currentR_y += step_size
        if 'k' in self.pressed_keys:
            currentR_y -= step_size

        self.playerL.pos = (currentL_x, currentL_y)
        self.playerR.pos = (currentR_x, currentR_y)

class PongApp(App):
    def build(self):
        return PongWidget()

if __name__ == "__main__":
    app = PongApp()
    app.run()