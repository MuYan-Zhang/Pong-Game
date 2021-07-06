from random import randint, uniform
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (ObjectProperty, NumericProperty, ReferenceListProperty)
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.animation import Animation
from math import sqrt
from time import sleep
from functools import partial

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
            # print("hitting x coord: {}".format(ball.x))
            vx, vy = ball.velocity
            # print("vx1: {}, vy1: {}, mag1: {}".format(vx, vy, sqrt(vx**2 + vy**2)))
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            ball.velocity = -1*vx, vy + offset
            # print("final ball velocity: {}".format(ball.velocity))

class PowerUp(Widget):

    def spawn_pu(self, p_wid, dt):
        self.x = uniform(p_wid.width/6, p_wid.width/6*5)
        self.y = uniform(p_wid.top/6, p_wid.top/6*5)

    def hit_lengthen(self, ball, p_wid):
        if (self.collide_widget(ball)):
            l_factor = 1.3 # How much to lengthen by
            vx = ball.velocity[0]
            
            if (vx < 0): # Player R gets power up
                p_wid.playerR.size[1] *= l_factor
                Clock.schedule_once(partial(self.revert_eff, p_wid.playerR, l_factor), 10)
            else:
                p_wid.playerL.size[1] *= l_factor
                Clock.schedule_once(partial(self.revert_eff, p_wid.playerL, l_factor), 10)

            self.y = p_wid.top + 50
            
    def revert_eff(self, player, l_factor, dt):
        player.size[1] /= l_factor


class PongWidget(Widget):
    ball = ObjectProperty(None)
    playerL = ObjectProperty(None)
    playerR = ObjectProperty(None)
    power = ObjectProperty(None)
    gover_msg = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._keyboard = Window.request_keyboard(self._on_keyboard_close, self)
        self._keyboard.bind(on_key_down = self._on_key_down)
        self._keyboard.bind(on_key_up = self._on_key_up)

        # Tracks currently pressed keys, allows multiple keys to be registered at once
        self.pressed_keys = set()
        self.gover_anim = Animation(opacity = 1, duration = 1) + Animation(opacity = 0, duration = 1)
        self.gover_anim.repeat = True
        self.over_flag = False

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

    def keyboard_input(self, dt):
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

        if ('r' in self.pressed_keys and self.over_flag is True): #Restarts game
            self.over_flag = False
            Animation.cancel(self.gover_anim, self.gover_msg)
            self.playerL.score = 0
            self.playerR.score = 0
            self.gover_msg.color = 1,0,0,0
            self.serve_ball()

    def serve_ball(self, vel=(8,0)):
        self.ball.center = self.center
        self.playerL.center_y = self.center_y
        self.playerR.center_y = self.center_y
        self.ball.velocity = vel

    def game_over(self): # Game over screen, starts the flashing text animation
        self.ball.center = self.center
        self.ball.velocity = (0,0)
        self.gover_msg.color = 1, 0, 0, 1
        self.gover_anim.start(self.gover_msg)
            
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
        if (self.ball.x < self.x): #playerR wins
            # print("playerR winning velocity: {}".format(self.ball.velocity))
            # print("playerR winning x coord: {}".format(self.ball.x))
            self.playerR.score += 1
            if (self.playerR.score == 5): #let user set game rounds later
                self.over_flag = True
                self.game_over()
            else:
                self.serve_ball()

        if (self.ball.x > self.width): #playerL wins
            self.playerL.score += 1
            if (self.playerL.score == 5): #let user set game rounds later
                self.over_flag = True
                self.game_over()
            else:
                self.serve_ball()

        self.power.hit_lengthen(self.ball, self)

class PongApp(App):
    def build(self):
        game = PongWidget()
        Clock.schedule_interval(game.keyboard_input, 0) # Want to execute "keyboard_input" every frame
        game.serve_ball()
        Clock.schedule_interval(game.update_ball, 1/60) # Moves and checks the ball every 1/60th of a second
        
        # Spawn power up at random spot, then in random intervals
        game.power.spawn_pu(game, None)
        Clock.schedule_interval(partial(game.power.spawn_pu, game), randint(6, 12))
        return game

if __name__ == "__main__":
    app = PongApp()
    app.run()