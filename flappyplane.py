import random
import struct
import json
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.atlas import Atlas
from kivy.core.audio import SoundLoader

W, H = 800.0, 480.0
WW = Window.size[0] * 1.0
WH = Window.size[1] * 1.0
X_RATIO = WW / W
Y_RATIO = WH / H
RATIO = max(X_RATIO, Y_RATIO)

SFX_FLAP = SoundLoader.load('flap.wav')
SFX_SCORE = SoundLoader.load('score.wav')
SFX_DIE = SoundLoader.load('die.wav')


def offset(pos, obj):
    x, y = pos
    size = obj.texture.size
    y = size[1] - 1 - y
    return (x + y * size[0]) * 4


def get_alpha_value(pos, obj):
    if obj.texture.size[0] > pos[0] > 0 and obj.texture.size[1] > pos[1] > 0:
        return struct.unpack_from('4B', obj.pixel_data, offset(pos, obj))[3]


class MyImage(Image):
    def __init__(self, **kwargs):
        args = kwargs
        if 'source' in args:
            _img = CoreImage.load(args['source'], keep_data=True)
            _size = (_img.texture.size[0] * RATIO, _img.texture.size[1] * RATIO)
            super(MyImage, self).__init__(size=_size)
            for attr in args:
                setattr(self, attr, args[attr])
        else:
            super(MyImage, self).__init__(**kwargs)
        self.pixel_data = self.texture.pixels


class Background(Widget):
    def __init__(self, **kwargs):
        super(Background, self).__init__()
        self.o_sprite = MyImage(**kwargs)
        self.d_sprite = MyImage(**kwargs)
        self.d_sprite.x = self.o_sprite.width
        self.add_widget(self.o_sprite)
        self.add_widget(self.d_sprite)
        self.size = (self.o_sprite.size[0] * 2, self.o_sprite.size[1] * 2)

    def update(self):
        self.o_sprite.x -= 1 * X_RATIO
        self.d_sprite.x -= 1 * X_RATIO
        if self.o_sprite.right <= 0:
            self.o_sprite.x = 0
            self.d_sprite.x = self.o_sprite.width


class Obstacle(MyImage):
    def __init__(self, p, scene):
        self.p = p
        self.scene = scene
        if self.p == 'up':
            self.source = 'atlas://img/{}Down'.format(self.scene)
            self.top = WH + random.randint(50, 100) * Y_RATIO
            super(Obstacle, self).__init__(allow_stretch=True, size_hint=(None, None), source=self.source, x=WW,
                                           top=self.top)
        elif self.p == 'down':
            self.source = 'atlas://img/{}'.format(self.scene)
            self.y = 0 - random.randint(50, 100) * Y_RATIO
            super(Obstacle, self).__init__(allow_stretch=True, size_hint=(None, None), source=self.source, x=WW,
                                           y=self.y)

    def update(self):
        self.x -= 1 * X_RATIO
        if self.right <= 0:
            self.parent.remove_widget(self)


class ObstacleGroup(Widget):
    def __init__(self, scene):
        super(ObstacleGroup, self).__init__()
        self.size_hint = (None, None)
        self.scene = scene
        self.time = 0

    def update(self):
        for child in self.children:
            child.update()
        self.time += 1
        if self.time % 400 == 1:
            self.add_widget(Obstacle('up', self.scene))
            self.add_widget(Obstacle('down', self.scene))
        if self.time % 400 == 250:
            self.add_widget(Star())


class Star(MyImage):
    def __init__(self):
        image_dict = {}
        for i, j in zip([3, 2, 1], ['Gold', 'Silver', 'Bronze']):
            image_dict[i] = 'atlas://img/star{}'.format(j)
        choice = random.randint(1, 3)
        self.score = choice
        _source = image_dict[choice]
        super(Star, self).__init__(source=_source, allow_stretch=True, size_hint=(None, None), x=WW,
                                   y=random.uniform(0.25, 0.75) * WH)

    def update(self):
        self.x -= 1 * X_RATIO
        if self.right <= 0:
            self.parent.remove_widget(self)


