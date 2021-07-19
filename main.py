from random import randint, uniform
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (ObjectProperty, NumericProperty, ReferenceListProperty)
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.animation import Animation
from functools import partial


class PongBall(Widget):
    '''
    Attributes:
        vx: ball's horizontal velocity
        vy: ball's vertical velocity
        velocity: contains both vx and vy
    '''
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    velocity = ReferenceListProperty(vx, vy) # vx and vy updates when velocity is changed
        
    def move_ball(self):
        '''
        Translates the ball using its current velocity based on its current location
        '''
        self.pos = Vector(*self.velocity) + self.pos

class PongPaddle(Widget):
    '''
    Rectangles that hit the ball.

    Attributes:
        score: the score of the player controlling that paddle.
    '''

    # Blank paddle with 0 points to start
    score = NumericProperty(0)

    def hit_ball(self, ball):
        '''
        Checks if the paddle is hitting the ball. Deflects ball if collision is detected.

        Args:
            ball: a object of class PongBall
        '''

        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2) # How much ball moves up/down after hitting paddle
            ball.velocity = -1*vx, vy + offset

class PowerUp(Widget):
    '''
    A small square that appears randomly and lengthen's a player's paddle if the ball is hit by
    that player into the powerup.
    '''

    def spawn_pu(self, p_wid, dt):
        '''
        Spawns a powerup at a random location
        
        Args:
            p_wid: an object of class PongWidget
        '''
        
        self.x = uniform(p_wid.width/6, p_wid.width/6*5)
        self.y = uniform(p_wid.top/6, p_wid.top/6*5)

    def hit_lengthen(self, ball, p_wid):
        '''
        Applies powerup; lengthens a player's paddle for 10s
        
        Args:
            ball: an object of class PongBall
            p_wid: an object of class PongWidget
        '''
        if (self.collide_widget(ball)):
            l_factor = 1.3 # How much to lengthen by
            vx = ball.velocity[0]
            
            if (vx < 0): # Player R gets power up
                p_wid.playerR.size[1] *= l_factor
                Clock.schedule_once(partial(self.revert_eff, p_wid.playerR, l_factor), 10) # Reverts effect after 10s
            else:
                p_wid.playerL.size[1] *= l_factor
                Clock.schedule_once(partial(self.revert_eff, p_wid.playerL, l_factor), 10)

            self.y = p_wid.top + 50
            
    def revert_eff(self, player, l_factor, dt):
        '''
        Shorten's the player's paddle back to normal

        Args:
            player: an object of class PongPaddle
            l_factor: the amount to shrink paddle by
        '''
        player.size[1] /= l_factor


class PongWidget(Widget):
    '''
    Main widget of the game; handles starting/restarting the game, taking keyboard input, and updating the ball and paddles' positions.

    Attributes:
        ball: an object of class PongBall
        playerL/R: left/right players, objects of class PongPaddle
        power: an object of class PowerUp
        gover_msg: gameover label
    '''
    ball = ObjectProperty(None)
    playerL = ObjectProperty(None)
    playerR = ObjectProperty(None)
    power = ObjectProperty(None)
    gover_msg = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Need custom functions for pressing/releasing keys
        self._keyboard = Window.request_keyboard(self._on_keyboard_close, self)
        self._keyboard.bind(on_key_down = self._on_key_down)
        self._keyboard.bind(on_key_up = self._on_key_up)

        # Tracks currently pressed keys, allows multiple keys to be registered at once
        self.pressed_keys = set()

        # Flasing animation for game over screen
        self.gover_anim = Animation(opacity = 1, duration = 1) + Animation(opacity = 0, duration = 1)
        self.gover_anim.repeat = True
        self.over_flag = False

    def _on_keyboard_close(self):
        self._keyboard.unbind(on_key_down = self._on_key_down)
        self._keyboard.unbind(on_key_up = self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        '''The set is where we check for pressed keys'''

        self.pressed_keys.add(text)

    def _on_key_up(self, keyboard, keycode):
        '''Immediately remove key if no longer pressed'''

        text = keycode[1]
        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def keyboard_input(self, dt):
        '''
        Takes all keyboard input and updates player location/restarts game 
        '''
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

        if ('r' in self.pressed_keys and self.over_flag is True): # Restarts only if game is already over
            self.over_flag = False
            Animation.cancel(self.gover_anim, self.gover_msg)
            self.playerL.score = 0
            self.playerR.score = 0
            self.gover_msg.color = 1,0,0,0
            self.serve_ball()

    def serve_ball(self, vel=(8,0)):
        '''
        Serves ball starting from the center with no vertical velocity.

        Args:
            vel: the initial ball velocity
        '''
        self.ball.center = self.center
        self.playerL.center_y = self.center_y
        self.playerR.center_y = self.center_y
        self.ball.velocity = vel

    def game_over(self):
        '''
        Starts flashing game-over screen animation
        '''
        self.ball.center = self.center
        self.ball.velocity = (0,0)
        self.gover_msg.color = 1, 0, 0, 1
        self.gover_anim.start(self.gover_msg)
            
    def update_game(self, dt):
        '''
        Checks for ball collision, powerup collision, winning points/game over, and updates the game in responce.  
        '''
        self.ball.move_ball()

        # Hit paddles
        self.playerL.hit_ball(self.ball)
        self.playerR.hit_ball(self.ball)

        # Hit top/bottom (self.ball.y is the very bottom of the square)
        if (self.ball.top >= self.top) or (self.ball.y <= self.y):
            self.ball.velocity[1] *= -1
            
        # Score
        if (self.ball.x < self.x): # playerR wins
            self.playerR.score += 1
            if (self.playerR.score == 5):
                self.over_flag = True
                self.game_over()
            else:
                self.serve_ball()

        if (self.ball.x > self.width): # playerL wins
            self.playerL.score += 1
            if (self.playerL.score == 5):
                self.over_flag = True
                self.game_over()
            else:
                self.serve_ball()

        # Power-up collision
        self.power.hit_lengthen(self.ball, self)

class PongApp(App):
    '''
    Kivy base app class
    '''
    def build(self):
        game = PongWidget()
        Clock.schedule_interval(game.keyboard_input, 0) # Get keyboard input every frame
        game.serve_ball()
        Clock.schedule_interval(game.update_game, 1/60) # Moves and checks the ball every 1/60th of a second

        # Spawn power-up at random times
        Clock.schedule_interval(partial(game.power.spawn_pu, game), randint(6, 12))
        return game

if __name__ == "__main__":
    app = PongApp()
    app.run()