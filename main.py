from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.toolbar import MDTopAppBar

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import threading
import requests
import time


KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex


<StatCard>:
    size_hint_y: None
    height: dp(90)
    orientation: "vertical"
    padding: dp(10)
    radius: [14]
    elevation: 2
    md_bg_color: app.theme_cls.bg_dark

    MDLabel:
        text: root.value
        halign: "center"
        bold: True
        font_style: "H5"

    MDLabel:
        text: root.title
        halign: "center"
        font_style: "Caption"


<DashboardScreen>:
    name: "dashboard"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "IPTV MAC Scanner PRO"
            md_bg_color: app.theme_cls.primary_color

        MDScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(12)
                padding: dp(12)
                size_hint_y: None
                height: self.minimum_height

                MDBoxLayout:
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(90)

                    StatCard:
                        title: "TOTAL"
                        value: root.total_requests

                    StatCard:
                        title: "HITS"
                        value: root.success_hits

                    StatCard:
                        title: "ERRORS"
                        value: root.errors

                MDCard:
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(12)
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [14]
                    elevation: 2

                    MDLabel:
                        text: "TARGET CONFIGURATION"
                        size_hint_y: None
                        height: dp(25)

                    MDTextField:
                        id: target_url
                        hint_text: "Portal URL"
                        size_hint_y: None
                        height: dp(50)

                    MDTextField:
                        id: mac_prefix
                        hint_text: "MAC Prefix"
                        text: "00:1A:79"
                        size_hint_y: None
                        height: dp(50)

                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)

                        MDTextField:
                            id: hex_start
                            hint_text: "HEX START"

                        MDTextField:
                            id: hex_end
                            hint_text: "HEX END"

                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)

                        MDTextField:
                            id: threads
                            hint_text: "THREADS"

                        MDTextField:
                            id: timeout
                            hint_text: "TIMEOUT"

                MDCard:
                    padding: dp(12)
                    size_hint_y: None
                    height: dp(90)

                    MDLabel:
                        text: root.status

                    MDProgressBar:
                        value: root.progress

                    MDLabel:
                        text: root.progress_text
                        halign: "right"

                MDBoxLayout:
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(52)

                    MDRaisedButton:
                        text: "START"
                        on_release: root.start_scan()

                    MDRaisedButton:
                        text: "STOP"
                        on_release: root.stop_scan()

                    MDRaisedButton:
                        text: "CLEAR"
                        on_release: root.clear_logs()

                MDCard:
                    orientation: "vertical"
                    radius: [14]
                    padding: dp(8)
                    md_bg_color: get_color_from_hex("#0D1117")
                    size_hint_y: None
                    height: dp(320)

                    MDLabel:
                        text: "LIVE LOG"
                        size_hint_y: None
                        height: dp(25)

                    MDScrollView:
                        MDList:
                            id: logs_list
                            size_hint_y: None
                            height: self.minimum_height


<SettingsScreen>:
    name: "settings"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Hits Dashboard"

        MDLabel:
            text: "HITS PANEL"
            halign: "center"
"""


class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("0")


class DashboardScreen(MDScreen):

    total_requests = StringProperty("0")
    success_hits = StringProperty("0")
    errors = StringProperty("0")

    progress = NumericProperty(0)
    progress_text = StringProperty("0%")
    status = StringProperty("● IDLE")

    running = BooleanProperty(False)

    total = 0
    hits = 0
    errors_count = 0

    def start_scan(self):
        if self.running:
            return

        self.running = True
        self.status = "▶ RUNNING"
        self.ids.logs_list.clear_widgets()

        try:
            self.start = int(self.ids.hex_start.text, 16)
            self.end = int(self.ids.hex_end.text, 16)
        except:
            self.start = 0
            self.end = 1000

        self.session = requests.Session()

        threading.Thread(target=self.engine, daemon=True).start()

    def stop_scan(self):
        self.running = False
        self.status = "■ STOPPED"

    def engine(self):

        for i in range(self.start, self.end):

            if not self.running:
                break

            mac = self.build_mac(i)
            url = self.ids.target_url.text

            try:
                r = self.session.get(url, timeout=5)

                if r.status_code == 200:
                    level = "HIT"
                    self.hits += 1
                else:
                    level = "MISS"
                    self.errors_count += 1

            except:
                level = "ERROR"
                self.errors_count += 1

            self.total += 1

            Clock.schedule_once(lambda dt, m=mac, l=level: self.add_log(m, l))

            self.total_requests = str(self.total)
            self.success_hits = str(self.hits)
            self.errors = str(self.errors_count)

            self.progress = int((self.total / max(self.end - self.start, 1)) * 100)
            self.progress_text = f"{self.progress}%"

            time.sleep(0.15)

    def build_mac(self, value):
        suffix = f"{value:06X}"
        return ":".join([self.ids.mac_prefix.text] + [suffix[i:i+2] for i in range(0, 6, 2)])

    def add_log(self, mac, level):
        self.ids.logs_list.add_widget(
            OneLineListItem(text=f"{level} | {mac}")
        )

    def clear_logs(self):
        self.ids.logs_list.clear_widgets()


class SettingsScreen(MDScreen):
    pass


class MainApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"

        Builder.load_string(KV)

        nav = MDBottomNavigation()

        dash = DashboardScreen()
        settings = SettingsScreen()

        tab1 = MDBottomNavigationItem(name="scanner", text="Scanner", icon="radar")
        tab1.add_widget(dash)

        tab2 = MDBottomNavigationItem(name="history", text="History", icon="history")
        tab2.add_widget(settings)

        nav.add_widget(tab1)
        nav.add_widget(tab2)

        return nav


MainApp().run()