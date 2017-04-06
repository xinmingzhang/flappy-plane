import random
import struct
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock, ClockBase
from kivy.graphics import Mesh,Color,Rectangle,Point
from kivy.uix.screenmanager import ScreenManager, Screen


W, H = 800.0, 480.0
WW = Window.size[0]
WH = Window.size[1]
X_RATIO = WW / W
Y_RATIO = WH / H
RATIO = max(X_RATIO, Y_RATIO)




def window_size(obj):
    size = obj.texture_size
    return (RATIO * size[0], RATIO * size[1])

def offset(pos,obj):
    x,y = pos
    size = obj.texture.size
    y = size[1] - 1 - y
    return (x + y * size[0]) * 4

def get_alpha_value(pos, obj):
    if obj.texture.size[0]>=pos[0]>0 and obj.texture.size[1]>=pos[1]>0:
        return struct.unpack_from('4B',obj.texture.pixels,offset(pos,obj))[3]


class MyImage(Image):
    def __init__(self,**kwargs):
        super(MyImage,self).__init__(**kwargs)
        if self.y > 0:
            self._top = self.top
            self.size = window_size(self)
            self.top = self._top
        else:
            self.size = window_size(self)

class Background(Widget):
    def __init__(self, **kwargs):
        super(Background, self).__init__()
        self.o_sprite = MyImage(**kwargs)
        self.d_sprite = MyImage(**kwargs)
        self.d_sprite.x = self.o_sprite.width
        self.add_widget(self.o_sprite)
        self.add_widget(self.d_sprite)
        self.size = (self.o_sprite.size[0] * 2, self.o_sprite.size[1]*2)

    def update(self):
        self.o_sprite.x -= 1 * X_RATIO
        self.d_sprite.x -= 1 * X_RATIO
        if self.o_sprite.right <= 0:
            self.o_sprite.x = 0
            self.d_sprite.x = self.o_sprite.width


class Obstacle(MyImage):
    def __init__(self, p, **kwargs):
        self.p = p
        if self.p == 'up':
            self.source = 'rockGrassDown.png'
            self.top = WH + random.randint(50,100) * Y_RATIO
            super(Obstacle,self).__init__(allow_stretch=True, size_hint=(None, None),source = self.source,x = WW,top = self.top)


        elif self.p == 'down':
            self.source = 'rockGrass.png'
            self.y = 0 - random.randint(50,100) * Y_RATIO
            super(Obstacle,self).__init__(allow_stretch=True, size_hint=(None, None),source = self.source,x=WW, y=self.y)

    def update(self):
        self.x -= 1 * X_RATIO
        if self.x <=0:
            anim = Animation(x = 0,y = 0)
            anim.start(self)
        if self.right <= 0:
            self.parent.remove_widget(self)

class ObstacleGroup(Widget):
    def __init__(self):
        super(ObstacleGroup, self).__init__()
        self.size_hint = (None,None)
        self.time = 0

    def update(self):
        for child in self.children:
            child.update()
        self.time += 1
        if self.time % 400 == 1:
            self.add_widget(Obstacle('up'))
            self.add_widget(Obstacle('down'))

class Player(Image):
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        self.source = 'planeBlue1.png'
        self.allow_stretch = True
        self.size_hint = (None, None)
        self.center = (WW / 2.0, WH / 2.0)
        self.size = window_size(self)
        self.velocity = 0
        self.gravity = -0.1 * Y_RATIO
        with self.canvas:
            Color(rgba = (1,0,0,1))
            self.point1 = Point(points = self.to_parent(2* RATIO,53* RATIO,True),pointsize = 2)
            self.point2 = Point(points = self.to_parent(82* RATIO,53* RATIO,True),pointsize = 2)
            self.point3 = Point(points=self.to_parent(2* RATIO, 53* RATIO, True), pointsize=2)
            self.point4 = Point(points=self.to_parent(82* RATIO, 11* RATIO, True), pointsize=2)

    def update(self):
        self.point1.points = self.to_parent(2* RATIO,53* RATIO,True)
        self.point2.points = self.to_parent(82* RATIO, 53* RATIO, True)
        self.point3.points = self.to_parent(2* RATIO, 53* RATIO, True)
        self.point4.points = self.to_parent(82* RATIO, 11* RATIO, True)
        self.velocity += self.gravity
        self.velocity = max(self.velocity, - 10 * Y_RATIO)
        self.y += self.velocity


    def check_pixel_collison(self,obj):
        if obj.collide_point(self.x,self.top):
            collide_point = (2,53)
        elif obj.collide_point(self.right,self.top):
            collide_point = (82,53)
        elif obj.collide_point(self.x,self.y):
            collide_point = (2, 53)
        elif obj.collide_point(self.right,self.y):
            collide_point = (82,11)
        else:
            collide_point = (44,36)
        point_x, point_y = collide_point[0] * RATIO,collide_point[1]*RATIO
        a,b = self.to_parent(point_x,point_y,True)
        c,d = obj.to_widget(a,b,True)
        pos = int(c/RATIO),int(d/RATIO)
        if get_alpha_value(pos,obj) == 255:
            with self.canvas:
                Color(rgba = (0,1,0,1))
                Point(points = obj.to_parent(c,d,True), pointsize = 3)
            return True

        if obj.__class__ == Obstacle:
            if obj.p == 'up':
                collide_point = (66,4)
            elif obj.p == 'down':
                collide_point = (66,236)
            point_x, point_y = collide_point[0] * RATIO,collide_point[1]*RATIO
            a,b = obj.to_parent(point_x,point_y,True)
            c,d = self.to_widget(a,b,True)
            pos = int(c/RATIO),int(d/RATIO)
            if get_alpha_value(pos,self)==255:
                with self.canvas:
                    Color(rgba = (0,1,1,1))
                    Point(points = (a,b), pointsize = 5)
                return True

    def check_pixel_collison_with_ground(self, obj):
        if self.center_y >= WH/2.0:
            collide_point = (44,73)
        else:
            collide_point = (58,2)
        point_x, point_y = collide_point[0] * RATIO, collide_point[1] * RATIO
        a, b = self.to_parent(point_x, point_y, True)
        c, d = obj.to_widget(a, b, True)
        pos = int(c / RATIO), int(d / RATIO)
        if get_alpha_value(pos, obj) == 255:
            with self.canvas:
                Color(rgba=(0, 1, 0, 1))
                Point(points=obj.to_parent(c, d, True), pointsize=5)
            return True


    def on_touch_down(self, touch):
        self.velocity = 2 * Y_RATIO


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.background = Background(allow_stretch=True, size_hint=(None, None), source='background.png')
        self.ground = Background(allow_stretch=True, size_hint=(None, None), source='groundGrass.png')
        self.sky = Background(allow_stretch=True, size_hint=(None, None), source='skyGrass.png',top = WH)
        self.obstacles = ObstacleGroup()
        self.player = Player()


        self.add_widget(self.background)
        self.add_widget(self.obstacles)
        self.add_widget(self.ground)
        self.add_widget(self.sky)
        self.add_widget(self.player)


        Clock.schedule_interval(self.update, 1.0 / 60.0)

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


    def check_collide(self):
        for ground in self.ground.children:
            if self.player.collide_widget(ground):
                if self.player.check_pixel_collison_with_ground(ground):
                    return  True
        for sky in self.sky.children:
            if self.player.collide_widget(sky):
                if self.player.check_pixel_collison_with_ground(sky):
                    return True
        for obstacle in self.obstacles.children:
            if self.player.collide_widget(obstacle):
                if self.player.check_pixel_collison(obstacle):
                    return True




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
