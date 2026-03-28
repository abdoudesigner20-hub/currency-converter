import requests
from threading import Thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, StencilPush, StencilUse, StencilUnUse, StencilPop, Rectangle
from kivy.clock import Clock, mainthread
from datetime import datetime
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.core.audio import SoundLoader
from kivy.uix.modalview import ModalView
import os
import json
import webbrowser
import random

Window.clearcolor = (0, 0, 0, 1)

# ── إعلانات AdMob بدون KivMob ──────────────────
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    AdView         = autoclass('com.google.android.gms.ads.AdView')
    AdRequest      = autoclass('com.google.android.gms.ads.AdRequest')
    AdSize         = autoclass('com.google.android.gms.ads.AdSize')
    MobileAds      = autoclass('com.google.android.gms.ads.MobileAds')
    InterstitialAd = autoclass('com.google.android.gms.ads.interstitial.InterstitialAd')
    AdLoadCallback = autoclass('com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback')
    ADMOB_AVAILABLE = True
except Exception:
    ADMOB_AVAILABLE = False

BANNER_ID       = "ca-app-pub-3896006690470878/6968965776"
INTERSTITIAL_ID = "ca-app-pub-3896006690470878/7380029313"
APP_ID          = "ca-app-pub-3896006690470878~2043942153"

# ───────────────────────────────────────────────

class RoundedImage(Image):
    def __init__(self, radius=40, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.allow_stretch = True
        self.keep_ratio = False
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            StencilPush()
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            StencilUse()
        self.canvas.after.clear()
        with self.canvas.after:
            StencilUnUse()
            StencilPop()

class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.rect_color = Color(1, 0.5, 0, 0)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[40])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class RoundBox(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [30, 20]
        self.spacing = 15
        self.background_color = (0.1, 0.1, 0.1, 1)
        with self.canvas.before:
            self.canvas_color = Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20,])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class SettingsPopup(ModalView):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.size_hint = (0.5, 0.4)
        self.pos_hint = {'right': 1, 'top': 1}
        self.background = ""

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        layout = BoxLayout(orientation='vertical', padding=[10, 35], spacing=0)
        header = BoxLayout(size_hint_y=None, height=50)
        header.add_widget(BoxLayout(size_hint_x=0.2))
        header.add_widget(Label(text="Settings", color=(0,0,0,1),
                               font_size='14sp', bold=True, halign='center', size_hint_x=0.6))
        exit_btn = ImageButton(source='exit.png', size_hint_x=0.2, allow_stretch=True, keep_ratio=True)
        exit_btn.bind(on_release=self.dismiss)
        header.add_widget(exit_btn)
        layout.add_widget(header)

        separator = BoxLayout(size_hint_y=None, height=15)
        with separator.canvas:
            Color(0.8, 0.8, 0.8, 1)
            self.line = Rectangle(pos=(self.x, self.y), size=(self.width, 2))
        separator.bind(pos=self.update_line, size=self.update_line)
        layout.add_widget(separator)

        items = [
            ("Report an error", self.open_mail),
            ("Suggest a new feature", self.open_mail),
            ("Contact us via email", self.open_mail)
        ]

        for text, func in items:
            btn = Button(
                text=text, color=(0, 0, 0, 1), background_normal="",
                background_color=(1, 1, 1, 1), background_down="",
                halign='left', padding_x=10, font_size='14sp'
            )
            btn.bind(on_press=lambda instance: setattr(instance, 'background_color', (0.8, 0.8, 0.8, 1)))
            btn.bind(on_release=lambda instance: setattr(instance, 'background_color', (1, 1, 1, 1)))
            if func: btn.bind(on_release=func)
            btn.text_size = (Window.width * 0.45, None)
            layout.add_widget(btn)

        sound_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 0])
        sound_label = Label(text="Sound", color=(0, 0, 0, 1), font_size='14sp', halign='center', size_hint_x=0.5)
        initial_source = 'btn1.png' if self.main_app.sound_enabled else 'btn2.png'
        self.sound_toggle_btn = ImageButton(source=initial_source, size_hint_x=0.3, allow_stretch=True, keep_ratio=True)
        self.sound_toggle_btn.bind(on_release=self.toggle_sound)
        sound_layout.add_widget(sound_label)
        sound_layout.add_widget(self.sound_toggle_btn)
        layout.add_widget(sound_layout)
        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_line(self, instance, value):
        self.line.pos = (instance.x, instance.y + 5)
        self.line.size = (instance.width, 1)

    def toggle_sound(self, instance):
        self.main_app.sound_enabled = not self.main_app.sound_enabled
        instance.source = 'btn1.png' if self.main_app.sound_enabled else 'btn2.png'

    def open_mail(self, instance):
        webbrowser.open("mailto:abdoudesigner20@gmail.com")

class EnhancedBankUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=[25, 40, 25, 20], **kwargs)

        self.sound_numbers = SoundLoader.load('beep-29.mp3')
        self.sound_actions = SoundLoader.load('beep-22.mp3')
        self.sound_enabled = True

        self.rates_file = "rates.json"
        self.old_rates_file = "old_rates.json"

        self.rates = {
            "DZA": 1.0, "EUR": 0.0068, "USD": 0.0074, "GBP": 0.0058, "TRY": 0.24,
            "SAR": 0.027, "TND": 0.023, "KWD": 0.0022, "EGP": 0.35, "JPY": 1.10,
            "BTC": 0.0000001, "CNY": 0.053, "AED": 0.027, "RUB": 0.68, "MAD": 0.074,
            "CAD": 0.010, "CHF": 0.0065, "MXN": 0.12, "INR": 0.61, "AUD": 0.011,
            "KRW": 9.8, 'BRL': 0.04, 'ARS': 10.56
        }
        self.old_rates = {k: v * random.choice([0.99, 1.01]) for k, v in self.rates.items()}

        self.selected_currency = "DZA"
        self.current_value = "1"
        self.rows = {}

        title_box = BoxLayout(size_hint_y=0.091, height=190, orientation='horizontal', padding=[0, 1])
        title_box.add_widget(Label(text="CURRENCY CONVERTER PRO", color=(1, 1, 1, 1),
                                  font_size='16sp', bold=True, halign='left', size_hint_x=0.44))
        settings_btn = ImageButton(source='paramètres.png', size_hint_x=0.1, allow_stretch=True, keep_ratio=True)
        settings_btn.bind(on_release=self.show_settings)
        title_box.add_widget(settings_btn)
        self.add_widget(title_box)

        self.time_label = Label(text="", color=(0, 1, 0, 1), font_size='12sp', size_hint_y=0.024, size_hint_x=0.48, height=40)
        self.add_widget(self.time_label)
        Clock.schedule_interval(self.update_time, 1)

        self.scroll = ScrollView(size_hint=(1, 0.55), bar_width=4, bar_pos_y='left')
        self.list_layout = GridLayout(cols=1, spacing=7, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        currencies = [
            ("DZA", "dza.png"), ("EUR", "eur.png"), ("USD", "usd.png"), ("GBP", "gbp.png"),
            ("TRY", "try.png"), ("SAR", "ksa.png"), ("TND", "tun.png"), ("KWD", "kwt.png"),
            ("EGP", "egy.png"), ("JPY", "jpy.png"), ("BTC", "btc.jpg"), ("CNY", "chn.png"),
            ("AED", "uae.png"), ("RUB", "rus.png"), ("MAD", "mar.png"), ("CAD", "can.png"),
            ("CHF", "che.png"), ("MXN", "mex.png"), ("INR", "ind.png"), ("AUD", "aud.png"),
            ("KRW", "kor.png"), ('BRL', 'brl.jpg'), ('ARS', 'ars.jpg')
        ]

        for code, flag in currencies:
            row = RoundBox(size_hint_y=None, height=180)
            row.on_release = lambda c=code: self.select_currency(c)
            flag_container = BoxLayout(size_hint_x=None, width=180, padding=[0, 25])
            flag_img = RoundedImage(source=flag if os.path.exists(flag) else "default_flag.png", radius=25)
            flag_container.add_widget(flag_img)
            code_lbl = Label(text=code, size_hint_x=0.3, font_size='18sp', bold=True, halign='left')
            arrow_img = Image(source='arrow1.png', size_hint_x=0.2, width=50, opacity=0)
            val_lbl = Label(text="1.00", halign='right', font_size='20sp')
            val_lbl.bind(size=val_lbl.setter('text_size'))
            row.add_widget(flag_container)
            row.add_widget(code_lbl)
            row.add_widget(arrow_img)
            row.add_widget(val_lbl)
            self.list_layout.add_widget(row)
            self.rows[code] = {"row": row, "label": val_lbl, "arrow": arrow_img}

        self.scroll.add_widget(self.list_layout)
        self.add_widget(self.scroll)

        num_pad_container = BoxLayout(orientation='vertical', size_hint_y=0.38, padding=[20, 5, 20, 5], spacing=8)
        grid_9 = GridLayout(cols=3, spacing=10, size_hint_y=0.75)
        for i in range(1, 10): grid_9.add_widget(self.create_key(str(i)))
        num_pad_container.add_widget(grid_9)

        bottom_row = GridLayout(cols=3, spacing=10, size_hint_y=0.25)
        left_half = BoxLayout(orientation='horizontal', spacing=8)
        back_btn = ImageButton(source='back.png')
        back_btn.rect_color.a = 1
        back_btn.bind(on_release=lambda x: self.on_key_press(type('obj', (object,), {'text': '<-'})()))
        left_half.add_widget(back_btn)
        left_half.add_widget(self.create_key('.'))
        bottom_row.add_widget(left_half)
        bottom_row.add_widget(self.create_key('0'))
        bottom_row.add_widget(self.create_key('C', color=(0.8, 0.2, 0.2, 1)))
        num_pad_container.add_widget(bottom_row)
        self.add_widget(num_pad_container)

        self.load_local_rates()
        Thread(target=self.update_rates_from_internet, daemon=True).start()
        Clock.schedule_interval(lambda dt: Thread(target=self.update_rates_from_internet, daemon=True).start(), 60)
        self.select_currency("DZA")

    def show_settings(self, instance):
        try:
            App.get_running_app().show_full_ad()
        except:
            pass
        SettingsPopup(main_app=self).open()

    def create_key(self, text, color=(0.15, 0.15, 0.15, 1)):
        btn = Button(text=text, background_color=(0,0,0,0), font_size='22sp', bold=True)
        with btn.canvas.before:
            Color(*color)
            btn.rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[63])
        btn.bind(pos=self.update_btn_rect, size=self.update_btn_rect)
        btn.bind(on_release=self.on_key_press)
        return btn

    def update_btn_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def update_time(self, *args):
        self.time_label.text = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")

    def load_local_rates(self):
        if os.path.exists(self.rates_file):
            try:
                with open(self.rates_file, 'r') as f:
                    self.rates.update(json.load(f))
            except: pass
        if os.path.exists(self.old_rates_file):
            try:
                with open(self.old_rates_file, 'r') as f:
                    self.old_rates.update(json.load(f))
            except: pass
        if self.rates == self.old_rates:
            self.old_rates = {k: v * 0.999 for k, v in self.rates.items()}
        self.apply_arrow_logic()

    def apply_arrow_logic(self):
        for code, data in self.rows.items():
            arrow = data["arrow"]
            if code == self.selected_currency:
                arrow.opacity = 0
                continue
            arrow.opacity = 1
            current = self.rates.get(code, 0)
            old = self.old_rates.get(code, 0)
            if current >= old:
                arrow.source = 'arrow1.png'
            else:
                arrow.source = 'arrow2.png'

    @mainthread
    def _apply_new_rates(self, new_rates, old_rates_copy):
        self.old_rates = old_rates_copy
        self.rates.update(new_rates)
        try:
            with open(self.old_rates_file, 'w') as f:
                json.dump(self.old_rates, f)
            with open(self.rates_file, 'w') as f:
                json.dump(self.rates, f)
        except: pass
        self.apply_arrow_logic()
        self.update_values()

    def update_rates_from_internet(self):
        try:
            url = "https://open.er-api.com/v6/latest/DZD"
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get("result") == "success":
                old_rates_copy = self.rates.copy()
                live_rates = data["rates"]
                mapping = {
                    "DZA": "DZD", "EUR": "EUR", "USD": "USD", "GBP": "GBP", "TRY": "TRY",
                    "SAR": "SAR", "TND": "TND", "KWD": "KWD", "EGP": "EGP", "JPY": "JPY",
                    "CNY": "CNY", "AED": "AED", "RUB": "RUB", "MAD": "MAD", "CAD": "CAD",
                    "CHF": "CHF", "MXN": "MXN", "INR": "INR", "AUD": "AUD", "KRW": "KRW",
                    'BRL': 'BRL', 'ARS': 'ARS'
                }
                new_rates = {}
                for app_code, api_code in mapping.items():
                    if api_code in live_rates:
                        new_rates[app_code] = live_rates[api_code]
                try:
                    btc_r = requests.get("https://api.coinbase.com/v2/prices/BTC-DZD/spot", timeout=3).json()
                    new_rates["BTC"] = 1 / float(btc_r["data"]["amount"])
                except: pass
                self._apply_new_rates(new_rates, old_rates_copy)
        except:
            pass

    def select_currency(self, code):
        self.selected_currency = code
        for c, data in self.rows.items():
            data["row"].canvas_color.rgba = (0.1, 0.5, 0.8, 0.3) if c == code else (0.1, 0.1, 0.1, 1)
        self.apply_arrow_logic()
        self.update_values()

    def on_key_press(self, instance):
        key = instance.text
        if key == 'C': self.current_value = "0"
        elif key == '<-':
            self.current_value = self.current_value[:-1]
            if not self.current_value: self.current_value = "0"
        elif key == '.':
            if '.' not in self.current_value: self.current_value += "."
        else:
            if self.current_value == "0": self.current_value = key
            else: self.current_value += key
        if self.sound_enabled:
            if self.sound_numbers and key not in ['C', '<-']: self.sound_numbers.play()
            elif self.sound_actions: self.sound_actions.play()
        self.update_values()

    def update_values(self):
        try: val = float(self.current_value)
        except: val = 0
        base_in_dzd = val / self.rates.get(self.selected_currency, 1)
        for code, data in self.rows.items():
            result = base_in_dzd * self.rates.get(code, 1)
            data["label"].text = f"{result:,.2f}".replace(",", " ")


