[app]
title = IPTV MAC Scanner PRO
package.name = iptvscanner
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg

version = 1.0

requirements = python3,kivy,kivymd,requests

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE ,READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

log_level = 2

[buildozer]
warn_on_root = 1
