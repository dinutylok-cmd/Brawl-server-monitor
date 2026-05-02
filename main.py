import random
import subprocess
import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty

Window.clearcolor = get_color_from_hex('#1A75D2')

class MassiveButton(ButtonBehavior, FloatLayout):
    press_scale = NumericProperty(1.0)
    btn_color = ListProperty([0.95, 0.95, 0.95, 1]) 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_active = False
        self.size_hint = (None, None)
        self.size = (280, 280)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.55}
        self.bind(pos=self.draw, size=self.draw, press_scale=self.draw, btn_color=self.draw)

    def draw(self, *args):
        self.canvas.before.clear()
        w, h = self.width * self.press_scale, self.height * self.press_scale
        offset_y = 10 * (1.0 - self.press_scale)
        cx, cy = self.center_x, self.center_y - offset_y
        with self.canvas.before:
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(cx - w/2 + 5, cy - h/2 - 7), size=(w, h))
            Color(*self.btn_color)
            Ellipse(pos=(cx - w/2, cy - h/2), size=(w, h))
            Color(1, 1, 1, 1) if self.is_active else Color(rgba=get_color_from_hex('#1A75D2'))
            Line(circle=(cx, cy, 45 * self.press_scale, 30, 330), width=8)
            Line(points=[cx, cy + 10*self.press_scale, cx, cy + 50*self.press_scale], width=8)

    def on_press(self):
        Animation(press_scale=0.9, btn_color=get_color_from_hex('#002D5A'), duration=0.1).start(self)

    def on_release(self):
        self.is_active = not self.is_active
        t_color = get_color_from_hex('#003366') if self.is_active else [0.95, 0.95, 0.95, 1]
        t_scale = 0.94 if self.is_active else 1.0
        Animation(press_scale=t_scale, btn_color=t_color, duration=0.3, t='out_back').start(self)
        App.get_running_app().toggle_monitoring(self.is_active)

class BrawlMonitorApp(App):
    def build(self):
        self.root = FloatLayout()
        # (Тут можно добавить TechnicalBackground и RadarWave из прошлых версий)
        
        self.btn = MassiveButton()
        self.root.add_widget(self.btn)
        
        self.card = BoxLayout(orientation='vertical', padding=[20, 15], size_hint=(0.9, None), height=180)
        self.card.pos_hint = {'center_x': 0.5, 'y': 0.05}
        with self.card.canvas.before:
            Color(1, 1, 1, 0.95)
            self.rect = RoundedRectangle(pos=self.card.pos, size=self.card.size, radius=[40,])
        
        self.status = Label(text="IDLE", color=(0.3, 0.3, 0.3, 1), font_size='20sp', bold=True)
        self.info_main = Label(text="SCANNING OFF", color=(0,0,0,1), font_size='18sp')
        self.card.add_widget(self.status)
        self.card.add_widget(self.info_main)
        self.root.add_widget(self.card)
        
        return self.root

    def toggle_monitoring(self, active):
        if active:
            self.status.text = "SCANNING NETWORK..."
            self.status.color = get_color_from_hex('#007BFF')
            Clock.schedule_interval(self.find_brawl_ip, 2)
        else:
            Clock.unschedule(self.find_brawl_ip)
            self.status.text = "IDLE"
            self.status.color = (0.3, 0.3, 0.3, 1)
            self.info_main.text = "SCANNING OFF"

    def find_brawl_ip(self, dt):
        """Пытается найти IP игрового сервера через netstat"""
        try:
            # Команда для поиска активных UDP соединений (наиболее часто для игр)
            # В Android через Pydroid может потребоваться упрощенный вызов
            output = subprocess.check_output(['netstat', '-an']).decode('utf-8')
            lines = output.split('\n')
            
            found_ip = None
            for line in lines:
                # Ищем стандартный порт Brawl Stars (9339) или признаки активного UDP
                if ":9339" in line or "ESTABLISHED" in line:
                    parts = line.split()
                    if len(parts) > 2:
                        found_ip = parts[2].split(':')[0]
                        break
            
            if found_ip and found_ip != "0.0.0.0" and found_ip != "127.0.0.1":
                self.info_main.text = f"SERVER IP: {found_ip}"
                self.status.text = "TARGET FOUND"
            else:
                self.info_main.text = "WAITING FOR GAME..."
        except Exception as e:
            self.info_main.text = "SEARCHING..." # На некоторых Android доступ к netstat ограничен

if __name__ == '__main__':
    BrawlMonitorApp().run()
