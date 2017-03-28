import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rotate
from kivy.uix.screenmanager import ScreenManager, Screen

W, H = 800.0, 480.0
WW = Window.size[0]
WH = Window.size[1]
X_SPEED_RATIO = WW / W
Y_SPEED_RATIO = WH / H


def window_size(obj):
    size = obj.texture_size
    ratio = max(WW / W, WH / H)
    return (ratio * size[0], ratio * size[1])


class Background(Widget):
    def __init__(self, **kwargs):
        super(Background, self).__init__()
        self.o_sprite = Image(**kwargs)
        self.o_sprite.size = window_size(self.o_sprite)
        self.d_sprite = Image(**kwargs)
        self.d_sprite.size = window_size(self.d_sprite)
        self.d_sprite.x = self.o_sprite.width
        self.add_widget(self.o_sprite)
        self.add_widget(self.d_sprite)

    def update(self):
        self.o_sprite.x -= 1 * X_SPEED_RATIO
        self.d_sprite.x -= 1 * X_SPEED_RATIO
        if self.o_sprite.right <= 0:
            self.o_sprite.x = 0
            self.d_sprite.x = self.o_sprite.width


class Obstacle(Image):
    def __init__(self, **kwargs):
        super(Obstacle, self).__init__(**kwargs)
        self.size = window_size(self)

    def update(self):
        self.x -= 1 * X_SPEED_RATIO
        if self.right <= 0:
            self.parent.remove_widget(self)


class ObstacleGroup(Widget):
    def __init__(self):
        super(ObstacleGroup, self).__init__()
        self.time = 0

    def update(self):
        for child in self.children:
            child.update()
        self.time += 1
        if self.time % 400 == 1:
            r = int(random.randint(0, 50)) * X_SPEED_RATIO
            print(WW,X_SPEED_RATIO,r)
            self.add_widget(
                Obstacle(source='rockGrass.png', x= WW + r,
                         y=random.randint(-80, 5) * Y_SPEED_RATIO))

            self.add_widget(
                Obstacle(source='rockGrassDown.png', x= WW + r,
                         center_y = WH - random.randint(100, 200) * X_SPEED_RATIO))


class Player(Image):
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        self.size = window_size(self)
        self.velocity = 0
        self.gravity = -0.1 * Y_SPEED_RATIO

    def update(self):
        self.velocity += self.gravity
        self.velocity = max(self.velocity, - 10 * Y_SPEED_RATIO)
        self.y += self.velocity

    def on_touch_down(self, touch):
        self.velocity = 4 * Y_SPEED_RATIO


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.background = Background(allow_stretch=True, size_hint=(None, None), source='background.png', pos=(0, 0))

        self.ground = Background(allow_stretch=True, size_hint=(None, None), source='groundGrass.png', pos=(0, 0))

        self.sky = Background(allow_stretch=True, size_hint=(None, None), source='skyGrass.png', x=0, center_y =WH)
        # I do not why the top = Window.size[1] would cause a margin



        self.obstacles = ObstacleGroup()

        self.player = Player(source='planeBlue1.png', allow_stretch=True, size_hint=(None, None), center=(WW/2.0,WH/2.0))
        self.add_widget(self.background)
        self.add_widget(self.obstacles)
        self.add_widget(self.ground)
        self.add_widget(self.sky)
        self.add_widget(self.player)

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_touch_down(self, touch):
        self.player.on_touch_down(touch)

    def update(self, dt):
        self.background.update()
        self.sky.update()
        self.ground.update()
        self.obstacles.update()
        self.player.update()


class TitleScreen(Screen):
    pass


class EndScreen(Screen):
    pass


sm = ScreenManager()
sm.add_widget(TitleScreen(name='TITLE'))
sm.add_widget(GameScreen(name='GAME'))
sm.add_widget(EndScreen(name='END'))
sm.current = 'GAME'


class FlappyPlaneApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    FlappyPlaneApp().run()
