from random import randint, choice
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (ObjectProperty, NumericProperty, ReferenceListProperty)
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector


class PongBall(Widget):

    vx = NumericProperty(0)
    vy = NumericProperty(0)
    velocity = ReferenceListProperty(vx, vy) # vx and vy updates when velocity is changed
        
    def move_ball(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongPaddle(Widget):
        
    # Blank paddle with 0 points to start
    score = NumericProperty(0)

    def hit_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            #manipulate this
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            vel = Vector(-1 * vx, vy) * 1.1
            ball.velocity = vel.x, vel.y + offset

class PongWidget(Widget):
    ball = ObjectProperty(None)
    playerL = ObjectProperty(None)
    playerR = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._keyboard = Window.request_keyboard(self._on_keyboard_close, self)
        self._keyboard.bind(on_key_down = self._on_key_down)
        self._keyboard.bind(on_key_up = self._on_key_up)

        # Tracks currently pressed keys, allows multiple keys to be registered at once
        self.pressed_keys = set()
        self.start_flag = False

        # Want to execute "move_bars" every frame
        Clock.schedule_interval(self.move_bars, 0)
    
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
        step_size = 300 * dt

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

    def serve_ball(self, vel=(4,0)):
        self.ball.center = self.center
        self.playerL.center_y = self.center_y
        self.playerR.center_y = self.center_y
        self.ball.velocity = vel

    def update_ball(self, dt):
        self.ball.move_ball()

        # Hit paddles
        self.playerL.hit_ball(self.ball)
        self.playerR.hit_ball(self.ball)

        # Hit top/bottom (self.ball.y is the very bottom of the square)
        if (self.ball.top >= self.top) or (self.ball.y <= self.y):

            # Note the _y, part of the syntax for ReferenceListProperty
            self.ball.velocity[1] *= -1
            
        # Score
        if (self.ball.x <= self.x): #playerR wins
            self.playerR.score += 1
            self.serve_ball()
        if (self.ball.x + self.ball.width >= self.width): #playerL wins
            self.playerL.score += 1
            self.serve_ball()

class PongApp(App):
    def build(self):
        game = PongWidget()
        game.serve_ball()
        Clock.schedule_interval(game.update_ball, 1/60) # Moves the ball every 1/60th of a second
        return game

if __name__ == "__main__":
    app = PongApp()
    app.run()