class Player(MyImage):
    def __init__(self):
        img = ['atlas://img/planeBlue1', 'atlas://img/planeGreen1', 'atlas://img/planeRed1', 'atlas://img/planeYellow1']
        _source = random.choice(img)
        super(Player, self).__init__(source=_source, allow_stretch=True, size_hint=(None, None),
                                     center=(WW / 2, WH / 2))
        self.velocity = 0
        self.gravity = -0.1 * Y_RATIO

    def update(self):
        self.velocity += self.gravity
        self.velocity = max(self.velocity, - 10 * Y_RATIO)
        self.y += self.velocity

    def check_pixel_collison(self, obj):
        if obj.collide_point(self.x, self.top):
            collide_point = (2, 53)
        elif obj.collide_point(self.right, self.top):
            collide_point = (82, 53)
        elif obj.collide_point(self.x, self.y):
            collide_point = (2, 53)
        elif obj.collide_point(self.right, self.y):
            collide_point = (82, 11)
        else:
            collide_point = (44, 36)
        point_x, point_y = collide_point[0] * RATIO, collide_point[1] * RATIO
        a, b = self.to_parent(point_x, point_y, True)
        c, d = obj.to_widget(a, b, True)
        pos = int(c / RATIO), int(d / RATIO)
        if get_alpha_value(pos, obj) == 255:
            return True

        if obj.__class__ == Obstacle:
            if obj.p == 'up':
                collide_point = (66, 4)
            elif obj.p == 'down':
                collide_point = (66, 236)
            point_x, point_y = collide_point[0] * RATIO, collide_point[1] * RATIO
            a, b = obj.to_parent(point_x, point_y, True)
            c, d = self.to_widget(a, b, True)
            pos = int(c / RATIO), int(d / RATIO)
            if get_alpha_value(pos, self) == 255:
                return True

    def check_pixel_collison_with_ground(self, obj):
        if self.center_y >= WH / 2.0:
            collide_point = (44, 73)
        else:
            collide_point = (58, 2)
        point_x, point_y = collide_point[0] * RATIO, collide_point[1] * RATIO
        a, b = self.to_parent(point_x, point_y, True)
        c, d = obj.to_widget(a, b, True)
        pos = int(c / RATIO), int(d / RATIO)
        if get_alpha_value(pos, obj) == 255:
            return True

    def on_touch_down(self, touch):
        SFX_FLAP.play()
        self.velocity = 2 * Y_RATIO


class GameScreen(Screen):
    def on_enter(self, *args):
        self.init()

    def on_leave(self, *args):
        self.run.cancel()
        self.clear_widgets()

    def start(self, *args):
        self.run = Clock.schedule_interval(self.update, 1.0 / 60.0)

    def init(self):
        scene = random.choice(['Dirt', 'Grass', 'Ice', 'Rock'])
        rock_scene = random.choice(['rock', 'rockGrass', 'rockIce', 'rockSnow'])
        self.manager.score = 0
        self.background = Background(allow_stretch=True, size_hint=(None, None), source='atlas://img/background')
        self.ground = Background(allow_stretch=True, size_hint=(None, None),
                                 source='atlas://img/ground{}'.format(scene))
        self.sky = Background(allow_stretch=True, size_hint=(None, None),
                              source='atlas://img/ground{}down'.format(scene), top=WH)
        self.obstacles = ObstacleGroup(rock_scene)
        self.player = Player()
        self.label = Label(text=str(self.manager.score), font_size=40*RATIO, size_hint=(None, None), x=0, top=WH,
                           font_name='kenvector_future_thin.ttf')

        self.hint = MyImage(allow_stretch=True, size_hint=(None, None), source='atlas://img/textGetReady',
                            center_x=WW / 2, center_y=WH / 2)

        anim = Animation(center_x=WW / 2, y=WH, d=0.8)
        anim.bind(on_complete=self.start)
        self.add_widget(self.background)
        self.add_widget(self.obstacles)
        self.add_widget(self.ground)
        self.add_widget(self.sky)
        self.add_widget(self.player)
        self.add_widget(self.label)
        self.add_widget(self.hint)
        anim.start(self.hint)

    def on_touch_down(self, touch):
        self.player.on_touch_down(touch)

    def update(self, dt):
        if not self.check_collide():
            self.check_collide()
            self.background.update()
            self.sky.update()
            self.ground.update()
            self.obstacles.update()
            self.player.update()
        else:
            self.manager.current = 'END'

    def check_collide(self):
        for ground in self.ground.children:
            if self.player.collide_widget(ground):
                if self.player.check_pixel_collison_with_ground(ground):
                    SFX_DIE.play()
                    return True
        for sky in self.sky.children:
            if self.player.collide_widget(sky):
                if self.player.check_pixel_collison_with_ground(sky):
                    SFX_DIE.play()
                    return True
        for obstacle in self.obstacles.children:
            if self.player.collide_widget(obstacle):
                if obstacle.__class__ == Star:
                    SFX_SCORE.play()
                    self.manager.score += obstacle.score
                    self.obstacles.remove_widget(obstacle)
                    self.label.text = str(self.manager.score)
                else:
                    if self.player.check_pixel_collison(obstacle):
                        return True