class BankApp(App):
    def build(self):
        self._interstitial = None
        if ADMOB_AVAILABLE:
            try:
                activity = PythonActivity.mActivity
                MobileAds.initialize(activity)
                # بانر
                self._banner = AdView(activity)
                self._banner.setAdSize(AdSize.BANNER)
                self._banner.setAdUnitId(BANNER_ID)
                req = AdRequest.Builder().build()
                self._banner.loadAd(req)
                # إضافة البانر للشاشة
                activity.runOnUiThread(lambda: self._add_banner(activity))
                # إعلان كامل
                self._load_interstitial()
            except Exception as e:
                print(f"AdMob init error: {e}")
        return EnhancedBankUI()

    def _add_banner(self, activity):
        try:
            layout = activity.getWindow().getDecorView()
            layout.addView(self._banner)
        except: pass

    def _load_interstitial(self):
        try:
            activity = PythonActivity.mActivity
            req = AdRequest.Builder().build()
            InterstitialAd.load(activity, INTERSTITIAL_ID, req, self._interstitial_callback())
        except: pass

    def _interstitial_callback(self):
        class Callback(AdLoadCallback):
            def onAdLoaded(self_, ad):
                self._interstitial = ad
            def onAdFailedToLoad(self_, error):
                self._interstitial = None
        return Callback()

    def show_full_ad(self):
        try:
            if self._interstitial and ADMOB_AVAILABLE:
                activity = PythonActivity.mActivity
                self._interstitial.show(activity)
                self._interstitial = None
                Clock.schedule_once(lambda dt: self._load_interstitial(), 1)
        except: pass

    def on_resume(self):
        try:
            if ADMOB_AVAILABLE and hasattr(self, '_banner'):
                self._banner.resume()
        except: pass

    def on_pause(self):
        try:
            if ADMOB_AVAILABLE and hasattr(self, '_banner'):
                self._banner.pause()
        except: pass
        return True


if __name__ == "__main__":
    BankApp().run()
        
