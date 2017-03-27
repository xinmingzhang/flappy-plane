from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager,Screen


class Background(Widget):
    def __init__(self,source):
        super(Background, self).__init__()
        self.o_sprite = Image(source = source,size_hint = (None,None))
        size = self.o_sprite.texture_size
        self.o_sprite.size = size
        self.d_sprite = Image(source = source,size_hint = (None,None))
        size = self.d_sprite.texture_size
        self.d_sprite.size = size
        self.d_sprite.x = self.o_sprite.width
        self.add_widget(self.o_sprite)
        self.add_widget(self.d_sprite)

    def update(self):
        self.o_sprite.x -= 1
        self.d_sprite.x -= 1
        if self.o_sprite.right <= 0:
            self.o_sprite.x = 0
            self.d_sprite.x = self.o_sprite.width

class Player(Image):
    def __init__(self,source,**kwargs):
        super(Player, self).__init__(**kwargs)
        self.source = source
        size = self.texture_size
        self.size = size
        self.velocity = 0
        self.gravity = -0.2

    def update(self):
        self.velocity += self.gravity
        self.velocity = max(self.velocity, - 10)
        self.y += self.velocity

    def on_touch_down(self, touch):
        self.velocity = 4



class GameScreen(Screen):
    def __init__(self,**kwargs):
        super(GameScreen,self).__init__(**kwargs)
        self.background = Background('background.png')
        self.ground = Background('groundGrass.png')
        self.player = Player('planeBlue1.png')
        self.add_widget(self.background)
        self.add_widget(self.ground)
        self.add_widget(self.player)
        Clock.schedule_interval(self.update, 1.0 / 60.0)


    def on_touch_down(self, touch):
        self.player.on_touch_down(touch)

    def on_touch_up(self, touch):
        self.player.on_touch_up(touch)

    def update(self,dt):
        self.background.update()
        self.ground.update()
        self.player.update()




class TitleScreen(Screen):
    pass


class EndScreen(Screen):
    pass

sm = ScreenManager()
sm.add_widget(TitleScreen(name = 'TITLE'))
sm.add_widget(GameScreen(name = 'GAME'))
sm.add_widget(EndScreen(name = 'END'))
sm.current = 'GAME'

class FlappyPlaneApp(App):
    def build(self):
        return sm

if __name__=='__main__':
    FlappyPlaneApp().run()