class Tap(MyImage):
    def __init__(self, **kwargs):
        self.images = ['atlas://img/tap', 'atlas://img/tapTick']
        self.source = self.images[0]
        super(Tap, self).__init__(allow_stretch=True, size_hint=(None, None), source=self.source, x=WW / 3 * 2,
                                  y=WH / 7)
        self.frame = 0

    def update(self):
        self.frame += 1
        if self.frame % 16 == 0:
            self.source = self.images[0]
        elif self.frame % 16 == 8:
            self.source = self.images[1]


class TitleScreen(Screen):
    def on_enter(self, *args):
        self.init()

    def on_leave(self, *args):
        self.run.cancel()
        self.clear_widgets()

    def init(self):
        self.background = Background(allow_stretch=True, size_hint=(None, None), source='atlas://img/background')
        self.add_widget(self.background)
        for letter, pos_x, pos_y in zip('FLAPPYPLANE', (
                    WW / 14, WW / 14 * 2, WW / 14 * 3, WW / 14 * 4, WW / 14 * 5, WW / 14 * 6, WW / 14 * 5, WW / 14 * 6,
                    WW / 14 * 7, WW / 14 * 8, WW / 14 * 9), (
                                                        WH / 3 * 2, WH / 3 * 2, WH / 3 * 2, WH / 3 * 2, WH / 3 * 2,
                                                        WH / 3 * 2,
                                                        WH / 2, WH / 2, WH / 2, WH / 2, WH / 2)):
            self.add_widget(MyImage(allow_stretch=True, size_hint=(None, None), x=pos_x, y=pos_y,
                                    source='atlas://img/letter{}'.format(letter)))
        self.add_widget(MyImage(allow_stretch=True, size_hint=(None, None), center_x=WW / 2, center_y=WH / 3,
                                source='atlas://img/planeYellow1'))
        self.add_widget(
            MyImage(allow_stretch=True, size_hint=(None, None), center_x=WW / 3 * 2, center_y=WH / 3,
                    source='atlas://img/tapLeft'))
        self.add_widget(
            MyImage(allow_stretch=True, size_hint=(None, None), center_x=WW / 3, center_y=WH / 3,
                    source='atlas://img/tapRight'))

        self.tap = Tap()
        self.add_widget(self.tap)
        self.run = Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_touch_down(self, touch):
        self.manager.current = 'GAME'

    def update(self, dt):
        if self.manager.current == 'TITLE':
            self.background.update()
            self.tap.update()


class EndScreen(Screen):
    def on_enter(self, *args):
        with open('record.json', 'r') as f:
            self.record = json.load(f)
        self.init()

    def on_leave(self, *args):
        self.clear_widgets()
        with open('record.json', 'w') as f:
            json.dump(self.record, f)

    def init(self):
        self.background = Background(allow_stretch=True, size_hint=(None, None), source='atlas://img/background')
        self.add_widget(self.background)
        image = MyImage(source='atlas://img/textGameOver', allow_stretch=True, size_hint=(None, None), center_x=WW / 2,
                        center_y=WH / 4 * 3)
        self.add_widget(image)
        if self.manager.score >= self.record[0]:
            self.medal = 'atlas://img/medalGold'
            self.medal_image = MyImage(source=self.medal, allow_stretch=True, size_hint=(None, None), center_x=WW / 4,
                                       center_y=WH / 2)
            self.add_widget(self.medal_image)
            self.record = [self.manager.score, self.record[0], self.record[1]]
        elif self.manager.score >= self.record[1]:
            self.medal = 'atlas://img/medalSilver'
            self.record = [self.record[0], self.manager.score, self.record[1]]
            self.medal_image = MyImage(source=self.medal, allow_stretch=True, size_hint=(None, None), center_x=WW / 4,
                                       center_y=WH / 2)

            self.add_widget(self.medal_image)
        elif self.manager.score >= self.record[2]:
            self.medal = 'atlas://img/medalBronze'
            self.record = [self.record[0], self.record[1], self.manager.score]
            self.medal_image = MyImage(source=self.medal, allow_stretch=True, size_hint=(None, None), center_x=WW / 4,
                                       center_y=WH / 2)
            self.add_widget(self.medal_image)
        label = Label(text=str(self.manager.score), font_size=150*RATIO, size_hint=(None, None), center_x=WW / 2,
                      center_y=WH / 2,
                      font_name='kenvector_future_thin.ttf')
        self.add_widget(label)

    def on_touch_down(self, touch):
        self.manager.current = 'GAME'


class StateMachine(ScreenManager):
    score = NumericProperty(0)


sm = StateMachine()
sm.add_widget(TitleScreen(name='TITLE'))
sm.add_widget(GameScreen(name='GAME'))
sm.add_widget(EndScreen(name='END'))
sm.current = 'TITLE'


class FlappyPlaneApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    FlappyPlaneApp().run()
